import dimod
import hybrid
import dwavebinarycsp


#function to solve for the minimum energy posibility:
def SolveExtreme(bqm):
  # Define the workflow
  iteration = hybrid.RacingBranches(
      hybrid.InterruptableTabuSampler(),
      hybrid.EnergyImpactDecomposer(size=2)
      | hybrid.QPUSubproblemAutoEmbeddingSampler()
      | hybrid.SplatComposer()
  ) | hybrid.ArgMin()
  workflow = hybrid.LoopUntilNoImprovement(iteration, convergence=3)

  # Solve the problem
  init_state = hybrid.State.from_problem(bqm)
  final_state = workflow.run(init_state).result()

  # Print results
  result = ("Solution: sample={.samples.first}".format(final_state))
  resultSplit = result.split("{") #remove extra info
  resultSplit = resultSplit[1].split("}")
  result = resultSplit[0]
  results = result.split(", ") #separate the vars

  #now extract the numerical results:
  refLen = 0
  for i in range(len(results)):
    if (not("*" in results[i])):
      refLen += 1 #make sure that refined is the right length
  refined = [0] * refLen
  for i in range(len(results)):
    if (not("*" in results[i])): #if this is a useful result that only contains one term
      num = results[i].split(": ")
      trash, position = num[0].split("v")
      position = position.replace("'", "")
      position = int(position) 
      refined[position] = (float(num[1]))
  return(refined)


#function to solve BQM formatted from a CSP
def SolveCSP(bqm):
  # Define the workflow
  iteration = hybrid.RacingBranches(
      hybrid.InterruptableTabuSampler(),
      hybrid.EnergyImpactDecomposer(size=2)
      | hybrid.QPUSubproblemAutoEmbeddingSampler()
      | hybrid.SplatComposer()
  ) | hybrid.ArgMin()
  workflow = hybrid.LoopUntilNoImprovement(iteration, convergence=3)

  # Solve the problem
  init_state = hybrid.State.from_problem(bqm)
  final_state = workflow.run(init_state).result()

  # Print results
  result = ("Solution: sample={.samples.first}".format(final_state))
  result = result.replace("Solution: sample=Sample(sample={", "")
  result, trash = result.split("}")
  results = result.split(", ")

  #now extract the numerical results:
  for i in range(len(results)):
    trash, term = results[i].split(": ")
    results[i] = float(term)
  return(results)
  

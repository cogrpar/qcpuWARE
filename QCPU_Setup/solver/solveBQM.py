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
  for i in range(len(results)):
    results[i] = float(results[i].replace((str(i+1) + ": "), ""))
  return(results)
  

#function to set the values of the bqm matrix for the dwave system to minimize/maximize
def SetMatrix(matrix, numOfVars):
  equal = []
  dif = []
  for i in range(numOfVars):
    for j in range(numOfVars):
      if (i == j):
        if (i < numOfVars-1): #if we are not doing the last entry
          equal.append(str(i+1) + ": " + str(matrix[i][j]) + ", ")
        else:
          equal.append(str(i+1) + ": " + str(matrix[i][j]))
      if (i < j):
        dif.append("(" + str(i+1) + ", " + str(j+1) + "): " + str(matrix[i][j]) + ", ")
  #now combine all of these into a single executable function:
  exe = "bqm = dimod.BinaryQuadraticModel({"
  for i in equal:
    exe += i
  exe += "}, {"
  for i in dif:
    exe += i
  exe = exe[:-2:]
  exe += "}, 0.0, dimod.BINARY)"
  
  return(exe)

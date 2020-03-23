#import nececary tools
from baseConverter import *
from solveBQM import *
from solveMatrix import *
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from time import sleep

#function to define the variables given the number of vars
def DefVars(numOfVars):
  vars = []
  for i in range(numOfVars):
    vars.append("v" + str(i))
  return vars

def ReturnResults(results): #function to write results to result webserver file
  res = open("/var/www/html/results.txt","w+")
  res.write(results)
  res.close()
  
def GetInput(): #function to take the input from the server file 
  inp = open("/var/www/html/storage.txt","r+")
  strIn = inp.read()
  inp.close()
  inSplit = strIn.split("\n")
  
  #initiate the return variables
  data = []
  mode = ""
  
  #read the first line in the input to determine the mode specified by the user
  if (inSplit[0] == "funcExtreme"): #if the user specified function extreme solver mode
    mode = "funcExtreme"
    #the first term in the file should be the domain array, so we will extract that
    strDom = inSplit[1].split(", ") #split along each term of the array
    strDom[0] = strDom[0].replace("[", "")
    strDom[(len(strDom)-1)] = strDom[(len(strDom)-1)].replace("]", "")
    dom = []

    for i in strDom:
      dom.append(float(i))
    print(dom)  
    #the second term in the file should be the equation
    eq = parse_expr(inSplit[2], evaluate=False)

    #the third term in the file should be the min/max boolean
    minMaxBool = False
    minMax = inSplit[3]
    if ("True" in minMax):
      minMaxBool = True

    #clear the input file
    inp = open("/var/www/html/storage.txt","w+")
    inp.write("")
    inp.close()
    
    data = [dom, eq, minMaxBool]
  
  elif (inSplit[0] == "BCSP"): #if the mode is binary constraint satisfaction problem solver
    mode = "BCSP"
    constraints = inSplit[1]
    numOfVars = inSplit[2]
    data = [constraints.split(";"), int(numOfVars)]
    
  return (mode, data)

#function that checks to see if the storage file is empty
def EmptyInput():
  inp = open("/var/www/html/storage.txt","r+")
  strIn = inp.read()
  inp.close()
  
  if("\n" in strIn):
    return (False)
  else:
    return (True)

####################  code  ####################
while True: #run repeatedly in the background
  #check to see if there is any input on the server
  if (not EmptyInput()): 
    mode, data = GetInput()
    
    #check to see what mode was set
    if (mode == "funcExtreme"):
      domain, eq, minMax = data
      numOfVars = len(domain)

      #generate array containing variables:
      var = []
      for i in range(numOfVars):
        var.append("v" + str(i))

      for i in var: #this defines each variable using sympy's symbols function
        vars()[i] = symbols(i)

      EQ, numOfVars, places = ToBin(domain, eq, var) #convert function to binary and get it as a string, along with a new variable count and an array used to convert back to decimal

      #now solve for the matrix:
      inVars = DefVars(numOfVars)
      p = SolvMatrix(EQ, inVars, minMax) #set to true to maximise result
      exec(p) #define the polynomial that was returned
      bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)  # QUBO
      dimod.make_quadratic(poly, 10.0, bqm = bqm) #define the BQM

      #send to dwave to solve for max/min:
      vals = SolveExtreme(bqm)

      #convert the results back to decimal and send them to the webserver:
      results = ToDec(places, vals)
      result = "["
      result += ', '.join(str(i) for i in results) + "]"
      ReturnResults(result)
      
    elif (mode == "BCSP"):
      constraints, numOfVars = data
      #solve the CPS given the inputs
      #make all of the constraints into a big boolean statement
      boolean = "("
      for i in constraints:
          boolean += "(" + i + ") and "
      boolean = boolean[:-5:]
      boolean += ")"
      
      vars = ""
      for i in range(numOfVars-1):
          vars += "v" + str(i) + ", "
      vars += "v" + str(numOfVars-1)

      exe = '''def const(''' + vars + '''):
        return''' + boolean + '''
      '''

      #reformat vars for csp
      vars = ""
      for i in range(numOfVars-1):
          vars += "'v" + str(i) + "', "
      vars += "'v" + str(numOfVars-1) + "'"

      #execute the function to make it exist
      exec (exe)

      #define the csp 
      csp = dwavebinarycsp.ConstraintSatisfactionProblem(dwavebinarycsp.BINARY)
      add_const = '''csp.add_constraint(const, [''' + vars + '''])'''
      exec(add_const)

      bqm = dwavebinarycsp.stitch(csp)
      
      result = SolveCSP(bqm)

      resultStr = "["
      for i in result:
        resultStr += str(i) + ", "
      resultStr = resultStr[:-2:]
      resultStr += "]"

      ReturnResults(resultStr)
    
  else: #if there is no input, then wait a bit and check again
    sleep(0.3)

#import nececary tools
from baseConverter import *
from solveBQM import *
from solveMatrix import *
from sympy import *
from time import sleep

#function to define the variables given the number of vars
def DefVars(numOfVars):
  vars = []
  for i in range(numOfVars):
    vars.append("v" + str(i))
  return vars

def ReturnResult(results): #function to write results to result webserver file
  res = open("/var/www/html/results.txt","w+")
  res.write(results)
  res.close()
  
def GetInput(): #function to take the input from the server file 
  inp = open("/var/www/html/storage.txt","r+")
  strIn = inp.read()
  inp.close()
  inSplit = strIn.split("\n")
  #the first term in the file should be the domain array, so we will extract that
  strDom = inSplit[0].split(", ") #split along each term of the array
  strDom[0] = strDom.replace("[", "")
  strDom[(len(strDom)-1)] = strDom[(len(strDom)-1)].replace("]", "")
  dom = []
  for i in strDom:
    dom.append(double(i))
    
  #the second term in the file should be the equation
  eq = parse_expr(inSplit[1], evaluate=False)
  
  #the third term in the file should be the min/max boolean
  minMaxBool = False
  minMax = inSplit[2]
  if ("True" in minMax):
    minMaxBool = True
    
  #clear the input file
  inp = open("/var/www/html/storage.txt","w+")
  inp.write("")
  inp.close()
  
  return (dom, eq, minMaxBool)

#function that checks to see if the storage file is empty
def EmptyInput():
  inp = open("/var/www/html/storage.txt","r+")
  strIn = inp.read()
  inp.close()
  
  if("\n" in strIn):
    return (True)
  else:
    return (False)

####################  code  ####################
while True: #run repeatedly in the background
  #check to see if there is any input on the server
  if (not EmptyInput()): 
    domain, eq, minMax = GetInput()
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
    matrix = SolvMatrix(EQ, inVars, nimMax) #set to true to maximise result. Really we would get this boolean from webserver

    #send to dwave to solve for max/min:
    exec(SetMatrix(matrix, numOfVars))
    vals = SolveExtreme(bqm)

    #convert the results back to decimal and send them to the webserver:
    results = ToDec(places, vals)
    #print(results)
    ReturnResults(results)
    
  else: #if there is no input, then wait a bit and check again
    sleep(0.3)

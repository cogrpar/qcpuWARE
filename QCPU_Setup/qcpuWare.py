#import nececary tools
from baseConverter import *
from solveBQM import *
from solveMatrix import *

#function to define the variables given the number of vars
def defVars(numOfVars):
  vars = []
  for i in range(numOfVars):
    vars.append("v" + str(i))
  return vars

#code
domain = [4, 4, 4] #really we would get this array from webserver
numOfVars = len(domain)
var = ["v0", "v1", "v2"] #really we would get this array from webserver

for i in var: #this defines each variable using sympy's symbols function
  vars()[i] = symbols(i)

eq = v1 + v2 + v0 #really we would get this equation from webserver
EQ, numOfVars, places = toBin(domain, eq, var) #convert function to binary and get it as a string, along with a new variable count and an array used to convert back to decimal

#now solve for the matrix:
inVars = defVars(numOfVars)
matrix = solvMatrix(EQ, inVars, False) #set to true to maximise result. Really we would get this boolean from webserver

#send to dwave to solve for max/min:
exec(setMatrix(matrix, numOfVars))
vals = solveExtreme(bqm)

#convert the results back to decimal and send them to the webserver:
results = toDec(places, vals)
print(results)

#import nececary tools
from baseConverter import *
from solveBQM import *
from solveMatrix import *

#function to define the variables given the number of vars
def DefVars(numOfVars):
  vars = []
  for i in range(numOfVars):
    vars.append("v" + str(i))
  return vars

def ReturnResult(results): #function to write results to result webserver file
  res = open("/var/www/html/storage.txt","w+")
  resRead = open("var/www/html/storage.txt","r")
  #check to see if the file is empty
  data = resRead.read()
  res.write(results)
  res.close()
  resRead.close()
  
def GetServerIn(): #this function gets the required info from the server file
  

#code
domain = [4, 4, 4, 4] #really we would get this array from webserver
numOfVars = len(domain)
var = ["v0", "v1", "v2", "v3"] #really we would get this array from webserver

for i in var: #this defines each variable using sympy's symbols function
  vars()[i] = symbols(i)

eq = v1 + v2 - v0 - v3 #really we would get this equation from webserver
EQ, numOfVars, places = ToBin(domain, eq, var) #convert function to binary and get it as a string, along with a new variable count and an array used to convert back to decimal

#now solve for the matrix:
inVars = DefVars(numOfVars)
matrix = SolvMatrix(EQ, inVars, False) #set to true to maximise result. Really we would get this boolean from webserver

#send to dwave to solve for max/min:
exec(SetMatrix(matrix, numOfVars))
vals = SolveExtreme(bqm)

#convert the results back to decimal and send them to the webserver:
results = ToDec(places, vals)
print(results)

from sympy import *

#funtion to convert the input into a binary function:
def toBin(domain, eq, var):
  numOfVars = len(var)
  for i in var:
    vars()[i] = symbols(i) #initiate the symbols variables

  #change variable names to avoid mixups:
  for i in range(numOfVars):
    eq = eq.subs(vars()["v" + str(i)], "v" + str(i)+"temp") #temprarily swap the names of the variables to avoid mixups when substituting

  place = 0
  places = []

  for i in range(numOfVars): #loop over the number of variables
    upper = domain[i] #specify the upper bound of this variable

    power = 0

    while(2**power <= upper):
      power += 1 #find the number of binary place values required for the specified upper bound

    power -= 1
    places.append(power) #store this value in an array to be used later in converting back to decimal

    bina = "(2**-1)*v" + str(place) + " + "

    place += 1

    for j in range(power): #loop over eqch binary place value and specify its magnitude
      bina += "(2**" + str(j) + ")*v" + str(place) + " + "
      place += 1
    
    bina = bina[:-2:]

    eq = eq.subs(("v" + str(i)+"temp"), bina) #substitute the binary vars in for the decimal ones

  #replace fraction with decimal
  strEq = str(eq)
  terms = strEq.split(" + ")
  for i in range(len(terms)):
    if("/" in terms[i]): #for all terms containing "/""
      divisor = float(terms[i].split("/")[1]) #find the divisor
      terms[i] = terms[i][:-(len(terms[i]) - terms[i].find("/")):] #remove everything after "/" (included)
      terms[i] = str(1/divisor) + "*" + terms[i] #multiply by 1/divisor
  strEq = ""
  for i in terms:
    strEq += i + " + "
  
  strEq = strEq[:-2]

  return (strEq, place, places) #return the string of the binary function, the number of binary vars, and the number of binary digits in each base 10 number, used to convert back to decimal

    
#function to convert the binary results into base 10
def toDec(places, values):
  pos = 0 #keep track of the place value that we are on
  outVars = [] #an array to store the output values
  for i in places: #loop over the number of digits in each base ten var
    tot = 0
    i+= 1
    for j in range(i): #loop over the cooresponding binary place vals
      tot = 2**(i-1) * values[pos] #convert to decimal
      pos += 1
    outVars.append(tot) #append the result to the output array
  return(outVars)


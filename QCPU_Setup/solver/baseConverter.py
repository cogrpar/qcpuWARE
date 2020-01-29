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

  print(eq)
  #replace fraction with decimal
  strEq = str(eq)
  termsPos = []
  termsNeg = []
  termsPls = strEq.split(" + ")
  for i in termsPls:
    ii = i.split(" - ") #split along negative as well
    for j in range(len(ii)):
      if(j > 0): #if not the first entry (not positive)
        termsNeg.append(ii[j])
      else:
        termsPos.append(ii[j])
    
  for i in range(len(termsPos)):
    if("/" in termsPos[i]): #for all terms containing "/""
      divisor = float(termsPos[i].split("/")[1]) #find the divisor
      termsPos[i] = termsPos[i][:-(len(termsPos[i]) - termsPos[i].find("/")):] #remove everything after "/" (included)
      termsPos[i] = str(1/divisor) + "*" + termsPos[i] #multiply by 1/divisor
  for i in range(len(termsNeg)):
    if("/" in termsNeg[i]): #for all terms containing "/""
      divisor = float(termsNeg[i].split("/")[1]) #find the divisor
      termsNeg[i] = termsNeg[i][:-(len(termsNeg[i]) - termsNeg[i].find("/")):] #remove everything after "/" (included)
      termsNeg[i] = str(1/divisor) + "*" + termsNeg[i] #multiply by 1/divisor
  strEq = ""
  for i in termsPos:
    strEq += i + " + "
  strEq = strEq[:-3]
  for i in termsNeg:
    strEq += i + " - "
  strEq = strEq[:-3]
  print(strEq)

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


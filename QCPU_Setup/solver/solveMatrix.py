#function to convert input function to bqm (and return the matrix), as accurately as possible
def SolvMatrix(eq, inVars, Max):

  numOfVars = len(inVars)

  poly = """poly = {"""

  positive = []
  negative = []

  splitEq = eq.split("+") #split along the +
  for i in splitEq:
    spl = i.split("-") #split along the -
    for j in range(len(spl)):
      if (j != 0): #skip over the positive term
        if (spl[j] == " "): #if there is a blank term
          pass
        else:
          negative.append(spl[j].replace(" ", ""))
      else: #append the positive term
        if (spl[j] == " "): #if there is a blank term
          pass
        else:
          positive.append(spl[0].replace(" ", "")) 

  #swap the pos and neg if we want to max the function (this corresponds to multiplying the funtion by -1)
  if (Max):
    temp = positive
    positive = negative
    negative = temp


  for i in negative:

    #get rid of all exponents
    mult = i.split("**")
    mult[0] += "*"
    for m in range(len(mult)):
      if(m > 0):
        mm = mult[m].split("*")

        try:
          mult[m] = mm[1]
        except:
          mult[m] = ""
          mult[m-1] = mult[m-1].replace("*", "")
    mul = ""
    for m in mult:
      mul += m

    #now find the number that this term is multiplied by
    fac = 1
    for m in mul.split("*"):
      try:
        fac = float(m)
      except:
        if(fac == 1):
          fac = 1


    contained = []
    for j in inVars:
      if (j in i): #if term i contains var j
        contained.append(j)
    
    if (len(contained) == 1): #if there is only one variable in the term
      #add polynomial to poly string
      poly += """('""" + contained[0] + """',): -""" + str(fac) + """, """ 

    elif (len(contained) > 1): #if there are several vars
      varList = ""
      for n in contained:
        varList += "'" + n + "', "
      varList = varList[:-2:]
      poly += """(""" + varList + """): -""" + str(fac) + """, """

  for i in positive: #now do the same thing but with the positives
  
    #get rid of all exponents
    mult = i.split("**")
    mult[0] += "*"
    for m in range(len(mult)):
      if(m > 0):
        mm = mult[m].split("*")

        try:
          mult[m] = mm[1]
        except:
          mult[m] = ""
          mult[m-1] = mult[m-1].replace("*", "")
    mul = ""
    for m in mult:
      mul += m

    #now find the number that this term is multiplied by
    fac = 1
    for m in mul.split("*"):
      try:
        fac = float(m)
      except:
        if(fac == 1):
          fac = 1

    contained = []
    for j in inVars:
      if (j in i): #if term i contains var j
        contained.append(j)
    
    if (len(contained) == 1): #if there is only one variable in the term
      #add polynomial to poly string
      poly += """('""" + contained[0] + """',): """ + str(fac) + """, """ 

    elif (len(contained) > 1): #if there are several vars
      varList = ""
      for n in contained:
        varList += "'" + n + "', "
      varList = varList[:-2:]
      poly += """(""" + varList + """): """ + str(fac) + """, """

  poly = poly[:-2:] + """}"""

  return poly

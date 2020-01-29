#function to convert input function to bqm (and return the matrix), as accurately as possible
def solvMatrix(eq, inVars, Max):

  numOfVars = len(inVars)

  w, h = numOfVars, numOfVars
  matrix = [[0 for x in range(w)] for y in range(h)]

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
      index = int(contained[0].replace("v", ""))
      matrix[index][index] = -1 * fac

    elif (len(contained) > 1): #if there are several vars
      vars = []
      for m in contained:
        vars.append(int(m.replace("v", "")))
      #loop over the indexes
      count = 0
      for w in vars:
        for h in vars:
          if (h < w):
            if (not (matrix[h][w] == 1 or matrix[h][w] == -1)): #if this entry does not have a value yet:
              count += 1
      for w in vars:
        for h in vars:
          if (h < w):
            if (not (matrix[h][w] == 1 or matrix[h][w] == -1)): #if this entry has no value...
              matrix[h][w] = (-1 * fac)/count

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
      index = int(contained[0].replace("v", ""))
      matrix[index][index] = fac

    elif (len(contained) > 1): #if there are several vars
      vars = []
      for m in contained:
        vars.append(int(m.replace("v", "")))
      #loop over the indexes
      count = 0
      for w in vars:
        for h in vars:
          if (h < w):
            if (not (matrix[h][w] == 1 or matrix[h][w] == -1)): #if this entry does not have a value yet:
              count += 1
      for w in vars:
        for h in vars:
          if (h < w):
            if (not (matrix[h][w] == 1 or matrix[h][w] == -1)): #if this entry has no value...
              matrix[h][w] = fac/count

  print(matrix)
  return matrix

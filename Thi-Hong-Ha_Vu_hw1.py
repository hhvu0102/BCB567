# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 15:06:07 2019

@author: Vu Thi-Hong-Ha
"""
import re
import sys

#Step 0: Taking the input from console
argList = sys.argv

#Step 0.1: Sanity checking for arguments
if int(argList[3]) < 0:
    raise Exception("Bonus score has to be nonnegative!")

#Step 0.2: Declaring the scoring scheme
matchScore = 10
mismatchScore = -15
gapOpen = 40
gapExtension = 2
bonusScore = int(argList[3])


#Step 1: Reading in the files
seq1 = open(argList[1], "r")
for line1 in seq1:
    if line1.startswith('>') and (" " in line1) == False:
        name1 = re.search('>(.*)\n', line1).group(1) #if there is no description
    elif line1.startswith('>') and (" " in line1):
        name1 = re.search('>(.*) ', line1).group(1) #if there is a description
    else:
        A = [" "]
        A.extend(list(line1))
        A1 = line1.rstrip() #remove the \n at the end of the line, if needed
seq1.close()


seq2 = open(argList[2], "r")
for line2 in seq2:
    if line2.startswith('>') and (" " in line2) == False:
        name2 = re.search('>(.*)\n', line2).group(1)
    elif line2.startswith('>') and (" " in line2):
        name2 = re.search('>(.*) ', line2).group(1)
    else:
        B= [" "]
        B.extend(list(line2))
        B1 = line2.rstrip()
seq2.close()


m = len(A1)
n = len(B1)


#Step 2: Constructing the matrices

#Initalizing three matrices
S = [[0 for i in range(n+1)] for j in range(m+1)]
D = [[0 for i in range(n+1)] for j in range(m+1)]
I = [[0 for i in range(n+1)] for j in range(m+1)]

#Calculating the matrices
score = 0
rowFirst = m
colFirst = n
D[m][n] = -(gapOpen + gapExtension)
I[m][n] = -(gapOpen + gapExtension)

for j in range(n-1, -1, -1):
    I[m][j] = -(gapOpen + gapExtension)
    D[m][j] = -(gapOpen + gapExtension)
    
for i in range(m-1, -1, -1):
    S[i][n] = 0;
    D[i][n] = -(gapOpen + gapExtension)
    I[i][n] = -(gapOpen + gapExtension)
    for j in range(n-1, -1, -1):
        D[i][j] = max(D[i+1][j] - gapExtension, S[i+1][j] - gapOpen - gapExtension)
        I[i][j] = max(I[i][j+1] - gapExtension, S[i][j+1] - gapOpen - gapExtension)
        if i != 0 and j != 0:
            if A[i+1] == B[j+1] and A[i] == B[j]:
                S[i][j] = max(0, S[i+1][j+1] + matchScore + bonusScore, D[i][j], I[i][j])
            elif A[i+1] == B[j+1]:
                S[i][j] = max(0, S[i+1][j+1] + matchScore, D[i][j], I[i][j])
            else:
                S[i][j] = max(0, S[i+1][j+1] + mismatchScore, D[i][j], I[i][j])
        else:
            if A[i+1] == B[j+1]:
                S[i][j] = max(0, S[i+1][j+1] + matchScore, D[i][j], I[i][j])
            else:
                S[i][j] = max(0, S[i+1][j+1] + mismatchScore, D[i][j], I[i][j])
                
        if score < S[i][j]:
            score = S[i][j]
            rowFirst = i
            colFirst = j
            
            
#Step 3: Traceback-ing to get alignment
OA = []
i = rowFirst
j = colFirst
mat = "S"
while i <= m and j <= n:
    if mat == "S":
        if i == m or j == n or S[i][j] == 0:
            break
        if S[i][j] == D[i][j]:
            mat = "D"
            continue
        if S[i][j] == I[i][j]:
            mat = "I"
            continue
        OA.append([A[i+1], B[j+1]])
        i = i+1
        j = j+1
        continue
    if mat == "D":
        OA.append([A[i+1], "-"])
        if i == m-1 or D[i][j] == S[i+1][j] - gapOpen - gapExtension:
            mat = "S"
        i = i+1
        continue
    if mat == "I":
        OA.append(["-", B[j+1]])
        if i == n-1 or I[i][j] == S[i][j+1] - gapOpen - gapExtension:
            mat = "S"
        j = j+1
        continue
rowLast = i
colLast = j


#Step 4: Preping outputs and printing
#Getting the aligned sequences, including gaps
alignedA = []
alignedB = []

for k in range(len(OA)):
    alignedA.append(OA[k][0])
    alignedB.append(OA[k][1])


#Counting numbers of matches, mismatches and displaying results
#Keeping track for report
matchNum = 0
mismatchNum = 0
gapNum = 0
conseNum = 0

match = [] #for displaying results
for l in range(len(OA)):
    if alignedA[l] == alignedB[l]:
        matchNum = matchNum + 1
        match.extend("|")
    elif alignedA[l] != alignedB[l] and (alignedA[l] != "-" and alignedB[l] != "-"):
        mismatchNum = mismatchNum + 1
        match.extend(" ")
    else:
        if alignedA[l] == "-":
            gapNum = gapNum + 1
            alignedA[l] = " "
            match.extend("-")
        elif alignedB[l] == "-":
            gapNum = gapNum + 1
            alignedB[l] = " "
            match.extend("-")
for h in range(len(OA)-1):
    if alignedA[h] == alignedB[h] and alignedA[h+1] == alignedB[h+1]:
        conseNum = conseNum + 1

#Printing out report
longer = max(len(name1), len(name2))
print(" "*(len("Sequence ") + longer - len("Sequence " + name1)) + "Sequence " + name1 + ": " + A1)
print(" "*(len("Sequence ") + longer - len("Length")) + "Length: " + str(m))
print(" "*(len("Sequence ") + longer - len("Sequence " + name2)) + "Sequence " + name2 + ": " + B1)
print(" "*(len("Sequence " + name2) - len("Length")) + "Length: " + str(n) + "\n")

print(" "*(len("Gap-Extension Penalty") - len("Match Score")) + "Match Score: " + str(matchScore))
print(" "*(len("Gap-Extension Penalty") - len("Mismatch Score")) + "Mismatch Score: " + str(mismatchScore))
print(" "*(len("Gap-Extension Penalty") - len("Gap-Open Penalty")) + "Gap-Open Penalty: " + str(gapOpen))
print("Gap-Extension Penalty: " + str(gapExtension))
print(" "*(len("Gap-Extension Penalty") - len("Bonus Score")) + "Bonus Score: " + str(bonusScore) + "\n")

print(" "*(len("Start Position in ") + longer - len("Alignment Score")) + "Alignment Score: " + str(S[rowFirst][colFirst]) + " " + "(" + str(S[rowFirst][colFirst] - conseNum*bonusScore) + " + " + str(conseNum*bonusScore) + ")")
print(" "*(len("Start Position in ") + longer - len("Length")) + "Length: " + str(len(OA)))
print(" "*(len("Start Position in ") + longer - len("Start Position in" + name1)) + "Start Position in " + name1 + ": " + str(rowFirst+1))
print(" "*(len("Start Position in ") + longer - len("Start Position in" + name2)) + "Start Position in " + name2 + ": " + str(colFirst+1))
print(" "*(len("Start Position in ") + longer - len("End Position in" + name1)) + "End Position in " + name1 + ": " + str(rowLast))
print(" "*(len("Start Position in ") + longer - len("End Position in" + name2)) + "End Position in " + name2 + ": " + str(colLast) + "\n")

print(" "*(len("Number of mismatches") - len("Number of matches")) + "Number of Matches: " + str(matchNum))
print(" "*(len("Number of mismatches") - len("Percent identity")) + "Percent Identity: " + str(round(matchNum/len(OA)*100)) + "%")
print("Number of Mismatches: " + str(mismatchNum))
print(" "*(len("Number of mismatches") - len("Number of gaps")) + "Number of Gaps: " + str(gapNum) + "\n")

l = int(len(alignedA)/70) #calculating the number of blocks to be displayed
gapInA = 0 #number of gaps in A 
gapInB = 0 #number of gaps in B

dots = [" "]*70
for i in range(len(dots)):
    if i%10 == 9 and i%2 == 1:
        dots[i] = ":"
    elif i%5 == 4:
        dots[i] = "."
        
c = 0 #keeping track of the block
for c in range(1, l+1, 1):
    if c != 1:
        for e in alignedA[(c-1-1)*70:((c-1)*70)]:
            if e == " ":
                gapInA = gapInA + 1
        for f in alignedB[(c-1-1)*70:((c-1)*70)]:
            if f == " ":
                gapInB = gapInB + 1
    
    print(str(1+(c-1)*70) + " "*(10 - len(str(1+(c-1)*70))) + "".join(dots[:]))
    print(str(rowFirst+1+(c-1)*70-gapInA) + " "*(10 - len(str(rowFirst+1+(c-1)*70))) + "".join(alignedA[(c-1)*70:(c*70)]))
    print(" "*10 + "".join(match[(c-1)*70:(c*70)]))
    print(str(colFirst+1+(c-1)*70-gapInB) + " "*(10 - len(str(colFirst+1+(c-1)*70))) + "".join(alignedB[(c-1)*70:(c*70)]) + "\n")

if len(alignedA)%70 != 0:
    if c != 0:
        print(str(1+(c-1)*70) + " "*(10 - len(str(1+(c-1)*70))) + "".join(dots[0:len(alignedA[c*70:])]))
    else:
        print(str(1) + " "*(10 - len(str(1))) + "".join(dots[0:len(alignedA[c*70:])]))
    print(str(rowFirst+1+c*70-gapInA) + " "*(10 - len(str(rowFirst+1+c*70))) + "".join(alignedA[c*70:]))
    print(" "*10 + "".join(match[c*70:]))
    print(str(colFirst+1+c*70-gapInB) + " "*(10 - len(str(colFirst+1+c*70))) + "".join(alignedB[c*70:]))
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 19:55:52 2019

@author: Vu Thi-Hong-Ha
"""
import sys

#Step 0: Taking the input from console
argList = sys.argv

#Step 0.1: Sanity checking for arguments
if int(argList[3]) <= 0:
    raise Exception("Maximum number of words has to be positive!")
    
#Step 1: Read files and create combined sequence
def reverse_compliment(seq):
    reverse = list(seq)
    reverse.reverse()
    for i in range(len(reverse)):
        if reverse[i] == "A":
            reverse[i] = "T"
        elif reverse[i] == "C":
            reverse[i] = "G"
        elif reverse[i] == "G":
            reverse[i] = "C"
        elif reverse[i] == "T":
            reverse[i] = "A"
        elif reverse[i] == "a":
            reverse[i] = "t"
        elif reverse[i] == "c":
            reverse[i] = "g"
        elif reverse[i] == "g":
            reverse[i] = "c"
        elif reverse[i] == "t":
            reverse[i] = "a"
    result = seq + "#" + ''.join(reverse) + "#"
    return result

def readGenomeFile(s):
    A = []
    B = []
    with open(s, 'r') as f:
        lines = f.read().splitlines()
    for i, line in enumerate(lines): 
        if i%2 == 1:
            A.append(line)
    
    for sub in A:
        sub1 = reverse_compliment(sub)
        B.extend(sub1)
    
    genome_length = len(B)

    return B, genome_length

def readFileOfFiles(file_of_files):
    A = []
    st = [1]
    with open(file_of_files, 'r') as f:
        files = f.read().splitlines()
        numOfGenomes = len(files) #number of genomes
    
    for i, file in enumerate(files):
        if i == 0:
            with open(file, 'r') as f1:
                lines = f1.read().splitlines()
                for j, line in enumerate(lines):
                    if j%2 == 1:
                        A.extend(list(line))
                        A.append("#")
            genome1_length = len(A)
            st.append(st[0] + genome1_length)
        else:
            genome, length = readGenomeFile(file)
            A.extend(genome)
            if i != numOfGenomes-1:
                st.append(st[i] + length)
            else:
                st.append(st[i] + length-1) #the last genome doesn't have pound sign at the end
    
    A.insert(0, " ")
    del A[-1]
    
    st.insert(0, " ")
    
    return A, numOfGenomes, st
    
A, numOfGenomes, st = readFileOfFiles(argList[1])
n = len(A) - 1 #length of combined sequence, excluding the empty element at the beginning of A

#Step 2: Building look-up table
#Base scores + set up:
d_A = 0
d_C = 1
d_G = 2
d_T = 3

#read word model
#f = open(argList[2], "r")
c1 = 0
with open(argList[2], "r") as f:
    line = f.read().splitlines()
    model = list(line[0])
    if len(line) > 1:
        raise Exception("Model file must have only one line.")
    if " " in model:
        raise Exception("Model must not contain any whitespace.")
f.close()

for i in range(len(model)):
    model[i] = int(model[i])
    if model[i] == 1:
        c1 += 1
    elif model[i] != 0:
        print("Error " + str(model[i]) + " is not accepted.")
        raise Exception("Model only contains 0 or 1.")

w = len(model) #word length
buck = [0]*(4**c1+1)
l = [0]*(n+1) #list
wordCode = [" "]*(n+1)
sw = [0]*(n+2)
wlcut = int(argList[3])
pos = 0
last = 0
c = 0
p = 0


#Look-up table:
for j in range(1, n-w+2, 1):
    p = 0
    c = 0
    for i in range(j+w-1, j-1, -1):
        if model[i-j] == 1:
            if A[i] == "A" or A[i] == "a":
                c = 4**p * d_A + c
                p = p+1
            elif A[i] == "C" or A[i] == "c":
                c = 4**p * d_C + c
                p = p+1
            elif A[i] == "G" or A[i] == "g":
                c = 4**p * d_G + c
                p = p+1
            elif A[i] == "T" or A[i] == "t":
                c = 4**p * d_T + c
                p = p+1 
            elif A[i] == "N" or A[i] == "#" or A[i] == "n":
                wordCode[j] = -1
                break
        else:
            if A[i] == "#":
                wordCode[j] = -1
                break
        if i == j:
            wordCode[j] = c
    
for j in range(n-w+2, n+1, 1): #the last positions where there are not enough letters for a word
    wordCode[j] = -1
    
#Step 3: Building superword array:
bsize = 4**w
for i in range(1, n+1, 1):
    sw[i] = i
for wlev in range(1, wlcut+1, 1):
    buck = [0]*(4**w+1)
    for i in range(1, n+1):
        p = sw[i] - w
        if p > 0:
            c = wordCode[p]
            l[p] = buck[c]
            buck[c] = p
    for p in range(n-w+1, n+1):
        c = wordCode[p]
        l[p] = buck[c]
        buck[c] = p
    
    k = n+1
    for c in range(bsize-1, -2, -1):
        p = buck[c]
        while p > 0:
            k = k - 1
            sw[k] = p
            p = l[p]


#Step 4: Calculating frequency array
freq = [0]*(n+1) #frequency array

j = 1
k = 1

eq = True #check if two superwords are identical

#Frequency array
blockStartPos = []  #start positions of all sw with frequency = numOfGenome,
                    #only if the sw only comes from each genome once
uniq = True #boolean variable to check if a sw comes from each genome only once

T = ["n"]*n #Check overlap between superwords
T.insert(0, " ")

take = False #whether we will take the block or not

while j < n+1:
    k = j + 1
    eq = True
    code_at_j = [0]*wlcut
    for m in range(wlcut):
        if sw[j] + w*m > n:
            code_at_j[m] = -1
        else:
            code_at_j[m] = wordCode[sw[j] + w*m]
            
    if -1 in code_at_j:
        j = j + 1
    else:
        while eq == True:
            code_at_k = [0]*wlcut
            for h in range(wlcut):
                if sw[k] + w*h > n:
                    code_at_k[h] = -1
                else:
                    code_at_k[h] = wordCode[sw[k] + w*h]

            for x in range(wlcut):
                if code_at_j[x] != code_at_k[x]:
                    eq = False
                    break

            if eq == True:
                k = k+1
        freq[k-j] = freq[k-j] + 1
        if k-j == numOfGenomes: #Check if each sw comes from each genome exactly once
            for h in range(j, k, 1):
                if sw[h] >= st[h-j+1] and sw[h] < st[h-j+2]:
                    uniq = True
                else:
                    uniq = False
                    break
            if uniq == True:
                for e in sw[j:k]: #check if the superwords overlap
                    if "y" in T[e:(e+w*wlcut)]:
                        take = False
                        break
                    else:
                        take = True
                        T[e:(e+w*wlcut)] = ["y" for el in range(e, (e+w*wlcut), 1)]
                if take == True:
                    blockStartPos.append(sw[j:k])
        j = k

#Concatnate multiple seq alignment
alignment = argList[1] + ".alignment"
f2 = open(alignment, "w+")
for i in range(0, numOfGenomes, 1):
    genome = []
    for j in range(len(blockStartPos)):
        genome.extend(A[blockStartPos[j][i]:(blockStartPos[j][i]+w*wlcut)])
    f2.write(">Genome " + str(i+1) + "\n" + ''.join(genome) + "\n")
        
f2.close()

#Report word model
summary = argList[1] + ".summary"
f3 = open(summary, "a+")
   
def convert(list): 
    # Converting integer list to string list 
    s = [str(i) for i in list] 
    # Join list items using join() 
    res = int("".join(s)) 
      
    return(res) 
    
f3.write(str(convert(model)) + "\n")
        
#Report wlcut:
f3.write(str(wlcut) + "\n")

#the length of a largest subset of superword blocks
f3.write(str(len(blockStartPos)*w*wlcut) + "\n")
        
#the number of superword blocks in the subset
f3.write(str(len(blockStartPos)) + "\n")

f3.close()
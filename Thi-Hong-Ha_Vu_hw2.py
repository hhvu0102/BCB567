# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 21:14:57 2019

@author: Vu Thi-Hong-Ha; NetID: 851924086
"""

#import sys

#Step 0: Taking the input from console
#argList = sys.argv
#
##Step 0.1: Sanity checking for arguments
#if int(argList[2]) <= 0:
#    raise Exception("Maximum number of words has to be positive!")
    
#Step 1: Read file
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
    result = seq + "#" + ''.join(reverse)
    return result

def readFile(s):
    A = []
    B = []
    with open(s, 'r') as f:
        lines = f.read().splitlines()
    for i, line in enumerate(lines): 
        if i%4 == 1:
            A.append(line)
    
    for sub in A:
        sub1 = reverse_compliment(sub)
        B.extend(sub1)
    
    B.insert(0, " ")
    return B

#A = readFile(argList[1])
A = readFile("D:\\Coursework\\BCB 567 Fall 2019\\Assignment2\\data_10.fastq")

#Step 2: Building look-up table
#Base scores + set up:
d_A = 0
d_C = 1
d_G = 2
d_T = 3
#model = [1, 1]
w = 2 #word length
n = len(A) - 1 #actual length of A, excluding the space at the beginning
buck = [0]*(4**w+1)
l = [0]*(n+1) #list
wordCode = [" "]*(n+1)
sw = [0]*(n+2)
#wlcut = int(argList[2])
wlcut = 1
pos = 0
last = 0
c = 0

#Look-up table:
for j in range(1, n-w+2, 1):
    for i in range(j, j+w-1, 1):
        if "N" not in A[j:(j+w-1)] and "#" not in A[j:(j+w-1)]:
            if A[i] == "A":
                c = 4*c + d_A
            elif A[i] == "C":
                c = 4*c + d_C
            elif A[i] == "G":
                c = 4*c + d_G
            elif A[i] == "T":
                c = 4*c + d_T
            last = last + w-1
        else:
            if A[i] == "N" or A[i] == "#":
                pos = i
            for k in range(j, pos+1, 1):
                wordCode[k] = -1
            continue
    if A[j+w-1] == "N" or A[j+w-1] == "#":
        last = 0
        c = 0
    else:
        last = last + 1
        if A[j+w-1] == "A":
            c = (4*c + d_A)%(4**w)
        elif A[j+w-1] == "C":
            c = (4*c + d_C)%(4**w)
        elif A[j+w-1] == "G":
            c = (4*c + d_G)%(4**w)
        elif A[j+w-1] == "T":
            c = (4*c + d_T)%(4**w)
    if last >= w:
        wordCode[j] = c
    else:
        wordCode[j] = -1

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
        j = k
        
#Step 5: Reports
for k in range(1, len(freq)):
    if freq[k] != 0:
        print("k = " + str(k) + "; count(k) = " + str(freq[k]))
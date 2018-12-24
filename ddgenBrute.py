import numpy
import random, re, json

maxDuties = 10	# Max duties per person
maxPerDay = 2	#Max duties per person per day
slotsPerDay = 11	# Number of slots in a day
duties = [i for i in range(9)]	# Duties ka slots

tt = [["SJT","SJT","SJT","","SJT","","","SJT","SJT","",""],["SJT","SJT","SJT","SJT","","","","SJT","SJT","",""],["SJT","SJT","SJT","","","","","SJT","SJT","",""],["SJT","SJT","SJT","SJT","","","","","SJT","",""],["SJT","SJT","SJT","","SJT","SJT","SJT","","","",""]]

def findPrev(day, slot, t):		# Finds previous class location and slot
	for i in range(slot, 0, -1):
		if t[day][i] != "":
			return [i, t[day][i]]
	return -1		

def findNext(day, slot, t):		# Finds next class location and slot
	for i in range(slot + 1, slotsPerDay, 1):
		if t[day][i] != "":
			return [i, t[day][i]]
	return -1		

def findBreaks(day, t):		# Finds breaks in the day
	breaks = []
	for i in range(0, slotsPerDay):
		if t[day][i] == "":
			breaks.append(i)
	return breaks	

def findSingleBreaks(day, tt):
	breaks = []
	for i in range(0, slotsPerDay - 1):
		if  tt[day][i] == "" and ((i == 0) or (tt[day][i - 1] != "" and tt[day][i + 1] != "")):
			breaks.append(i)
	return breaks

def findDoubleBreaks(day, tt):
	breaks = [];
	for i in range(0, slotsPerDay - 2):
		if tt[day][i] == "" and ((i == 0) or (tt[day][i + 1] == "") and tt[day][i + 1] == "" and tt[day][i + 2] != ""):
			breaks.append(i)
	return breaks


def countValidity(duties):
	x = 1

def generateDuties(duties=None):
	if not duties:
		duties = {"count": 0, "assigned": [], "dayCount": [0, 0, 0, 0, 0]};

	while(duties["count"] < maxDuties):
		breaks = findBreaks(0)
		assign = random.choice(breaks)




print(findPrev(0, 3, tt))
print(findNext(0, 3, tt))
print(findBreaks(0, tt))
print(findSingleBreaks(4, tt))
print(findDoubleBreaks(0, tt))
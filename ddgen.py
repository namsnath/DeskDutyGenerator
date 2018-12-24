import numpy
from pprint import pprint
import random, re, json

slotsPerDay = 11
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

def findSingleBreaks(tt):
	breaks = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": []}

	for j in range(0, 5):
		for i in range(0, slotsPerDay - 1):
			if  tt[j][i] == "" and ((i == 0) or (tt[j][i - 1] != "" and tt[j][i + 1] != "")):
				breaks[days[j]].append(i)
	return breaks

def findFree(day, slot):
	jr = []
	sr = []

	for i in juniorCore:
		if i in juniorCoreData:
			if juniorCoreData[i][day][slot] == "":
				jr.append(i)

	for i in seniorCore:
		if i in seniorCoreData:
			if seniorCoreData[i][day][slot] == "":
				sr.append(i)			
	return (jr, sr)				

def genDuty(duty=None, peeps=None):
	if duty == None or peeps == None:
		duty = {"Monday": [["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""]], 
				"Tuesday": [["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""]], 
				"Wednesday": [["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""]], 
				"Thursday": [["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""]], 
				"Friday": [["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""]], 
				"count": 0,
				# "Filled": [False, False, False, False, False]
				}

		peeps = {}
		for i in seniorCore:
			peeps[i] = { "count": 0, "dayCount": [0, 0, 0, 0, 0] }

		for i in juniorCore:
			peeps[i] = { "count": 0, "dayCount": [0, 0, 0, 0, 0] }	

		
	# while not any(duty["Filled"]):
	while duty["count"] < 80:

		for i in range(5):
			for j in range(8):
				sr, jr = findFree(i, j)

				if sr != []:
					srChoice = random.choice(sr)
					peeps[srChoice]["count"] += 1
					peeps[srChoice]["dayCount"][i] += 1
					duty[days[i]][j][0] = srChoice
					duty["count"] += 1
				else:
					duty[days[i]][j][0] = ""	

				if jr != []:
					jrChoice = random.choice(jr)
					peeps[jrChoice]["count"] += 1
					peeps[jrChoice]["dayCount"][i] += 1
					duty[days[i]][j][1] = jrChoice
					duty["count"] += 1
				else:
					duty[days[i]][j][1] = ""

	return (duty, peeps)		


def person_fitness(peeps, person):
	fitness = 0
	if peeps[person]["count"] <= maxSlots["total"]:
		fitness += points["total"]
	
	daily = True
	for j in range(5):
		if peeps[person]["dayCount"][j] > maxSlots["daily"]:
			daily = False;
	if daily:
		fitness += points["daily"]

	return fitness			

def slot_fitness(peeps, person):
	fitness = 0


srData = open("srCoreData.txt")
jrData = open("jrCoreData.txt")

seniorCore = ['Atul', 'Ayush', 'Charu', 'Kabiir', 'Krityaan', 'Manisha', 'Namit', 'Pavithra', 'Rishab', 'Saksham', 'Sakshi', 'Sarthak', 'Saurav', 'Simran', 'Sonal']
seniorCoreData = json.loads(srData.read())

juniorCore = ['Aban', 'Aradhita', 'Bhavishya', 'Chinmay', 'David', 'Devam', 'Fardeen', 'Gauri', 'Kuhoo', 'Lakshay', 'Manan', 'Prajeeth', 'Rishit', 'Rohan', 'Ruchica', 
			'Sanjana', 'SauravH', 'Siddharth', 'Suranjan', 'Taarussh', 'Tajendar', 'Tanya', 'Thiru', 'Vaishnavi']
juniorCoreData = json.loads(jrData.read())

# data = {"Manisha":[["SJT","SJT","SJT","SJT","SJT","SJT","SJT","","","",""],["SJT","SJT","SJT","SJT","SJT","SJT","SJT","","","",""],["SJT","SJT","SJT","SJT","","SJT","SJT","","","",""],["SJT","SJT","SJT","SJT","SJT","SJT","SJT","","","",""],["SJT","SJT","SJT","SJT","SJT","SJT","SJT","","","",""]],"Saksham":[["SJT","SJT","","SJT","TT","","","SJT","","",""],["SJT","","SJT","SJT","","SJT","SJT","SJT","","",""],["SJT","","SJT","SJT","","","","","SJT","",""],["","SJT","","SJT","","SJT","SJT","SJT","SJT","",""],["SJT","SJT","","SJT","SJT","SJT","","SMV","SMV","",""]],"Krityaan":[["SJT","SJT","SJT","","","","","SJT","SJT","SJT",""],["","","SJT","SJT","","SJT","SJT","SJT","","",""],["SJT","SJT","SJT","","SJT","","","","","",""],["SJT","","","SJT","SJT","","","","SJT","",""],["SJT","SJT","","SJT","SJT","SJT","","SMV","SMV","",""]],"Atul":[["","","SJT","","CDMM","SJT","","","SJT","SJT","SJT"],["SJT","CDMM","CDMM","TT","","SJT","SJT","","","SJT",""],["TT","","SJT","SJT","TT","","SJT","","TT","",""],["SJT","SJT","CDMM","CDMM","TT","","","SJT","SJT","SJT",""],["CDMM","TT","","","SJT","SJT","SJT","SJT","","",""]],"Rishab":[["","SMV","TT","TT","SJT","SJT","","SJT","SJT","",""],["TT","SJT","TT","TT","","TT","TT","","TT","TT",""],["TT","","SMV","","","","SJT","","","",""],["TT","TT","SJT","TT","","","","","SJT","",""],["TT","TT","","SMV","TT","","","","","",""]],"Namit":[["SJT","SJT","SJT","","SJT","","","SJT","SJT","",""],["SJT","SJT","SJT","SJT","","","","SJT","SJT","",""],["SJT","SJT","SJT","","","","","SJT","SJT","",""],["SJT","SJT","SJT","SJT","","","","","SJT","",""],["SJT","SJT","SJT","","SJT","SJT","SJT","","","",""]],"Kabiir":[["","","","","","TT","","TT","TT","",""],["","SJT","TT","TT","TT","TT","TT","MB","TT","",""],["","","TT","TT","","TT","TT","SJT","SJT","","TT"],["","","SJT","TT","","TT","TT","TT","MB","TT",""],["TT","","","","","MB","TT","","","",""]],"Pavithra":[["SJT","","SJT","SJT","","SJT","","","","",""],["SJT","SMV","SJT","SJT","SJT","SJT","SJT","SJT","SJT","",""],["SJT","SJT","","SJT","SJT","","SJT","TT","TT","",""],["SJT","SJT","SMV","SJT","SJT","","","","SJT","",""],["SJT","SJT","SJT","SJT","SJT","","","","","",""]],"Sarthak":[["TT","","TT","TT","SJT","","","SJT","SJT","",""],["TT","SJT","TT","TT","","SMV","SMV","TT","TT","",""],["TT","TT","","","","TT","TT","","","",""],["TT","TT","SJT","TT","","","","","SJT","",""],["TT","TT","TT","","TT","TT","","","","",""]],"Charu":[["SJT","SJT","SJT","SJT","","","","","","",""],["SJT","","SJT","SJT","","","TT","SJT","SJT","",""],["SJT","SJT","SJT","","SJT","","","SJT","SJT","",""],["SJT","SJT","","SJT","SJT","","","TT","SJT","SJT",""],["SJT","SJT","","TT","SJT","MB","MB","","","",""]],"Simran":[["SJT","SJT","SJT","SJT","","","","","","SJT",""],["SJT","","SJT","SJT","","SJT","SJT","","SJT","SJT",""],["SJT","SJT","SJT","","SJT","","","TT","TT","",""],["SJT","SJT","","SJT","SJT","","","","SJT","SJT",""],["SJT","SJT","","","SJT","","","","","",""]],"Ayush":[["TT","SMV","","TT","TT","","","","","",""],["SJT","TT","TT","CBMR","","TT","TT","TT","TT","",""],["CBMR","TT","SMV","","CBMR","TT","","SJT","SJT","",""],["","SJT","TT","TT","CBMR","TT","TT","","SJT","",""],["TT","CBMR","TT","SMV","","","TT","","","",""]],"Sakshi":[["","SJT","SJT","SJT","TT","","","SJT","SJT","SJT",""],["SJT","TT","SJT","TT","","","SJT","","","",""],["TT","","SJT","","TT","SJT","SJT","","","",""],["SJT","SJT","TT","SJT","TT","TT","TT","SJT","","",""],["SJT","TT","","","SJT","","","","","",""]],"Saurav":[["SJT","","SJT","","CDMM","","","","SJT","SJT",""],["SJT","CDMM","TT","TT","","SJT","SJT","","","",""],["TT","SJT","SJT","SJT","TT","","","","TT","",""],["SJT","SJT","CDMM","TT","TT","","","SJT","SJT","SJT",""],["TT","TT","SJT","SJT","SJT","SJT","SJT","","","",""]],"Sonal":[["SJT","SJT","SJT","SJT","","","","","SJT","SJT",""],["SJT","SJT","SJT","SJT","","","","SJT","SJT","",""],["SJT","SJT","SJT","","SJT","","","","","",""],["SJT","SJT","SJT","SJT","SJT","","","","SJT","SJT",""],["SJT","SJT","TT","","SJT","MB","MB","","","",""]]}

srSingleBreaks = {}
jrSingleBreaks = {}


for i in seniorCore:
	if i not in seniorCoreData:
		continue
	srSingleBreaks[i] = findSingleBreaks(seniorCoreData[i])
# pprint(srSingleBreaks)	

for i in juniorCore:
	if i not in juniorCoreData:
		continue
	jrSingleBreaks[i] = findSingleBreaks(juniorCoreData[i])
# pprint(jrSingleBreaks)	


maxSlots = {
	"total": 8,
	"daily": 2
}

points = {
	"total": 8,
	"daily": 2 * 5,
}

(duty, peeps) = genDuty()
print("peeps")
pprint(peeps)
print("duty")
pprint(duty)

for i in seniorCore:
	print(i, person_fitness(peeps, i))


for i in juniorCore:
	print(i, person_fitness(peeps, i))	

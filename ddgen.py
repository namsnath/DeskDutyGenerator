import numpy
from pprint import pprint
import random, re, json

################################################## Constants ##################################################

slotsPerDay = 11
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
seniorCore = ['Atul', 'Ayush', 'Charu', 'Kabiir', 'Krityaan', 'Manisha', 'Namit', 'Pavithra', 'Rishab', 'Saksham', 'Sakshi', 'Sarthak', 'Saurav', 'Simran', 'Sonal']
juniorCore = ['Aban', 'Aradhita', 'Bhavishya', 'Chinmay', 'David', 'Devam', 'Fardeen', 'Gauri', 'Kuhoo', 'Lakshay', 'Manan', 'Prajeeth', 'Rama', 'Rishit', 'Rohan', 'Ruchica', 
			'Sanjana', 'SauravH', 'Siddharth', 'Suranjan', 'Taarussh', 'Tajendar', 'Tanya', 'Thiru', 'Vaishnavi']

core = ['Atul', 'Ayush', 'Charu', 'Kabiir', 'Krityaan', 'Manisha', 'Namit', 'Pavithra', 'Rishab', 'Saksham', 'Sakshi', 'Sarthak', 'Saurav', 'Simran', 'Sonal',
		'Aban', 'Aradhita', 'Bhavishya', 'Chinmay', 'David', 'Devam', 'Fardeen', 'Gauri', 'Kuhoo', 'Lakshay', 'Manan', 'Prajeeth', 'Rishit', 'Rohan', 'Ruchica', 
		'Sanjana', 'SauravH', 'Siddharth', 'Suranjan', 'Taarussh', 'Tajendar', 'Tanya', 'Thiru', 'Vaishnavi']

srData = open("srCoreData.txt")
seniorCoreData = json.loads(srData.read())

jrData = open("jrCoreData.txt")
juniorCoreData = json.loads(jrData.read())

crData = open("coreData.txt")
coreData = json.loads(crData.read())

srSingleBreaks = {}
jrSingleBreaks = {}
singleBreaks = {i: None for i in core}
# pprint(singleBreaks)

maxSlots = {
	"total": 8,
	"daily": 2
}

points = {
	"total": 0.4,
	"daily": 0.5,
	"singleBreak": 2,
	"doubleBreak": 0.5,
	"fullDuty": 20,
	"venue": 1,
	"empty": -20,
}



highestScore = 0
highest = []
population = []
fit = []

################################################## Constants ##################################################

################################################## Functions ##################################################

def findNext(day, slot, person):		# Finds next class location and slot
	if person not in coreData:
		return [-1, None]
	t = coreData[person]
	for i in range(slot + 1, slotsPerDay, 1):
		if t[day][i] != "":
			return [i, t[day][i]]
	return [-1, None]

def findSingleBreaks(tt):
	breaks = [[], [], [], [], []]

	for j in range(0, 5):
		for i in range(0, slotsPerDay - 1):
			if  tt[j][i] == "" and ((i == 0) or (tt[j][i - 1] != "" and tt[j][i + 1] != "")):
				breaks[j].append(i)
	return breaks

def findFree(day, slot, peeps):
	jr = []
	sr = []

	for i in juniorCore:
		if i in coreData and peeps[i]["dayCount"][day] < maxSlots["daily"]: #Because the hard coded condition beats the purpose of populations
		# if i in juniorCoreData:
			if coreData[i][day][slot] == "":
				jr.append(i)

	for i in seniorCore:
		if i in coreData and peeps[i]["dayCount"][day] < maxSlots["daily"]:
		# if i in seniorCoreData:	
			if coreData[i][day][slot] == "":
				sr.append(i)			
	return (jr, sr)				

def genDuty(duty=None, peeps=None):
	if duty == None or peeps == None:
		duty = {"Monday": [{"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}], 
				"Tuesday": [{"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}], 
				"Wednesday": [{"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}], 
				"Thursday": [{"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}], 
				"Friday": [{"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}, {"SJT": [], "TT": []}], 
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
				jr, sr = findFree(i, j, peeps)

				for k in range(2):
					if k == 0:
						venue = "SJT"
					else:
						venue = "TT"

					if sr == [] and jr == []:
						# print(i, j, k)
						continue

					if jr != []:
						jrChoice = random.choice(jr)
						jr.remove(jrChoice)
						peeps[jrChoice]["count"] += 1
						peeps[jrChoice]["dayCount"][i] += 1
						duty[days[i]][j][venue].append(jrChoice)
						duty["count"] += 1
					elif sr != []:
						srChoice = random.choice(sr)
						sr.remove(srChoice)

						peeps[srChoice]["count"] += 1
						peeps[srChoice]["dayCount"][i] += 1
						duty[days[i]][j][venue].append(srChoice)
						duty["count"] += 1
					# else:
					# 	# print("jr", i, j, k)
					# 	duty[days[i]][j][[1 + k*2]] = ""

					if sr != []:
						srChoice = random.choice(sr)
						sr.remove(srChoice)

						peeps[srChoice]["count"] += 1
						peeps[srChoice]["dayCount"][i] += 1
						duty[days[i]][j][venue].append(srChoice)
						duty["count"] += 1
					elif jr != [] and len(jr) > 2:
						jrChoice = random.choice(jr)
						jr.remove(jrChoice)
						peeps[jrChoice]["count"] += 1
						peeps[jrChoice]["dayCount"][i] += 1
						duty[days[i]][j][venue].append(jrChoice)
						duty["count"] += 1
					# else:
					# 	# print("sr", i, j, k)
					# 	duty[days[i]][j][0 + k*2] = ""


	return (duty, peeps)		

def generatePopulation(count):
	global fit, highest, highestScore

	while len(fit) < count:
		duty, peeps = genDuty()
		fitnessScore = fitness(peeps, duty)
		fit.append((peeps, duty, fitnessScore))

		if fitnessScore > highestScore:
			highest = [peeps, duty]
			highestScore = fitnessScore

def balance():
	global fit
	fit.sort(key=lambda x: x[2], reverse=True)
	fit = fit[:int(0.4 * len(fit))]

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

def slot_fitness(peeps, duty, person):
	fitness = 0
	peopleAssigned = []
	for i in range(5):
		for j in range(8):
			nextClass = findNext(i, j, person)
			if nextClass == [-1, None]:
				fitness += 0
			elif nextClass[0] == j + 1 and nextClass[1] == "SJT" and person in duty[days[i]][j]["SJT"]:
				fitness += points["venue"]
			elif nextClass[0] == j + 1 and nextClass[1] != "SJT" and person in duty[days[i]][j]["TT"]:
				fitness += points["venue"]

			peopleAssigned = duty[days[i]][j]["SJT"] + duty[days[i]][j]["TT"]
			if person in peopleAssigned and person in coreData:
				if j in singleBreaks[person][i]:
					fitness += points["singleBreak"]
					# print(i, j, peopleAssigned)
	return fitness

def overall_fitness(peeps, duty):
	fitness = 0
	full = True
	emptyCount = 0
	for i in range(5):
		for j in range(8):
			if duty[days[i]][j]["SJT"] == [] or duty[days[i]][j]["TT"] == []:
				full = False
				emptyCount += 1
	if full:
		fitness += points["fullDuty"]
	else:
		fitness += points["empty"] * emptyCount
	return fitness	

def fitness(peeps, duty):
	score = 0
	for i in core:
		score += person_fitness(peeps, i) + slot_fitness(peeps, duty, i)
	score += overall_fitness(peeps, duty)	
	return score	 
################################################## Functions ##################################################

################################################## Run ##################################################

for i in core:
	if i not in coreData:
		continue
	singleBreaks[i] = findSingleBreaks(coreData[i])	
pprint(singleBreaks)

# pprint(singleBreaks)	

# (duty, peeps) = genDuty()
# print("peeps")
# pprint(peeps)
# print("duty")
# pprint(duty)

# print("\n\nFitness:")
# print(round(fitness(peeps, duty)))

# for i in juniorCore:
# 	print(i, person_fitness(peeps, i) + slot_fitness(peeps, duty, i), peeps[i])


generatePopulation(10000)
balance()
print("FIT Population",len(fit))
print("Highest score", highestScore)
pprint(fit[0])


for i in fit:
	if i[1]["Thursday"][3]["TT"] != [] and i[1]["Friday"][4]["TT"] != []:
		pprint(i[1]["Thursday"][3], i[1]["Friday"][4], i[2])


################################################## Run ##################################################
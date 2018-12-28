import numpy
from pprint import pprint
import random, re, json
from collections import Counter

################################################## Doodling ##################################################

"""
Chromosome:
		0-160 (Day-5 Slot-8 Bldg-2 Duty-2)
______________________________________________________
					People Assigned
______________________________________________________

"""

################################################## Doodling ##################################################


################################################## Constants ##################################################

slotsPerDay = 11
dutySlotsPerDay = 8
dayCount = 5
buildingCount = 2
dutiesPerBuilding = 2

DAY_INDEX = dutySlotsPerDay * buildingCount * dutiesPerBuilding
SLOT_INDEX = buildingCount * dutiesPerBuilding
BLDG_INDEX = dutiesPerBuilding
DUTY_INDEX = 1

POPULATION_SIZE = 8000
GENERATIONS = 40
CHILDREN_MULTIPLIER = 0.4
chromosomeLength = dutySlotsPerDay * dayCount * buildingCount * dutiesPerBuilding

details = []

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
slots = ["8-9", "9-10", "10-11", "11-12", "12-1", "2-3", "3-4", "4-5"]
buildings = ["SJT", "TT"]
duties = [1, 2]

seniorCore = ['Atul', 'Ayush', 'Charu', 'Kabiir', 'Krityaan', 'Manisha', 'Namit', 'Pavithra', 'Rishab', 'Saksham', 'Sakshi', 'Sarthak', 'Saurav', 'Simran', 'Sonal']
juniorCore = ['Aban', 'Aradhita', 'Bhavishya', 'Chinmay', 'David', 'Devam', 'Fardeen', 'Gauri', 'Kuhoo', 'Lakshay', 'Manan', 'Prajeeth', 'Rama', 'Rishit', 'Rohan', 'Ruchica', 
			'Sanjana', 'SauravH', 'Siddharth', 'Suranjan', 'Taarussh', 'Tajendar', 'Tanya', 'Thiru', 'Vaishnavi']

core = ['Atul', 'Ayush', 'Charu', 'Kabiir', 'Krityaan', 'Manisha', 'Namit', 'Pavithra', 'Rishab', 'Saksham', 'Sakshi', 'Sarthak', 'Saurav', 'Simran', 'Sonal',
		'Aban', 'Aradhita', 'Bhavishya', 'Chinmay', 'David', 'Devam', 'Fardeen', 'Gauri', 'Kuhoo', 'Lakshay', 'Manan', 'Prajeeth', 'Rishit', 'Rohan', 'Ruchica', 
		'Sanjana', 'SauravH', 'Siddharth', 'Suranjan', 'Taarussh', 'Tajendar', 'Tanya', 'Thiru', 'Vaishnavi']

data = open("coreData.txt")
coreData = json.loads(data.read())

singleBreaks = {i: None for i in core}
singleBreaksFlat = {i: None for i in core}

sameSlot = []
sameDay = []

maxSlots = {
	"total": 8,
	"daily": 2
}

points = {
	# "free": 1.0,
	"total": 0.4,
	"daily": 0.5,
	"singleBreak": 7.0,
	"doubleBreak": 0.5,
	# "fullDuty": 20.0,
	# "empty": -20.0,
	"venue": 1.0,
	"clash": -4.0,
}



highestScore = 0
highest = 0
population = []
fit = []

################################################## Constants ##################################################

################################################## Functions ##################################################

def generateSameList():
	i = 0
	while i < chromosomeLength:
		slots = [j for j in range(i, i + SLOT_INDEX)]
		sameSlot.append(slots)
		i += 4

	i = 0
	while i < chromosomeLength:
		d = [j for j in range(i, i + DAY_INDEX)]
		sameDay.append(d)
		i += 32	

	# pprint(sameSlot)
	# pprint(sameDay)


def generateSingleBreakData():
	global dayCount, dutySlotsPerDay, buildingCount, dutiesPerBuilding, singleBreaks, singleBreaksFlat
	dayIndex = dutySlotsPerDay*buildingCount*dutiesPerBuilding
	slotIndex = buildingCount*dutiesPerBuilding

	for k in core:
		if k in coreData:
			tt = coreData[k]

			breaks = [[], [], [], [], []]
			breaksFlat = []

			for j in range(dayCount):
				for i in range(dutySlotsPerDay - 1):
					if  tt[j][i] == "" and ((i == 0) or (tt[j][i - 1] != "" and tt[j][i + 1] != "")):
						breaks[j].append(k)
						breaksFlat.append(dayIndex*j + slotIndex*i)

			singleBreaksFlat[k] = breaksFlat			
			singleBreaks[k] = breaks

	# pprint(singleBreaksFlat)		


def findFree(day, slot):
	peeps = []

	for i in core:
		if i in coreData and coreData[i][day][slot] == "":
			peeps.append(i)

	return peeps		

def getFreePeople(day, slot):
	peeps = findFree(day, slot)
	return peeps

def getPerson(day, slot):
	freePeeps = getFreePeople(day, slot)
	return random.choice(freePeeps)

def generateDetails():
	global details

	dutyIndex = dutiesPerBuilding
	bldgIndex = dutyIndex * buildingCount
	slotIndex = bldgIndex * dutySlotsPerDay
	dayIndex = slotIndex * dayCount

	for i in range(chromosomeLength):
		day = int(i % dayIndex / slotIndex)
		slot = int(i % slotIndex / bldgIndex)
		bldg = int(i % bldgIndex / dutyIndex)
		duty = int(i % dutyIndex)
		details.append((day, slot, bldg, duty))

	# pprint(details)	


def calculateDetails(n):
	global details
	return details[n]

def createEmptyChromosome():
	return {"chromosome": [], "score": 0}

def createChromosomeMaterial():
	# length = dayCount * dutySlotsPerDay * buildingCount * dutiesPerBuilding

	chromosome = []
	for i in range(chromosomeLength):
		det = calculateDetails(i)
		chromosome.append(getPerson(det[0], det[1]))
	
	return chromosome

def generatePopulation(count):
	population = []

	for i in range(count):
		cr = createEmptyChromosome()
		cr["chromosome"] = createChromosomeMaterial()
		population.append(cr)

	return population	

# Returns the intersection of two lists
def intersection(l1, l2):
	return list(set(l1) & set(l2))

# Function to calculate the score for clashes in the duty assignment 
# Clarification: places where the same person has multiple duties in the same slot
def slotClashScore(chromosome, person):
	indices = [i for i, x in enumerate(chromosome) if x == person]
	
	score = 0

	for i in sameSlot:
		intersect = intersection(indices, i)
		if len(intersect) > 1:
			score += points["clash"] * len(intersect)
	
	return score

# Function to calculate score for the maximum daily slots limit
def totalDailyScore(chromosome, person):
	score = 0
	indices = [i for i, x in enumerate(chromosome) if x == person]

	for i in sameDay:
		intersect = intersection(indices, i)

		if len(intersect) <= maxSlots["daily"]:
			score += points["daily"]
	return score	

# Function to calculate score for the maximum total slots limit
def totalSlotsScore(chromosome, person):
	score = 0
	if chromosome.count(person) <= maxSlots["total"]:
		score += points["total"]
	return score

def personFitness(chromosome, person):
	score = 0
	dayValid = True

	score += totalSlotsScore(chromosome, person)
	score += totalDailyScore(chromosome, person)
	score += slotClashScore(chromosome, person)

	return score

def calculateScore(chromosome):
	score = 0

	for i in coreData:
		score += personFitness(chromosome, i)

	for i in range(chromosomeLength):
		x = 1

	return score

def calculatePopulationScores(population):
	avg = 0

	maxLen = len(population)

	for i in range(0, maxLen):
		data = population[i]

		score = calculateScore(data["chromosome"])
		population[i]["score"] = score
		avg += score
		# print(i, score)

	avg /= len(population)
	print("Average = ", avg)

	return population

def selection(population):
	newPopulation = []

	FIT_RETENTION = 0.3
	RANDOM_RETENTION = 0.2

	fitCount = int(FIT_RETENTION * len(population))
	randCount = int(RANDOM_RETENTION * len(population))

	# print("\nFIT = ", fitCount, "\nRANDOM = ", randCount)

	population.sort(key=lambda k: k["score"], reverse=True)
	
	for i in range(fitCount):
		newPopulation.append(population[i])
	
	for i in range(randCount):
		newPopulation.append(random.choice(population))

	return newPopulation	

def crossover(p1, p2):
	global chromosomeLength

	chance = random.random()
	crossoverLength = int(0.5 * chromosomeLength)
	
	child = createEmptyChromosome()

	if chance < 0.5:
		child["chromosome"] = p1["chromosome"][:crossoverLength] + p2["chromosome"][crossoverLength:]
	else:
		child["chromosome"] = p2["chromosome"][:crossoverLength] + p1["chromosome"][crossoverLength:]	
	child["score"] = calculateScore(child["chromosome"])

	return child

def doCrossover(population):
	p1 = random.choice(population)
	p2 = random.choice(population)

	child = crossover(p1, p2)

	return child

def mutation(item):
	geneNumber = int(random.random() * chromosomeLength)
	det = calculateDetails(geneNumber)

	item["chromosome"][geneNumber] = getPerson(det[0], det[1])
	item["score"] = calculateScore(item["chromosome"])

	return item

def doMutation(population):
	item = int(random.random() * len(population))

	population[item] = mutation(population[item])

def generation(population):
	selected = selection(population)
	if not len(selected) > 0:
		return population

	children = []
	childrenCount = int(CHILDREN_MULTIPLIER * len(selected))

	while len(children) <= childrenCount:
		child = doCrossover(population)

		child = mutation(child)

		children.append(child)

	newPopulation = selected + children

	if not len(newPopulation) > 0:
		return population

	return newPopulation

def algorithm():
	global POPULATION_SIZE
	global GENERATIONS

	population = generatePopulation(POPULATION_SIZE)
	population = calculatePopulationScores(population)


	# while len(population) > 2:
	for i in range(GENERATIONS):
		print("\nGENERATION #", i)
		
		population = generation(population)
		calculatePopulationScores(population)
		print("Population Length = ", len(population))

		findAverage(population)
		findFittest(population)	

	print("\n\nFinally, ")
	findAverage(population)
	fittest = findFittest(population)["chromosome"]
	# print("Fittest = ")
	# pprint(fittest)

	print("Proper: ")
	printProperly(fittest)
			 
def findAverage(population):
	total = 0
	for i in population:
		total += i["score"]
	avg = total / len(population)

	print("Average Score = ", avg)	

def findFittest(population):
	population.sort(key=lambda k: k["score"], reverse=True)

	# print("Fittest = ", population[0]["chromosome"])
	print("Fittest Score = ", population[0]["score"])
	return population[0]

def printProperly(chromosome):
	global days, slots, buildings

	duties = {}
	for i in days:
		duties[i] = {}
		for j in slots:
			duties[i][j] = {}
			for k in buildings:
				duties[i][j][k] = []
				for l in range(2):
					duties[i][j][k].append("")

	for i in range(chromosomeLength):
		det = calculateDetails(i)
		duties[days[det[0]]][slots[det[1]]][buildings[det[2]]][det[3]] = chromosome[i]

	pprint(duties)	

def countDuties(chromosome):
	x = 1

################################################## Functions ##################################################

################################################## Run ##################################################

generateSameList()
generateSingleBreakData()
generateDetails()
algorithm()

# cr = createChromosomeMaterial()
# s = slotClashScore(cr, "Namit")
# print(s)
################################################## Run ##################################################

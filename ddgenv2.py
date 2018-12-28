import numpy
from pprint import pprint
import random, re, json

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

POPULATION_SIZE = 8000
GENERATIONS = 40
CHILDREN_MULTIPLIER = 0.1
chromosomeLength = dutySlotsPerDay * dayCount * buildingCount * dutiesPerBuilding

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

maxSlots = {
	"total": 8,
	"daily": 2
}

points = {
	"free": 1.0,
	"total": 0.4,
	"daily": 0.5,
	"singleBreak": 2.0,
	"doubleBreak": 0.5,
	"fullDuty": 20.0,
	"venue": 1.0,
	"empty": -20.0,
}



highestScore = 0
highest = 0
population = []
fit = []

################################################## Constants ##################################################

################################################## Functions ##################################################

def findFree(day, slot):
	peeps = []

	for i in core:
		if i in coreData and coreData[i][day][slot] == "":
			peeps.append(i)

	return peeps		

def getPerson(day, slot):
	freePeeps = getFreePeople(day, slot)
	return random.choice(freePeeps)

def getFreePeople(day, slot):
	peeps = findFree(day, slot)
	return peeps

def calculateDetails(n):
	dutyIndex = dutiesPerBuilding
	bldgIndex = dutyIndex * buildingCount
	slotIndex = bldgIndex * dutySlotsPerDay
	dayIndex = slotIndex * dayCount

	
	day = int((n % dayIndex) / slotIndex)
	slot = (int(n % slotIndex / bldgIndex))
	bldg = (int(n % bldgIndex / dutyIndex))
	duty = (int(n % dutyIndex))

	return (day, slot, bldg, duty)	

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

def calculateScore(chromosome):
	score = 0

	for i in range(chromosomeLength):
		det = calculateDetails(i)
		day = det[0]
		slot = det[1]
		bldg = det[2]
		duty = det[3]

		# print(i, chromosome[i])
		# print(day, slot, bldg, duty)
		# print(day+1, slot+1, bldg+1, duty+1)

		if chromosome[i] in coreData and coreData[chromosome[i]][day][slot] == "":
			score += points["free"]
		else:
			score -= points["free"]	

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

	p1MaterialLength = int(0.5 * chromosomeLength)
	p2MaterialLength = int(0.5 * chromosomeLength)

	child = createEmptyChromosome()

	child["chromosome"] = p1["chromosome"][:p1MaterialLength] + p2["chromosome"][p1MaterialLength:]
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

	dutyIndex = dutiesPerBuilding
	bldgIndex = dutyIndex * buildingCount
	slotIndex = bldgIndex * dutySlotsPerDay
	dayIndex = slotIndex * dayCount

	for i in range(chromosomeLength):
		day = int((i % dayIndex) / slotIndex)
		slot = (int(i % slotIndex / bldgIndex))
		bldg = (int(i % bldgIndex / dutyIndex))
		duty = (int(i % dutyIndex))

		# print(i, chromosome[i])
		# print(day, slot, bldg, duty)
		# print(day+1, slot+1, bldg+1, duty+1)

		if fittest[i] in coreData and coreData[fittest[i]][day][slot] == "":
			print(fittest[i], " Free")
		else:
			print(fittest[i], " Not Free")	


			 
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


################################################## Functions ##################################################

################################################## Run ##################################################

algorithm()

# dutyIndex = dutiesPerBuilding
# bldgIndex = dutyIndex * buildingCount
# slotIndex = bldgIndex * dutySlotsPerDay
# dayIndex = slotIndex * dayCount
# for i in range(chromosomeLength):
# 	det = list(calculateDetails(i))

# 	print(i, det, det[0]*8*2*2 + det[1]*2*2 + det[2]*2 + det[3]*1)

################################################## Run ##################################################

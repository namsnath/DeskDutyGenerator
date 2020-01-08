from pprint import pprint
import random, re, json
from collections import Counter
import statistics
from tqdm import tqdm
from copy import deepcopy

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

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
slots = ["8-9", "9-10", "10-11", "11-12", "12-1", "2-3", "3-4", "4-5", "5-6"]
buildings = ["SJT", "TT"]
duties = [1, 2]

slotsPerDay = 11
dutySlotsPerDay = len(slots)
dayCount = len(days)
buildingCount = len(buildings)
dutiesPerBuilding = len(duties)

DAY_INDEX = dutySlotsPerDay * buildingCount * dutiesPerBuilding
SLOT_INDEX = buildingCount * dutiesPerBuilding
BLDG_INDEX = dutiesPerBuilding
DUTY_INDEX = 1

POPULATION_SIZE = 8000
GENERATIONS = 40
CHILDREN_MULTIPLIER = 0.4

FIT_RETENTION = 0.3		# Percentage of fit population to be retained
RANDOM_RETENTION = 0.2	# Percentage of random population to be selected

chromosomeLength = dutySlotsPerDay * dayCount * buildingCount * dutiesPerBuilding

details = []

data = open("coreData.txt")
coreData = json.loads(data.read())
core = list(dict.keys(coreData))
random.shuffle(core)

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
	"total": 1,			# Per person
	"daily": 0.4,			# Per person, per day
	"singleBreak": 5.0,		# Per person, per slot
	"doubleBreak": 0.5,
	# "fullDuty": 20.0,
	# "empty": -20.0,
	"venue": 0.5,			# Per person, per slot if class is immediately after duty
	"clash": -5.0,			# Per person, per duty
	"avoidableClash": -10.0,	# With clash. Used if >4 people available but clash happens.
	"dutySD": -7.0,		# Per chromosome
}



highestScore = 0
highest = 0
population = []
fit = []

################################################## Constants ##################################################

################################################## Functions ##################################################

# Function to generate the sameDay and sameSlot lists
def generateSameList():
	i = 0
	while i < chromosomeLength:
		slots = [j for j in range(i, i + SLOT_INDEX)]
		sameSlot.append(slots)
		i += buildingCount * dutiesPerBuilding

	i = 0
	while i < chromosomeLength:
		d = [j for j in range(i, i + DAY_INDEX)]
		sameDay.append(d)
		i += buildingCount * dutiesPerBuilding * slotsPerDay

	# pprint(sameSlot)
	# pprint(sameDay)

# Function to generate data about the one-hour breaks of each person
def generateSingleBreakData():
	for k in core:
		if k in coreData:
			tt = coreData[k]
			breaksFlat = []

			for j in range(dayCount):
				for i in range(dutySlotsPerDay - 1):
					if  tt[j][i] == "" and (((i == 0) or (tt[j][i - 1] != "") and tt[j][i + 1] != "")) and i != 4:
						start = DAY_INDEX*j + SLOT_INDEX*i
						for l in range(dutiesPerBuilding * buildingCount):
							breaksFlat.append(start + l)

			singleBreaksFlat[k] = breaksFlat			

# Function to find the next class of the person
def findNextClass(day, slot, person):
	if person not in coreData:
		return [-1, None]
	t = coreData[person]
	for i in range(slot + 1, slotsPerDay, 1):
		if t[day][i] != "":
			return [i, t[day][i]]
	return [-1, None]

# Generates a list of people free in the given day and slot
# TODO make this into a static array to avoid recalculations
def findFree(day, slot):
	peeps = []

	for i in core:
		if i in coreData and coreData[i][day][slot] == "":
			peeps.append(i)

	return peeps		

# Function to get the free people in the given day and slot
def getFreePeople(day, slot):
	peeps = findFree(day, slot)
	return peeps

# Function to return a random free person for the given day and slot
def getPerson(day, slot):
	freePeeps = getFreePeople(day, slot)
	return random.choice(freePeeps)

# Helper function to calculate the values for day, slot, bldg and duty for each gene
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

# Function to return calculated details for day, slot, bldg, duty
def calculateDetails(n):
	global details
	return details[n]

# Function to initiate a chromosome
def createEmptyChromosome():
	return {"chromosome": [], "score": 0}

# Function to populate the chromosome
def createChromosomeMaterial():
	# length = dayCount * dutySlotsPerDay * buildingCount * dutiesPerBuilding

	chromosome = []
	for i in range(chromosomeLength):
		det = calculateDetails(i)
		chromosome.append(getPerson(det[0], det[1]))
	
	return chromosome

# Generates the given number of chromosomes for the population
def generatePopulation(count):
	population = []

	for i in tqdm(range(count)):
		cr = createEmptyChromosome()
		cr["chromosome"] = createChromosomeMaterial()
		population.append(cr)

	return population	

# Returns the intersection of two lists
def intersection(l1, l2):
	return list(set(l1) & set(l2))

# Function to calculate the score for clashes in the duty assignment 
# Clarification: places where the same person has multiple duties in the same slot
# Edit: Added condition to do slot clash scoring only if there are more than 4 people free in the slot. This should solve the problem of clashes even though someone else is free.
def slotClashScore(chromosome, person):
	indices = [i for i, x in enumerate(chromosome) if x == person]
	
	score = 0

	for i in sameSlot:
		# Details for any of the slots in the current sameSlot list.
		det = calculateDetails(i[0])	
		day = det[0]
		slot = det[1]

		personsFree = getFreePeople(day, slot)
		intersect = intersection(indices, i)

		if len(intersect) > 1 and len(personsFree) >= 4:
			score += points["clash"] * len(intersect)
			score += points["avoidableClash"] * (len(personsFree) - len(intersect))
	
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

# Function to calculate score for the assigned venue
def venueScore(chromosome, person):
	score = 0
	indices = [i for i, x in enumerate(chromosome) if x == person]

	for i in indices:
		det = calculateDetails(i)
		day = det[0]
		slot = det[1]
		bldg = det[2]
		nextDetails = findNextClass(day, slot, person)

		if nextDetails[0] - slot == 1:
			if buildings[bldg] == "SJT" and nextDetails[1] == "SJT":
				score += points["venue"]
			elif buildings[bldg] == "TT" and nextDetails[1] in ["CDMM", "MB", "GDN", "SMV", "CBMR", "TT"]:
				score += points["venue"]
	return score				

# Function to calculate score for duties assigned in single Breaks
def singleBreakScore(chromosome, person):
	score = 0
	indices = [i for i, x in enumerate(chromosome) if x == person]

	for i in indices:
		if i in singleBreaksFlat[person]:
			score += points["singleBreak"]
	return score			

# Function to calculate the fitness of each person in the timetable (slot limit and slot clash)
def personFitness(chromosome, person):
	score = 0

	score += totalSlotsScore(chromosome, person)
	score += totalDailyScore(chromosome, person)
	score += slotClashScore(chromosome, person)
	score += venueScore(chromosome, person)
	score += singleBreakScore(chromosome, person)

	return score

def dutyCountScore(chromosome):
	score = 0
	count = []

	for i in coreData:
		count.append(chromosome.count(i))

	sd = statistics.stdev(count)
	score += sd * points["dutySD"]
	return score

# Function to calculate the total fitness of the chromosome
def calculateScore(chromosome):
	score = 0

	for i in coreData:
		score += personFitness(chromosome, i)

	score += dutyCountScore(chromosome)

	return score

# Function to calculate the fitness of each chromosome in the population and display details
def calculatePopulationScores():
	global population
	avg = 0

	maxLen = len(population)

	print('Calculating chromosome scores...')
	for i in tqdm(range(0, maxLen)):
		data = population[i]

		score = calculateScore(data["chromosome"])
		population[i]["score"] = score

	return population

# Function for selection of the population
def selection():
	global population

	populationCopy = deepcopy(population)
	newPopulation = []

	fitCount = int(FIT_RETENTION * len(population))
	randCount = int(RANDOM_RETENTION * len(population))

	populationCopy.sort(key=lambda k: k["score"], reverse=True)
	newPopulation = populationCopy[:fitCount]
	
	for i in range(randCount):
		newPopulation.append(random.choice(populationCopy))

	return newPopulation	

# Function to crossover two parents in a simple 50-50 fashion.
# TODO Edit to either alternate or do a different crossover mechanism
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

# Function to initiate a crossover
# Selects random parents and calls the crossover(...) function
def doCrossover():
	global population

	p1 = random.choice(population)
	p2 = random.choice(population)

	child = crossover(p1, p2)

	return child

# Function to mutate a random gene in the chromosome
# TODO add more mutations?
def mutation(item):
	geneNumber = int(random.random() * chromosomeLength)
	det = calculateDetails(geneNumber)

	item["chromosome"][geneNumber] = getPerson(det[0], det[1])
	item["score"] = calculateScore(item["chromosome"])

	return item

# Function to select a random chromosome to mutate
# Calls the mutation(...) function
def doMutation():
	global population

	item = int(random.random() * len(population))
	population[item] = mutation(population[item])

# Function to proceed through a generation
# Selection
# Reproduction
# Mutation of each child
def generation():
	global population

	print('Proceeding through generation...')

	print("\t- Selecting...")
	selected = selection()
	if not len(selected) > 0:	# No selections made
		return

	children = []
	childrenCount = int(CHILDREN_MULTIPLIER * len(selected))

	print("\t- Reproducing and Mutating...")
	while len(children) < childrenCount:
		child = mutation(doCrossover())
		children.append(child)

	newPopulation = selected + children

	if not len(newPopulation) > 0:	# New population is empty
		return

	population = newPopulation

# Function to control the GA
# Generates population and runs through the defined generations
def algorithm():
	global POPULATION_SIZE
	global GENERATIONS
	global population

	print("Generating new Population...")
	population = generatePopulation(POPULATION_SIZE)

	print("\n\nGENERATION #0")
	calculatePopulationScores()

	print("Population Length = ", len(population))
	findAverage()
	findFittest()	


	# while len(population) > 2:
	for i in range(1, GENERATIONS):
		random.shuffle(core)
		print("\nGENERATION #", i)
		
		generation()
		calculatePopulationScores()
		print("Population Length = ", len(population))

		findAverage()
		findFittest()	

	print("\n\nFinally, ")
	findAverage()
	fittest = findFittest()["chromosome"]
	print("Duty Count Score = %s" % (dutyCountScore(fittest)))
	
	core.sort()
	print("\n\nProper: ")
	printProperly(fittest)

	print("\nIndividual Scores: ")
	printIndividualScores(fittest)

# Function to print the score split up of each person
def printIndividualScores(chromosome):
	print("Person\t\tCount\tDaily\tTotal\tClash\tVenue\tSingle\tSnglBrk")
	for i in core:
		count = chromosome.count(i)
		daily = round(totalDailyScore(chromosome, i) / points["daily"], 2)
		total = round(totalSlotsScore(chromosome, i) / points["total"], 2)
		clash = round(slotClashScore(chromosome, i) / points["clash"], 2)
		venue = round(venueScore(chromosome, i) / points["venue"], 2)
		single = round(singleBreakScore(chromosome, i) / points["singleBreak"], 2)
		brk = singleBreaksFlat[i]
		

		if len(i) < 8:
			print("%s\t\t%s\t%s\t%s\t%s\t%s\t%s\t" % (i, count, daily, total, clash, venue, single), brk)
		else:
			print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t" % (i, count, daily, total, clash, venue, single), brk)

# Function to find the average score of the population and print it			 
def findAverage():
	global population
	total = 0
	for i in population:
		total += i["score"]
	avg = total / len(population)

	print("Average Score = ", avg)	

# Function to find the fittest chromosome in the population
def findFittest():
	global population

	population.sort(key=lambda k: k["score"], reverse=True)

	# print("Fittest = ", population[0]["chromosome"])
	print("Fittest Score = ", population[0]["score"])
	return population[0]

# Function to print the chromosome in human-readable format
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

	pprint(duties, width=160)	

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

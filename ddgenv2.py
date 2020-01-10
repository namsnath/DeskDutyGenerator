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

DAYS_LIST = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
SLOTS_LIST = ["8-9", "9-10", "10-11", "11-12", "12-1", "2-3", "3-4", "4-5", "5-6"]
BUILDINGS_LIST = ["SJT", "TT"]
DUTIES_LIST = [1, 2]

SLOTS_PER_DAY = 11
SLOT_COUNT_FOR_DUTIES_PER_DAY = len(SLOTS_LIST)
DAYS_COUNT = len(DAYS_LIST)
BUILDING_COUNT = len(BUILDINGS_LIST)
DUTY_COUNT_PER_BUILDING = len(DUTIES_LIST)

# The number of genes to skip to get to the next values of: 
# - Duty
# - Building in same duty
# - Slot in same building, duty
# - Day in same slot, building, duty
DUTY_INDEX = 1
BLDG_INDEX = DUTY_COUNT_PER_BUILDING
SLOT_INDEX = BLDG_INDEX * BUILDING_COUNT
DAY_INDEX = SLOT_INDEX * SLOT_COUNT_FOR_DUTIES_PER_DAY

# The number of genes under each section
GENES_PER_DUTY = DUTY_COUNT_PER_BUILDING
GENES_PER_BUILDING = GENES_PER_DUTY * BUILDING_COUNT
GENES_PER_SLOT = GENES_PER_BUILDING * SLOT_COUNT_FOR_DUTIES_PER_DAY
GENES_PER_DAY = GENES_PER_SLOT * DAYS_COUNT

POPULATION_SIZE = 8000
GENERATIONS = 40
CHILDREN_MULTIPLIER = 0.4

FIT_RETENTION = 0.3		# Percentage of fit population to be retained
RANDOM_RETENTION = 0.2	# Percentage of random population to be selected

CHROMOSOME_LENGTH = SLOT_COUNT_FOR_DUTIES_PER_DAY * DAYS_COUNT * BUILDING_COUNT * DUTY_COUNT_PER_BUILDING

CHROMOSOME_GENE_DETAILS = []

DATA_FILE = open("coreData.txt")
CORE_DATA = json.loads(DATA_FILE.read())
CORE_LIST = list(dict.keys(CORE_DATA))
CORE_LIST.sort()

# print("# People = ", len(CORE_LIST))
# print(CORE_LIST)

random.shuffle(CORE_LIST)

SINGLE_BREAKS_LIST = {i: None for i in CORE_LIST}

SAME_SLOT_LIST = []
SAME_DAY_LIST = []

MAX_SLOTS_PER_PERSON = {
	"total": 8,
	"daily": 2
}

WEIGHTS = {
	"total": 1,				# Per person
	"daily": 0.4,			# Per person, per day
	"singleBreak": 7.0,		# Per person, per slot
	"doubleBreak": 0.5,
	"venue": 0.5,			# Per person, per slot if class is immediately after duty
	"clash": -5.0,			# Per person, per duty
	"avoidableClash": -5.0,	# With clash. Used if >4 people available but clash happens.
	"dutySD": -6.0,			# Per chromosome
}

POPULATION_ARRAY = []

################################################## Constants ##################################################

################################################## Functions ##################################################

# Function to generate the sameDay and sameSlot lists
def generateSameList():
	i = 0
	while i < CHROMOSOME_LENGTH:
		slots = [j for j in range(i, i + SLOT_INDEX)]
		SAME_SLOT_LIST.append(slots)
		i += BUILDING_COUNT * DUTY_COUNT_PER_BUILDING

	i = 0
	while i < CHROMOSOME_LENGTH:
		d = [j for j in range(i, i + DAY_INDEX)]
		SAME_DAY_LIST.append(d)
		i += BUILDING_COUNT * DUTY_COUNT_PER_BUILDING * SLOTS_PER_DAY

	# pprint(SAME_SLOT_LIST)
	# pprint(SAME_DAY_LIST)

# Function to generate data about the one-hour breaks of each person
def generateSingleBreakData():
	global SINGLE_BREAKS_LIST

	for k in CORE_LIST:
		if k in CORE_DATA:
			tt = CORE_DATA[k]
			breaksFlat = []

			for i in range(DAYS_COUNT):
				for j in range(SLOT_COUNT_FOR_DUTIES_PER_DAY - 1):
					if  tt[i][j] == "" and (((j == 0) or (tt[i][j - 1] != "") and tt[i][j + 1] != "")) and j != 4:
						start = DAY_INDEX*i + SLOT_INDEX*j
						for l in range(DUTY_COUNT_PER_BUILDING * BUILDING_COUNT):
							breaksFlat.append(start + l)

			SINGLE_BREAKS_LIST[k] = breaksFlat			

# Function to find the next class of the person
def findNextClass(day, slot, person):
	if person not in CORE_DATA:
		return [-1, None]
	t = CORE_DATA[person]
	for i in range(slot + 1, SLOTS_PER_DAY, 1):
		if t[day][i] != "":
			return [i, t[day][i]]
	return [-1, None]

# Generates a list of people free in the given day and slot
# TODO make this into a static array to avoid recalculations
def findFree(day, slot):
	peeps = []

	for i in CORE_LIST:
		if i in CORE_DATA and CORE_DATA[i][day][slot] == "":
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
	for i in range(CHROMOSOME_LENGTH):
		day = int(i % GENES_PER_DAY / GENES_PER_SLOT)
		slot = int(i % GENES_PER_SLOT / GENES_PER_BUILDING)
		bldg = int(i % GENES_PER_BUILDING / GENES_PER_DUTY)
		duty = int(i % GENES_PER_DUTY)
		CHROMOSOME_GENE_DETAILS.append((day, slot, bldg, duty))

	# pprint(CHROMOSOME_GENE_DETAILS)	

# Function to return calculated details for day, slot, bldg, duty
def getGeneDetails(n):
	return CHROMOSOME_GENE_DETAILS[n]

# Function to initiate a chromosome
def createEmptyChromosome():
	return {"chromosome": [], "score": 0}

# Function to populate the chromosome
def createChromosomeMaterial():
	# length = DAYS_COUNT * SLOT_COUNT_FOR_DUTIES_PER_DAY * BUILDING_COUNT * DUTY_COUNT_PER_BUILDING

	chromosome = []
	for i in range(CHROMOSOME_LENGTH):
		det = getGeneDetails(i)
		chromosome.append(getPerson(det[0], det[1]))
	
	return chromosome

# Generates the given number of chromosomes for the population
def generatePopulation(count):
	for i in tqdm(range(count), desc="Generating Initial Population"):
		cr = createEmptyChromosome()
		cr["chromosome"] = createChromosomeMaterial()
		POPULATION_ARRAY.append(cr)

# Returns the intersection of two lists
def intersection(l1, l2):
	return list(set(l1) & set(l2))

# Function to calculate the score for clashes in the duty assignment 
# Clarification: places where the same person has multiple duties in the same slot
# Edit: Added condition to do slot clash scoring only if there are more than 4 people free in the slot. This should solve the problem of clashes even though someone else is free.
def slotClashScore(chromosome, person):
	indices = [i for i, x in enumerate(chromosome) if x == person]
	
	score = 0

	for i in SAME_SLOT_LIST:
		# Details for any of the slots in the current sameSlot list.
		det = getGeneDetails(i[0])	
		day = det[0]
		slot = det[1]

		personsFree = getFreePeople(day, slot)
		intersect = intersection(indices, i)

		if len(intersect) > 1 and len(personsFree) >= 4:
			score += WEIGHTS["clash"] * len(intersect)
			score += WEIGHTS["avoidableClash"] * (len(personsFree) - len(intersect))
	
	return score

# Function to calculate score for the maximum daily slots limit
def totalDailyScore(chromosome, person):
	score = 0
	indices = [i for i, x in enumerate(chromosome) if x == person]

	for i in SAME_DAY_LIST:
		intersect = intersection(indices, i)

		if len(intersect) <= MAX_SLOTS_PER_PERSON["daily"]:
			score += WEIGHTS["daily"]
	return score	

# Function to calculate score for the maximum total slots limit
def totalSlotsScore(chromosome, person):
	score = 0
	if chromosome.count(person) <= MAX_SLOTS_PER_PERSON["total"]:
		score += WEIGHTS["total"]
	return score

# Function to calculate score for the assigned venue
def venueScore(chromosome, person):
	score = 0
	indices = [i for i, x in enumerate(chromosome) if x == person]

	for i in indices:
		det = getGeneDetails(i)
		day = det[0]
		slot = det[1]
		bldg = det[2]
		nextDetails = findNextClass(day, slot, person)

		if nextDetails[0] - slot == 1:
			if BUILDINGS_LIST[bldg] == "SJT" and nextDetails[1] == "SJT":
				score += WEIGHTS["venue"]
			elif BUILDINGS_LIST[bldg] == "TT" and nextDetails[1] in ["CDMM", "MB", "GDN", "SMV", "CBMR", "TT"]:
				score += WEIGHTS["venue"]
	return score				

# Function to calculate score for duties assigned in single Breaks
def singleBreakScore(chromosome, person):
	score = 0
	indices = [i for i, x in enumerate(chromosome) if x == person]

	for i in indices:
		if i in SINGLE_BREAKS_LIST[person]:
			score += WEIGHTS["singleBreak"]
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

	for i in CORE_DATA:
		count.append(chromosome.count(i))

	sd = statistics.stdev(count)
	score += sd * WEIGHTS["dutySD"]
	return score

# Function to calculate the total fitness of the chromosome
def calculateScore(chromosome):
	score = 0

	for i in CORE_DATA:
		score += personFitness(chromosome, i)

	score += dutyCountScore(chromosome)

	return score

# Function to calculate the fitness of each chromosome in the population and display details
def calculatePopulationScores():
	maxLen = len(POPULATION_ARRAY)

	for i in tqdm(range(0, maxLen), desc="Calculating Chromosome Fitness Scores"):
		data = POPULATION_ARRAY[i]

		score = calculateScore(data["chromosome"])
		POPULATION_ARRAY[i]["score"] = score

# Function for selection of the population
def selection():
	populationCopy = deepcopy(POPULATION_ARRAY)
	newPopulation = []

	fitCount = int(FIT_RETENTION * len(POPULATION_ARRAY))
	randCount = int(RANDOM_RETENTION * len(POPULATION_ARRAY))

	populationCopy.sort(key=lambda k: k["score"], reverse=True)
	newPopulation = populationCopy[:fitCount]
	
	for i in tqdm(range(randCount), desc="Selecting"):
		newPopulation.append(random.choice(populationCopy))

	return newPopulation	

# Function to crossover two parents in a simple 50-50 fashion.
# TODO Edit to either alternate or do a different crossover mechanism
def crossover(p1, p2):
	chance = random.random()
	crossoverLength = int(0.5 * CHROMOSOME_LENGTH)
	
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
	p1 = random.choice(POPULATION_ARRAY)
	p2 = random.choice(POPULATION_ARRAY)

	child = crossover(p1, p2)

	return child

# Function to mutate a random gene in the chromosome
# TODO add more mutations?
def mutation(item):
	geneNumber = int(random.random() * CHROMOSOME_LENGTH)
	det = getGeneDetails(geneNumber)

	item["chromosome"][geneNumber] = getPerson(det[0], det[1])
	item["score"] = calculateScore(item["chromosome"])

	return item

# Function to select a random chromosome to mutate
# Calls the mutation(...) function
def doMutation():
	global POPULATION_ARRAY

	item = int(random.random() * len(POPULATION_ARRAY))
	POPULATION_ARRAY[item] = mutation(POPULATION_ARRAY[item])

# Function to proceed through a generation
# Selection
# Reproduction
# Mutation of each child
def generation():
	global POPULATION_ARRAY

	print('Proceeding through generation...')

	selected = selection()
	if not len(selected) > 0:	# No selections made
		return

	children = []
	childrenCount = int(CHILDREN_MULTIPLIER * len(selected))

	for i in tqdm(range(childrenCount), desc="Reproducing and Mutating"):
		child = mutation(doCrossover())
		children.append(child)
	newPopulation = selected + children

	if not len(newPopulation) > 0:	# New population is empty
		return

	POPULATION_ARRAY = newPopulation

# Function to control the GA
# Generates population and runs through the defined generations
def algorithm():
	generatePopulation(POPULATION_SIZE)

	print("\n\nGENERATION #0")
	calculatePopulationScores()

	print("Population Length = ", len(POPULATION_ARRAY))
	findAverage()
	findFittest()	

	for i in range(1, GENERATIONS):
		random.shuffle(CORE_LIST)
		print("\nGENERATION #", i)
		
		generation()
		calculatePopulationScores()
		print("Population Length = ", len(POPULATION_ARRAY))

		findAverage()
		findFittest()	

	print("\n\nFinally, ")
	findAverage()
	fittest = findFittest()["chromosome"]
	print("Duty Count Score = %s" % (dutyCountScore(fittest)))
	
	CORE_LIST.sort()
	print("\n\nProper: ")
	printProperly(fittest)

	print("\nIndividual Scores: ")
	printIndividualScores(fittest)

# Function to print the score split up of each person
def printIndividualScores(chromosome):
	print("Person\t\tCount\tDaily\tTotal\tClash\tVenue\tSingle\tSnglBrk")
	for i in CORE_LIST:
		count = chromosome.count(i)
		daily = round(totalDailyScore(chromosome, i) / WEIGHTS["daily"], 2)
		total = round(totalSlotsScore(chromosome, i) / WEIGHTS["total"], 2)
		clash = round(slotClashScore(chromosome, i) / WEIGHTS["clash"], 2)
		venue = round(venueScore(chromosome, i) / WEIGHTS["venue"], 2)
		single = round(singleBreakScore(chromosome, i) / WEIGHTS["singleBreak"], 2)
		brk = SINGLE_BREAKS_LIST[i]
		

		if len(i) < 8:
			print("%s\t\t%s\t%s\t%s\t%s\t%s\t%s\t" % (i, count, daily, total, clash, venue, single), brk)
		else:
			print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t" % (i, count, daily, total, clash, venue, single), brk)

# Function to find the average score of the population and print it			 
def findAverage():
	total = 0
	for i in POPULATION_ARRAY:
		total += i["score"]
	avg = total / len(POPULATION_ARRAY)

	print("Average Score = ", avg)	

# Function to find the fittest chromosome in the population
def findFittest():
	POPULATION_ARRAY.sort(key=lambda k: k["score"], reverse=True)

	print("Fittest Score = ", POPULATION_ARRAY[0]["score"])
	return POPULATION_ARRAY[0]

# Function to print the chromosome in human-readable format
def printProperly(chromosome):
	duties = {}
	for i in DAYS_LIST:
		duties[i] = {}
		for j in SLOTS_LIST:
			duties[i][j] = {}
			for k in BUILDINGS_LIST:
				duties[i][j][k] = []
				for l in range(2):
					duties[i][j][k].append("")

	for i in range(CHROMOSOME_LENGTH):
		det = getGeneDetails(i)
		duties[DAYS_LIST[det[0]]][SLOTS_LIST[det[1]]][BUILDINGS_LIST[det[2]]][det[3]] = chromosome[i]

	pprint(duties, width=160)	

################################################## Functions ##################################################

################################################## Run ##################################################

generateSameList()
generateSingleBreakData()
generateDetails()
algorithm()

################################################## Run ##################################################

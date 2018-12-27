import numpy
from pprint import pprint
import random, re, json

################################################## Doodling ##################################################

"""
Chromosome:
						Slots
______________________________________________________
					People Assigned
______________________________________________________

"""

################################################## Doodling ##################################################


################################################## Constants ##################################################

slotsPerDay = 11
dutySlotsPerDay = 8
dayCount = 5
buildings = 2
dutiesPerBuilding = 2

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
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
highest = []
population = []
fit = []

################################################## Constants ##################################################

################################################## Functions ##################################################

def getPerson():
	return random.choice(core)

def createChromosome():
	length = dayCount * dutySlotsPerDay * buildings * dutiesPerBuilding

	chromosome = []
	for i in range(length):
		chromosome.append(getPerson())
	
	return chromosome

def calculateScore(chromosome):
	score = 0

	dutyIndex = dutiesPerBuilding
	bldgIndex = dutyIndex * buildings
	slotIndex = bldgIndex * dutySlotsPerDay
	dayIndex = slotIndex * dayCount

	for i in range(len(chromosome)):
		day = int((i % dayIndex) / slotIndex)
		slot = (int(i % slotIndex / bldgIndex))
		bldg = (int(i % bldgIndex / dutyIndex))
		duty = (int(i % dutyIndex))

		# print(i, chromosome[i])
		# print(day, slot, bldg, duty)
		# print(day+1, slot+1, bldg+1, duty+1)

		if chromosome[i] in coreData and coreData[chromosome[i]][day][slot] == "":
			score += points["free"]

	return score


################################################## Functions ##################################################

################################################## Run ##################################################

chrom = createChromosome()
score = calculateScore(chrom)
print(score)

################################################## Run ##################################################

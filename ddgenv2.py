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
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
seniorCore = ['Atul', 'Ayush', 'Charu', 'Kabiir', 'Krityaan', 'Manisha', 'Namit', 'Pavithra', 'Rishab', 'Saksham', 'Sakshi', 'Sarthak', 'Saurav', 'Simran', 'Sonal']
juniorCore = ['Aban', 'Aradhita', 'Bhavishya', 'Chinmay', 'David', 'Devam', 'Fardeen', 'Gauri', 'Kuhoo', 'Lakshay', 'Manan', 'Prajeeth', 'Rama', 'Rishit', 'Rohan', 'Ruchica', 
			'Sanjana', 'SauravH', 'Siddharth', 'Suranjan', 'Taarussh', 'Tajendar', 'Tanya', 'Thiru', 'Vaishnavi']

core = ['Atul', 'Ayush', 'Charu', 'Kabiir', 'Krityaan', 'Manisha', 'Namit', 'Pavithra', 'Rishab', 'Saksham', 'Sakshi', 'Sarthak', 'Saurav', 'Simran', 'Sonal',
		'Aban', 'Aradhita', 'Bhavishya', 'Chinmay', 'David', 'Devam', 'Fardeen', 'Gauri', 'Kuhoo', 'Lakshay', 'Manan', 'Prajeeth', 'Rishit', 'Rohan', 'Ruchica', 
		'Sanjana', 'SauravH', 'Siddharth', 'Suranjan', 'Taarussh', 'Tajendar', 'Tanya', 'Thiru', 'Vaishnavi']

srData = open("srCoreData.txt")
seniorCoreData = json.loads(srData.read())

singleBreaks = {i: None for i in core}

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

def generateDuty(peeps=None, duty=None):
	x=1

################################################## Functions ##################################################

################################################## Run ##################################################



################################################## Run ##################################################

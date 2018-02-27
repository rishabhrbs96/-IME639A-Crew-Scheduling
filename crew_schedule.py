#!/usr/bin/python
# Python code to solve the famous Crew Pairing Problem
# @author: Md Tabish Haque  "tabish@iitk.ac.in"
# @author: Rishabh Bhardwaj "brishabh@iitk.ac.in"
from __future__ import division			#For floating divisions in python 2.7

# CPLEX packages
import cplex							# IMB CPLEX

# Global variables
global trips, cities, base_cities


def is_overlap(a1, a2, b1, b2):
	"""
	Functin to check if two intervals overlap or not
	@param: a1,a2,b1,b2 : start and end times of the two intervals respsctively
	"""
	if(a1<b1 and a2<b2 and a2<b1):
		return False
	elif(a1>b1 and a2>b2 and b2<a1):
		return False
	elif(a1<b1 and a2>b2 and b2<b1):
		return False
	elif(b1<a1 and b2>a2 and a2<a1):
		return False
	return True

def read_input_data():
	"""
	Function to load data from input.txt file to global variables
	@param: void
	@return: void
	"""
	global trips, cities, base_cities
	trips = {}

	with open("input.txt") as fp:
		lines = fp.readlines()
	line_list = [ro.strip() for ro in lines]

	num_cities = int(line_list[0].split("=")[-1])
	cities = range(1,num_cities+1)
	num_base = int(line_list[1].split("=")[-1])
	
	base_cities = [int(x) for x in line_list[3].split(",")]

	num_trips = int(line_list[4].split("=")[-1])

	for i in xrange(1,num_trips+1):
		temp = line_list[5 + i].split(",")
		trips[i] = {'Start':int(temp[2]), 'End':int(temp[3]), 'Source':int(temp[0]), 'Destination':int(temp[1])}


def can_combine_duties(duties, x, y):
	"""
	Functn to check if we can add two duties x and y to form a pairing
	"""
	if(is_overlap(trips[duties[x][0]]['Start'],trips[duties[x][-1]]['End'],trips[duties[y][0]]['Start'],trips[duties[y][-1]]['End']) is True):
		return False
	if((trips[duties[x][0]]['Source'] == trips[duties[y][-1]]['Destination']) and (trips[duties[y][0]]['Source'] == trips[duties[x][-1]]['Destination'])):# and (abs(trips[duties[y][-1]]['End'] - trips[duties[x][0]]['Start']) <= 8)):
		if((trips[duties[y][0]]['Start'] - trips[duties[x][-1]]['End'] + 24) % 24 >= 1):
			return True
		else:
			return False
	else:
		return False


def can_add_duties(x, y):
	"""
	Functn to check if we can add two duties x and y to get anoter duty of larger length
	"""
	if(is_overlap(trips[x[0]]['Start'],trips[x[-1]]['End'],trips[y[0]]['Start'],trips[y[-1]]['End']) is True):
		return False
	for i in trips:
		if(i in x and i in y):
			return False
	if((trips[x[-1]]['Destination'] == trips[y[0]]['Source']) and ((trips[y[0]]['Start'] - trips[x[-1]]['End']) >= 1)):
		if((trips[y[-1]]['End'] - trips[x[0]]['Start'] + 24) %24 <= 8):
			return True
		else:
			return False
	else:
		return False


if __name__ == "__main__":
	global trips, cities, base_cities

	read_input_data()
	
	duties = {}
	pairings = []
	base_duties = []				# this will store all duties which consists of only one trip
	
	# constructing the base duties
	for i in trips:
		duties[i] = [i]
		base_duties.append([i])

	k = len(duties) + 1

	# we will try to combine each base duty to the lsit of duty of lengths n to create a new list
	# of duties of length n+1. At any step, new_duties will store duties of length n. length of a
	# duty means number of trips it is conposed of
	new_duties = base_duties
	while(len(new_duties) != 0):	# repeat till we cannot construct any more nre duty
		add_duties = []				# duties whic will be added after this step
		for i in new_duties:
			for j in base_duties:
				if(can_add_duties(i, j)):
					add_duties.append(i + j)
		for i in add_duties:
			duties[k] = i
			k = k + 1
		new_duties = add_duties
	

	print "All possible duties are"
	for i in duties:
		print i, duties[i]

	# constructing all possible pairings of two duties
	k = 1
	for i in xrange(1,len(duties)+1):
		if(trips[duties[i][0]]['Source'] in base_cities):
			for j in xrange(1,len(duties)+1):		
				if(can_combine_duties(duties, i, j) and i != j):
					pairings.append([i,j])
					k = k + 1
	
	# there will be some pairings which will be duplicate. The set duplicate_index will store the
	# index of duplicate pairings. temp will store the list of all trips in a pairing
	temp = {}
	for i in xrange(len(pairings)):
		t2 = []
		for j in pairings[i]:
			for k in duties[j]:
				t2.append(k)
		temp[i] = t2
	
	duplicate_index = set()
	for i in temp:
		for j in temp:
			if(i < j and temp[i] == temp[j]):
				duplicate_index.add(j)

	for i in sorted(duplicate_index, reverse=True):
		pairings.pop(i)		# removing duplicate pairings
	
	# code to calculate cost of a paiting
	# cost = time which a crew will spend outsinde the base
	costs = []
	for p in xrange(len(pairings)):
		cost = (trips[duties[pairings[p][-1]][-1]]['End'] - trips[duties[pairings[p][0]][0]]['Start'] + 24 ) % 24
		costs.append(cost)

	print "All possible pairings with costs are"
	for i in xrange(len(pairings)):
		print i,pairings[i],costs[i]
		
	num_decision_vars = len(pairings)
	num_constraints = len(trips)
	my_obj = costs
	my_ub = [1.0]*num_decision_vars
	my_lb = [0.0]*num_decision_vars
	my_rhs = [1.0]*num_constraints
	my_sense = ["E"]*num_constraints

	my_colnames = []
	for i in xrange(num_decision_vars):
		my_colnames.append("y" + str(i))
	
	my_rownames = []
	for i in xrange(num_constraints):
		my_rownames.append("r" + str(i))

	master = cplex.Cplex()
	master.objective.set_sense(master.objective.sense.minimize)
	master.variables.add(obj=my_obj, ub=my_ub, lb=my_lb, names = my_colnames)

	my_constraints = []
	my_constraints_coeff = []
	for i in xrange(num_constraints):
		my_constraints_coeff.append([0.0]*num_decision_vars)

	for i in xrange(num_decision_vars):
		for j in pairings[i]:
			for k in duties[j]:
				my_constraints_coeff[k-1][i] = 1.0
	
	for i in xrange(len(my_constraints_coeff)):
		my_constraints.append([my_colnames, my_constraints_coeff[i]])

	master.linear_constraints.add(lin_expr = my_constraints,rhs = my_rhs, names = my_rownames, senses=my_sense)

	for i in xrange(num_decision_vars):
		master.variables.set_types(i,master.variables.type.integer)
	try:
		fo = open("output.txt","w")
		master.solve()
		numcols = master.variables.get_num()
		x = master.solution.get_values()
		cnt = 0
		for j in range(numcols):
			if(x[j] > 0.0):
				cnt = cnt + 1
		fo.write("OPTIMAL SOLUTION COST = " + str(master.solution.get_objective_value()) + "\n")
		fo.write("NUMBER OF CREW SCHEDULES = "+ str(cnt) + "\n\n")
		cnt = 1
		for j in range(numcols):
			if(x[j] > 0.0):
				fo.write("CREW SCHEDULE "+ str(cnt) + "\n")
				fo.write("The following trips will be paired together in schedule " + str(cnt) + "\n")
				for i in pairings[j]:
					for k in duties[i]:
						fo.write("\tTrip: " + str(k) + "\n")
						fo.write("\t\tSource City: " + str(trips[k]['Source']) + "\n")
						fo.write("\t\tDeparture Time from source(in hrs): " + str(trips[k]['Start']) + "\n")
						fo.write("\t\tDestination City: " + str(trips[k]['Destination']) + "\n")
						fo.write("\t\tArrival Time at Destination(in hrs): " + str(trips[k]['End']) + "\n\n")
				cnt = cnt + 1
		print "Solution printed in output.txt"
		fo.close()
	except Exception as e:
		print "Fesiable solution doesn't exist"
		print e
#--------------------------------------------------------------------------------
# Pegboard Problem
# JL Popyack, March 2022
#
# This is a skeleton program for a production system that defines a Pegboard
# Problem for potential solution by a search strategy.  The program accepts 
# command-line inputs for the number of rows and columns, which define a
# rectangular area in which the problem is to be solved:
#
#    python3 pegboard_base.py BOARD_ROWS BOARD_COLS
#
#  sets the size of the grid, e.g.,  
#
#    python3 pegboard_base.py 4 4
# 
# This program contains partial definitions of State and Rule classes, which need
# to be completed.  To demonstrate that the classes work properly, the student 
# should implement a "flailing" strategy that begins with the problem in an 
# initial state and continues applying applicable moves until there are none
# remaining.  It is not necessary to try to solve the problem with an intelligent
# search strategy for this assignment.
#--------------------------------------------------------------------------------

import time
import sys
import copy


#============================================================================
# get_arg() returns command line arguments.
#============================================================================
def get_arg(index, default=1):
	'''Returns the command-line argument, or the default if not provided'''
	return sys.argv[index] if len(sys.argv) > index else default


import random

#-----------------------------------------------------------------
# These provide some LISP-like functionality.
#-----------------------------------------------------------------

def first(list):
    return list[0]

def rest(list):
    return list[1:]

def member(x,L):
	return x in L


#-----------------------------------------------------------------
# Global variables, set at startup
#-----------------------------------------------------------------
BOARD_ROWS = 4 
BOARD_COLS = 4
depthBound = 50
backTrackCt = 0
failed1Ct = 0
failed2Ct = 0
failed3Ct = 0
failed4Ct = 0
failed5Ct = 0

numMatrix = []
val = (BOARD_ROWS*BOARD_COLS)-1

for i in range(BOARD_ROWS):
	col = []
	for j in range(BOARD_COLS):
		col.append(val)
		val -= 1
	numMatrix.append(col)


def createMatrix(num):
	matrix = list()
	binstr = format(num, "b")
	if(len(binstr) < 16):
		addZero = 16 - len(binstr)
		binstr = ('0'*addZero)+ binstr
	matrix=[list(binstr[i:i + BOARD_COLS]) for i in range(0, len(binstr), BOARD_COLS)]
	return matrix

#--------------------------------------------------------------------------------
class State:

	#----------------------------------------------------------------------------
	# State: 
	#----------------------------------------------------------------------------
	# The state of the problem is a positive number whose binary representation
	# consists of a 1 for each peg.  The pegs are numbered from the right, i.e., 
	#     FEDC BA98 7654 3210
	# corresponding to the grid 
	#     F E D C 
	#     B A 9 8
	#     7 6 5 4
	#     3 2 1 0
	# for a problem with 4 rows and 4 columns, so that the number 
	#     1011 0010 1011 1111  (with decimal value 45759) 
	# represents this configuration:
	#     X . X X 
	#     . . X .
	#     X . X X
	#     X X X X 
	#----------------------------------------------------------------------------
	# uses global constants BOARD_ROWS, BOARD_COLS, GOAL_STATE
	#----------------------------------------------------------------------------

	
	def __init__(self, number):
	#-----------------------------------------------------------------
	# Creates a state with the given numeric value.
	#-----------------------------------------------------------------
	
		self.ROWS = BOARD_ROWS
		self.COLS = BOARD_COLS
		self.numeric = number
		self.matrix = createMatrix(self.numeric)


	def __str__ (self):
	#-----------------------------------------------------------------
	# returns a string containing the partially filled in grid 
	# corresponding to state.
	#-----------------------------------------------------------------
		outstr = format(self.numeric, "b")
		return outstr


	def applicableRules(self, board, verbose = False):
	#-----------------------------------------------------------------
	# Find all applicable rules for a given state.
	# Note that the set of all possible rules can be determined from
	# the number of rows and columns, and this function can check the 
	# precondition for each rule with the given state.  
	#-----------------------------------------------------------------
		
		
		result = []
		m = 0
		while m < BOARD_ROWS:
			n = 0
			while n < BOARD_COLS:
				if(board[m][n] == '1'):
					if(m-1 >= 0 and n-1 >=0):
						if(m-2 >= 0 and n-2 >=0):
							rule = Rule([numMatrix[m][n], numMatrix[m-1][n-1], numMatrix[m-2][n-2]])
							if rule.precondition(self):
								result.append([numMatrix[m][n], numMatrix[m-1][n-1], numMatrix[m-2][n-2]])
					if(m-1 >=0):
						if(m-2 >= 0):
							rule = Rule([numMatrix[m][n], numMatrix[m-1][n], numMatrix[m-2][n]])
							if rule.precondition(self):
								result.append([numMatrix[m][n], numMatrix[m-1][n], numMatrix[m-2][n]])
					if(m-1>=0 and n+1 < BOARD_COLS):
						if(m-2 >= 0 and n+2 < BOARD_COLS):
							rule = Rule([numMatrix[m][n], numMatrix[m-1][n+1], numMatrix[m-2][n+2]])
							if rule.precondition(self):
								result.append([numMatrix[m][n], numMatrix[m-1][n+1], numMatrix[m-2][n+2]])
					if(n-1 >= 0):
						if(n-2 >= 0):
							rule = Rule([numMatrix[m][n], numMatrix[m][n-1], numMatrix[m][n-2]])
							if rule.precondition(self):
								result.append([numMatrix[m][n], numMatrix[m][n-1], numMatrix[m][n-2]])
					if(n+1 < BOARD_COLS):
						if(n+2 < BOARD_COLS):
							rule = Rule([numMatrix[m][n], numMatrix[m][n+1], numMatrix[m][n+2]])
							if rule.precondition(self):
								result.append([numMatrix[m][n], numMatrix[m][n+1], numMatrix[m][n+2]])
					if(m+1 < BOARD_ROWS and n-1>=0):
						if(m+2 < BOARD_ROWS and n-2 >=0):
							rule = Rule([numMatrix[m][n], numMatrix[m+1][n-1], numMatrix[m+2][n-2]])
							if rule.precondition(self):
								result.append([numMatrix[m][n], numMatrix[m+1][n-1], numMatrix[m+2][n-2]])
					if(m+1 < BOARD_ROWS):
						if(m+2 < BOARD_ROWS):
							rule = Rule([numMatrix[m][n], numMatrix[m+1][n], numMatrix[m+2][n]])
							if rule.precondition(self):
								result.append([numMatrix[m][n], numMatrix[m+1][n], numMatrix[m+2][n]])
					if(m+1 < BOARD_ROWS and n+1 < BOARD_COLS):
						if(m+2 < BOARD_ROWS and n+2 < BOARD_COLS):
							rule = Rule([numMatrix[m][n], numMatrix[m+1][n+1], numMatrix[m+2][n+2]])
							if rule.precondition(self):
								result.append([numMatrix[m][n], numMatrix[m+1][n+1], numMatrix[m+2][n+2]])
				
				n+=1
			m+=1	
		return result


	def goal(self):
	#-----------------------------------------------------------------
	# Returns True if state equals a given GOAL_STATE, e.g., the state 
	# with exactly 1 peg, in position 9.
	#-----------------------------------------------------------------
		return self.numeric == GOAL_STATE.numeric


#--------------------------------------------------------------------------------
class Rule:

	#----------------------------------------------------------------------------
	# Rule: 
	#----------------------------------------------------------------------------
	# A rule r can be characterized by the attributes (jumper, goner, newpos), 
	# which respectively refer to the position of a peg that is about to jump 
	# (jumper), the position of the peg it jumps over (goner), and the new 
	# position of the jumper (newpos).
	# 
	# The rule is defined by the following action and preconditions:
	#   Action:??change values in state s of jumper position to 0, 
	#           goner position to 0, and newpos position to 1.
	#   Precondition: values of jumper, goner, newpos positions are respectively   
	#                 1, 1, and 0.
	#----------------------------------------------------------------------------


	def __init__(self, moveVector):
		self.moveVector = moveVector
		self.jumper = moveVector[0]
		self.goner  = moveVector[1]
		self.newpos = moveVector[2]


	def __eq__(self, r):
		return (self.moveVector == r.moveVector)
		
		
	def __str__(self):
	#-----------------------------------------------------------------
	# returns a string describing the rule to be applied
	#-----------------------------------------------------------------
		description = "Peg in slot "+str(self.jumper)+" jumps over the peg in slot "+str(self.goner)+" and lands in slot "+str(self.newpos)
		
		return description


	def applyRule(self,state, verbose):
	#-----------------------------------------------------------------
	# Returns a new state formed by applying rule to state.
	#-----------------------------------------------------------------
		board = createMatrix(state.numeric)
		m = 0
		initial = []
		final = []
		over = []
		while m < BOARD_ROWS:
			n = 0
			while n < BOARD_COLS:
				if(numMatrix[m][n] == self.jumper):
					initial.append(m)
					initial.append(n)
					n+=1
				elif(numMatrix[m][n] == self.goner):
					over.append(m)
					over.append(n)
					n+=1
				elif(numMatrix[m][n] == self.newpos):
					final.append(m)
					final.append(n)
					n+=1
				else:
					n+=1
			m+=1
		board[initial[0]][initial[1]] = '0'
		board[over[0]][over[1]] = '0'
		board[final[0]][final[1]] = '1'
		newState =state.numeric - ( 2**self.jumper + 2**self.goner - 2**self.newpos )
		return State(newState)


	def precondition(self,state):
	#-----------------------------------------------------------------
	# Returns True if the given Rule may be applied to state.
	# One way to do this is to make use of the binary representation,
	# and Python binary operators.
	#-----------------------------------------------------------------
		m = 0
		initial = []
		final = []
		over = []
		while m < BOARD_ROWS:
			n = 0
			while n < BOARD_COLS:
				if(numMatrix[m][n] == self.jumper):
					initial.append(m)
					initial.append(n)
					n+=1
				elif(numMatrix[m][n] == self.goner):
					over.append(m)
					over.append(n)
					n+=1
				elif(numMatrix[m][n] == self.newpos):
					final.append(m)
					final.append(n)
					n+=1
				else:
					n+=1
			m+=1
		if(state.matrix[initial[0]][initial[1]] == '1' and state.matrix[over[0]][over[1]] == '1' and state.matrix[final[0]][final[1]] == '0'):
			return True
		else:
			return False


#--------------------------------------------------------------------------------
path1 = []

def deadEnd(state):
	return False

def backTrack(stateList, verbose):
	global backTrackCt
	global failed1Ct, failed2Ct, failed3Ct, failed4Ct, failed5Ct
	backTrackCt += 1
	state = first(stateList)
	if state in rest(stateList):
		if verbose:
			failed1Ct += 1
			print("FAILED-1 State Cycle Detected")
		return "FAILED-1"
	if deadEnd(state):
		if verbose:
			failed2Ct += 1
			print("FAILED-2 Reached Dead End")
		return "FAILED-2"
	if state.goal():
		print("Goal Reached")     
		return None
	if len(stateList) > depthBound:
		if verbose:
			failed3Ct += 1
			print("FAILED-3 Depth Limit Exceeded")
		return "FAILED-3"
	ruleset = state.applicableRules(state.matrix, verbose)
	'''ruleLenList = []
	for rule in ruleset:
		rule = Rule(rule)
		tempState = rule.applyRule(state, verbose)
		tempRuleset = tempState.applicableRules(tempState.matrix, verbose)
		ruleLen = len(tempRuleset)
		ruleLenList.append(ruleLen)
	zip_list = list(zip(ruleset, ruleLenList))
	zip_list1 = []
	if zip_list != []:
		zip_list1.append(zip_list)
	print(zip_list1)
	#ruleset = sorted(zip_list, key = lambda x: x[1] )
	#print(ruleset)

	
	#print(ruleLenList)'''

	if verbose:
		print(ruleset)
	if len(ruleset) == 0:
		if verbose:
			failed4Ct += 1
			print("FAILED-4 No Applicable Rules Found")
		return "FAILED-4"
	
	for rule in ruleset:
		rule = Rule(rule)
		if verbose:
			print("Trying rule:", rule)
		newState = rule.applyRule(state, False)
		if verbose:
			print(newState.numeric)
			print("Pegboard", newState.matrix)
		newStateList = copy.deepcopy(stateList)
		newStateList.insert(0, newState)
		path = backTrack(newStateList, verbose)
		if path is None:
			path1.append(rule)
			return path
	failed5Ct += 1
	if verbose:
		print("FAILED-5")
	return "FAILED-5"
#--------------------------------------------------------------------------------
#  MAIN PROGRAM
#--------------------------------------------------------------------------------

start_time = time.time()
if __name__ == "__main__":
#--------------------------------------------------------------------------------
#    python3 pegboard_base.py BOARD_ROWS BOARD_COLS
#
#  	 sets the size of the grid, e.g., 
#    python3 pegboard_base.py 4 4
#--------------------------------------------------------------------------------

	BOARD_ROWS = int(get_arg(1))
	BOARD_COLS = int(get_arg(2))
	VERBOSE = str(get_arg(3))

	if VERBOSE == "verbose" :
		verboseFlag = True
	else:
		verboseFlag = False
		
	#-----------------------------------------------------------------
	# Create numeric peg values peg[i] = 2^i, for each peg position in 
	# the board.  If a state contains a peg in position i, the value of 
	# peg[i] is added to the empty state.
	#-----------------------------------------------------------------
	peg = []
	pegboard = []
	result = []
	pegValue = 1
	FULL_BOARD = 0
	
	for i in range(BOARD_ROWS*BOARD_COLS):
		peg.append(pegValue)
		FULL_BOARD += pegValue
		pegValue += pegValue
		#print("peg[%d] = %d" %(i,peg[i]))
		
	print("\nFULL_BOARD = %d" %FULL_BOARD)

	GOAL_STATE = peg[9]
	print("\nGOAL_STATE = %s" %GOAL_STATE)
	GOAL_STATE = State(GOAL_STATE)
	
	stateList = []
	#initialState = FULL_BOARD - ( peg[6]+peg[8]+peg[10]+peg[11]+peg[14] )
	initialState = FULL_BOARD - ( peg[9] )
	#initialState = FULL_BOARD - ( peg[2]+peg[15]+peg[7]+peg[4] )
	#print("\ninitialState = %s" %initialState)
	initialState = State(initialState)
	print("Initial State:", initialState.numeric)
	pegboard = createMatrix(initialState.numeric)
	print("pegboard:", pegboard)
	stateList.append(initialState)
	result = backTrack(stateList, verboseFlag)
	print("Final solution path:")
	for r in path1[::-1]:
		print(r)
	print("Total number of calls to backTrack():", backTrackCt)
	print("Total number of FAILED-1 condition:", failed1Ct)
	print("Total number of FAILED-2 condition:", failed2Ct)
	print("Total number of FAILED-3 condition:", failed3Ct)
	print("Total number of FAILED-4 condition:", failed4Ct)
	print("Total number of FAILED-5 condition", failed5Ct)
	print("--- %s seconds ---" % (time.time() - start_time))

	
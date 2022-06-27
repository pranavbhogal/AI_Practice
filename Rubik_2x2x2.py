from doctest import IGNORE_EXCEPTION_DETAIL
import random
import copy
import sys, getopt
import time
import queue

def get_arg(index, default=None):
#============================================================================
# Returns command line arguments.
#============================================================================
	'''Returns the command-line argument, or the default if not provided'''
	return sys.argv[index] if len(sys.argv) > index else default

def getConfiguration():
#============================================================================
# Returns configuration read from command line.
#   python3 <this program>.py -c arg -m arg -v
#
# -c, --config:
#	Specifies initial state.
#	  If given as a string, can be either in terse or reader-friendly mode, 
#	    e.g., "WOWOBBBBRWRWYRYRGGGGYOYO" or "WOWO BBBB RWRW YRYR GGGG YOYO"
#	  If given as a non-negative integer, specifies the number of random
#	    legal moves to apply to the goal state to produce initial state.
#
# -m, --method:
#	Specifies solution method to use.
#	Choices are:
#	  "b","breadth"     : specifying BREADTH_FIRST
#	  "d","depth"       : specifying IT_DEPTH_FIRST (Iterative Deepening Depth-First)
#	  "a","best"        : specifying BEST_FIRST
#	  "i","idbacktrack" : specifying IT_BACKTRACK (Iterative Deepening Backtrack)
#	  "o","other"       : user preference
#	  n>=0               : specifying DEPTH_FIRST with MAX_DEPTH=n
#
# -v, --verbose:
#  Indicates VERBOSE mode for detailed algorithm tracing 
#
# Examples:
#
# > python3 Rubik_2x2x2.py -c 3
# initialState=YWYW RRBG BGOO WWYY OOBG BGRR 
# method=DEPTH_FIRST, with MAX_DEPTH=1
# Non-Verbose mode.
# 
# > python3 Rubik_2x2x2.py -c 3 -m b
# initialState=OOYY OWOW GGGG WWRR YRYR BBBB 
# method=BREADTH_FIRST
# Non-Verbose mode.
# 
# > python3 Rubik_2x2x2.py -c 3 -m a -v
# initialState=WOWO BBBB RWRW YRYR GGGG YOYO 
# method=BEST_FIRST
# Verbose mode.
# 
# > python3 Rubik_2x2x2.py -c 3 -m i
# initialState=WWWW GGOO OOBB YYYY BBRR RRGG 
# method=IT_BACKTRACK
# Non-Verbose mode.
# 
# > python3 Rubik_2x2x2.py --config="WOWO BBBB RWRW YRYR GGGG YOYO" --method=depth 
# initialState=WOWO BBBB RWRW YRYR GGGG YOYO 
# method=IT_DEPTH_FIRST
# Non-Verbose mode.
# 
# > python3 Rubik_2x2x2.py --config="WOWO BBBB RWRW YRYR GGGG YOYO" --method=7 --verbose
# initialState=WOWO BBBB RWRW YRYR GGGG YOYO 
# method=DEPTH_FIRST, with MAX_DEPTH=7
# Verbose mode.
# 
#============================================================================
	METHOD = { }
	METHOD.update(dict.fromkeys(["b","breadth"], "BREADTH_FIRST"))
	METHOD.update(dict.fromkeys(["d","depth"  ], "IT_DEPTH_FIRST"))
	METHOD.update(dict.fromkeys(["a","best"   ], "B ST"))
	METHOD.update(dict.fromkeys(["i","idbacktrack"], "IT_BACKTRACK"))
	METHOD.update(dict.fromkeys(["o","other"], "OTHER"))

	method = "DEPTH_FIRST"   # default method
	MAX_DEPTH = 1            # default maximum depth
	VERBOSE = False
	commandLineErrors = False
			  
	goalState = Cube()  # by default, Cube() is the goal state
	
	opts, args= getopt.getopt(sys.argv[1:],"c:m:v",["config=","method=","verbose"])
	for opt, arg in opts:
		if opt in ("-c", "--config"):
			#==============================================================
			# initialState will either be the given string, or
			# an integer specifying a random state n moves away from
			# the goal state
			#==============================================================
			initialState = arg
			if len(arg) < len(goalState.tiles): 
				#==============================================================
				# If the argument is not a string sufficiently long to be an
				# initial state, it is assumed to be a non-negative integer.
				#==============================================================
				NUM_STEPS = int(arg)
				initialState = goalState.shuffle(NUM_STEPS)
			else:
				initialState = Cube(arg)
			
		elif opt in ("-m", "--method"):
			#==============================================================
			# Solution method will either be
			#  BREADTH_FIRST, IT_DEPTH_FIRST, BEST_FIRST, IT_DEEP_BACKTRACK, 
			# or an integer, specifying DEPTH_FIRST (i.e., not Iterative 
			# Depth-First Search), with a fixed depth of that value.
			#==============================================================
			if arg in METHOD.keys():
				method = METHOD[arg]
			else:
				MAX_DEPTH = int(arg)  
				
		elif opt in ("-v", "--verbose"):
			VERBOSE = True
			
		else:
			print("Unknown option, " + opt + " " +  str(arg) )
			commandLineErrors = True
			
	if commandLineErrors:
		sys.exit()
		 
	return initialState, method, MAX_DEPTH, VERBOSE



#--------------------------------------------------------------------------------


#============================================================================
# List of possible moves
# https://ruwix.com/online-puzzle-simulators/2x2x2-pocket-cube-simulator.php
#
# Each move permutes the tiles in the current state to produce the new state
#============================================================================

RULES = {
	"U" : [ 2,  0,  3,  1,   20, 21,  6,  7,    4,  5, 10, 11, 
	       12, 13, 14, 15,    8,  9, 18, 19,   16, 17, 22, 23],
	"U'": [ 1,  3,  0,  2,    8,  9,  6,  7,   16, 17, 10, 11, 
	       12, 13, 14, 15,   20, 21, 18, 19,    4,  5, 22, 23],
	"R":  [ 0,  9,  2, 11,    6,  4,  7,  5,    8, 13, 10, 15, 
	       12, 22, 14, 20,   16, 17, 18, 19,    3, 21,  1, 23],
	"R'": [ 0, 22,  2, 20,    5,  7,  4,  6,    8,  1, 10,  3, 
	       12, 9, 14, 11,    16, 17, 18, 19,   15, 21, 13, 23],
	"F":  [ 0,  1, 19, 17,    2,  5,  3,  7,   10,  8, 11,  9, 
	        6,  4, 14, 15,   16, 12, 18, 13,   20, 21, 22, 23],
	"F'": [ 0,  1,  4,  6,   13,  5, 12,  7,    9, 11,  8, 10, 
	       17, 19, 14, 15,   16,  3, 18,  2,   20, 21, 22, 23],
	"D":  [ 0,  1,  2,  3,    4,  5, 10, 11,    8,  9, 18, 19, 
	       14, 12, 15, 13,   16, 17, 22, 23,   20, 21,  6,  7],
	"D'": [ 0,  1,  2,  3,    4,  5, 22, 23,    8,  9,  6,  7, 
	       13, 15, 12, 14,   16, 17, 10, 11,   20, 21, 18, 19],
	"L":  [23,  1, 21,  3,    4,  5,  6,  7,    0,  9,  2, 11, 
	        8, 13, 10, 15,   18, 16, 19, 17,   20, 14, 22, 12],
	"L'": [ 8,  1, 10,  3,    4,  5,  6,  7,   12,  9, 14, 11, 
	       23, 13, 21, 15,   17, 19, 16, 18,   20,  2, 22,  0],
	"B":  [ 5,  7,  2,  3,    4, 15,  6, 14,    8,  9, 10, 11, 
	       12, 13, 16, 18,    1, 17,  0, 19,   22, 20, 23, 21],
	"B'": [18, 16,  2,  3,    4,  0,  6,  1,    8,  9, 10, 11, 
	       12, 13,  7,  5,   14, 17, 15, 19,   21, 23, 20, 22]
}


'''
sticker indices:

        0  1
        2  3
16 17   8  9   4  5  20 21
18 19  10 11   6  7  22 23
       12 13
       14 15

face colors:

    0
  4 2 1 5
    3

rules:
[ U , U', R , R', F , F', D , D', L , L', B , B']
'''

#--------------------------------------------------------------------------------

class Cube:


	def __init__(self, config="WWWW RRRR GGGG YYYY OOOO BBBB"):
			
		#============================================================================
		# This code ensures that tiles is a string without spaces in it, and
		# string is a more readable version with spaces in it, as in the default
		# argument.  The user may initialize Cube with a string in either form. 
		#============================================================================
		self.tiles = config.replace(" ","")
		#============================================================================
		# separate tiles into chunks of size 4 and insert a space between them
		#============================================================================
		chunks = [self.tiles[i:i+4] + " " for i in range(0, len(self.tiles), 4)]
		self.config = "".join(chunks)
		
		self.depth = 0
		self.rule = ""
		self.parent = None


	def __str__(self):
		#============================================================================
		# Shows cube in "readable" string format.
		#============================================================================
		return self.config

		
	def __eq__(self,state):
		return (self.tiles == state.tiles) or (self.config == state.config)

	def __lt__(self, state):
		return calcHeuristic(self) < calcHeuristic(state)

	def toGrid(self):
		#============================================================================
		# produces a string portraying the cube in flattened display form, i.e.,
		#
		#	   RW       
		#	   GG       
		#	BR WO YO GY 
		#	WW OO YG RR 
		#	   BB       
		#	   BY       
		#============================================================================

		def part(face,portion):
			
			#============================================================================
			# This routine converts the string corresponding to a single face to a 
			# 2x2 grid
			#    face is in [0..5] if it exists, -1 if not
			#    portion is either TOP (=0) or BOTTOM (=1)
			# Example:
			# If state.config is "RWGG YOYG WOOO BBBY BRWW GYRR". 
			#   part(0,TOP) is GW , part(0,BOTTOM) is WR, ...
			#   part(5,TOP) is BR , part(5,BOTTOM) is BB
			#============================================================================

			result = "   "
			if face >=0 :	
				offset = 4*face + 2*portion
				result = self.tiles[offset] + self.tiles[offset+1] + " "
			return result
			
		TOP    = 0
		BOTTOM = 1

		str = ""
		for row in [TOP,BOTTOM]:
			str += part(-1,row) + part(0,row) + \
			      part(-1,row) + part(-1,row) + "\n"
			
		for row in [TOP,BOTTOM]:
			str += part(4,row) + part(2,row) + \
			      part(1,row) + part(5,row) + "\n"
		
		for row in [TOP,BOTTOM]:
			str += part(-1,row) + part(3,row) + \
			      part(-1,row) + part(-1,row) + "\n"

		return str


	def applicableRules(self):
		return list( RULES.keys() )
	
	
	def applyRule(self, rule):
		#============================================================================
		# return new state formed by applying rule to state
		#============================================================================
		# your code
		stateArr = list(self.tiles)
		tempArr = copy.deepcopy(stateArr)
		for i in range(0, 24):
			stateArr[i] = tempArr[RULES[rule][i]]
		stateStr = "".join(stateArr)
		newState = Cube(stateStr)
		return newState 

	def shuffle(self, n):
		state = copy.deepcopy(self)
		for i in range(0, n):
			chosenRule = random.choice(list(RULES))
			state = state.applyRule(chosenRule)
			print(chosenRule)
			print(state)
		return state

	def goal(self):
		return self.config == goalState.config


goalState = Cube()

#--------------------------------------------------------------------------------
#  GRAPH SEARCH
#--------------------------------------------------------------------------------

def first(list):
    return list[0]

def rest(list):
    return list[1:]

def member(x,L):
	return x in L

def compare(a,b):
	s = 0
	for i in range(0, 24):
		if a[i] != b[i]:
			s+=1
		else:
			continue
	return s

'''
The Hueristic applied calculates the  number of tiles that are out of position + depth(node). states are added to the open container(priority queue)
in increasing order of the calculated heuristic value.
'''

def calcHeuristic(state):
	h = compare(state.config, goalState.config)
	h += state.depth
	return h

def deadEnd(state):
	return False

path1 = []


def backTrack(stateList):
	
	state = first(stateList)
	if member(state, rest(stateList)):
		return "FAILED-1"
	if deadEnd(state):
		return "FAILED-2"
	if state.goal():
		print("Goal Reached")
		return None
	if len(stateList) > 20:
		return "FAILED-3"
	if RULES == None:
		return "FAILED-4"
	
	for rule in RULES:
		newState = state.applyRule(rule)
		newStateList = copy.deepcopy(stateList)
		newStateList.insert(0, newState)
		path = backTrack(newStateList)
		if path is None:
			path1.append(rule)
			return path
	
	return "FAILED-5"


def search(state, container, heuristic):
	closed = []
	root = state
	if state.goal():
		print("goal reached")
		exit()
	if heuristic:
		container.put((0, root))
	else:
		container.put(root)
	while (not container.empty()):
		print("Number of states in Open", container.qsize())
		if heuristic:
			node = container.get()[1]
		else:
			node = container.get()
		closed.append(node)
		if node.goal():
			print(node)
			print("goal reached")
			print("solution path")
			while node != root:
				print(node)
				node = node.parent
			print(root)
			print("--- %s seconds ---" % (time.time() - start_time))
			exit()
		for rule in RULES:
			newNode = node.applyRule(rule)
			print(newNode)
			if not member(newNode, closed):
				newNode.parent = node
				newNode.depth = node.depth + 1
				if heuristic:
					container.put((calcHeuristic(newNode) ,newNode))
				else:
					container.put(newNode)
			else:
				continue


#--------------------------------------------------------------------------------
#  MAIN PROGRAM
#--------------------------------------------------------------------------------
def depthFirstSearch(state):
	search(state, queue.LifoQueue(), False)

def breadthFirstSearch(state):
	search(state, queue.Queue(), False)

def bestFirstSearch(state):
	search(state, queue.PriorityQueue(), True)

start_time = time.time()
if __name__ == '__main__':
	
	#============================================================================
	# Read input from command line:
	#   python3 <this program>.py -c arg -m arg -v
	# where
	#   -c provides an initial state or an integer n specifying a number of random 
	#      rules to apply to the goal state.
	#   -m indicates the method to use to solve the problem 
	#   -v indicates VERBOSE mode for detailed algorithm tracing
	#
	# See definition of getConfiguration() above for further details, examples.
	#============================================================================

	initialState, method, MAX_DEPTH, VERBOSE = getConfiguration()
			
	parameter = ""
	if method=="DEPTH_FIRST":
		parameter=", with MAX_DEPTH=" + str(MAX_DEPTH)
	print("method=" + method + parameter)

	if not VERBOSE:
		print("Non-", end="")
	print("Verbose mode.\n")

	
	random.seed() # use clock to randomize RNG
	print(initialState)
	print(calcHeuristic(initialState))
	print(initialState.toGrid())

	if(method == "DEPTH_FIRST"):
		print("initiating depth first search")
		depthFirstSearch(initialState)
	elif(method == "BREADTH_FIRST"):
		print("initiating breadth first search")
		breadthFirstSearch(initialState)
	elif(method == "BEST_FIRST"):
		print("initiating best first search")
		bestFirstSearch(initialState)
	elif(method == "IT_BACKTRACK"):
		stateList = []
		print("initiating itterative backtrack")
		for rule in RULES:
			state = initialState.applyRule(rule)
			stateList.append(state)
		result = backTrack(stateList)
		print(result)



		


import threading
import time
import logging
import requests
import random
global exitFlag
exitFlag = 0

global VIOLATION_PERCENT
VIOLATION_PERCENT = 0.2
global ITERATION_SIZE
ITERATION_SIZE = 40

global runningCountLock
runningCountLock = threading.Lock()

global runningReadCount
runningReadCount = 0
global runningWriteCount
runningWriteCount = 0



global neededAccountLock
neededAccountLock = threading.Lock()

global neededRead
neededRead = 4 
global neededWrite
neededWrite = 4

global totalCount
totalCount = 0

global totalCountLock
totalCountLock = threading.Lock()

global totalMax
totalMax = 300



logger = logging.getLogger('mylogger')
logger.setLevel(logging.INFO)

handler = logging.FileHandler('./example.log')
logger.addHandler(handler)

# tells if need more get or post or none
def setNeededType():
	global totalCountLock
	totalCountLock.acquire()
	global VIOLATION_PERCENT
	global ITERATION_SIZE
	global totalCount
	thresholdVioLation = False
	thresholdVioReset = False
	if totalCount % ITERATION_SIZE == (ITERATION_SIZE * (1-VIOLATION_PERCENT)):
		thresholdVioLation = True
	elif totalCount % ITERATION_SIZE == 0:
		thresholdVioReset = True
	totalCountLock.release()
	
	global neededAccountLock
	neededAccountLock.acquire()
	global neededRead
	global neededWrite
	if (thresholdVioLation):
		
		vioType = random.randint(0, 2) #0: read, 1: write, 2:both
		if vioType == 0:
			
			neededRead = 6 
			logger.info(str(time.time()) + " set violation:true neededRead:" + str(neededRead) + " neededWrite:" + str(neededWrite))
		elif vioType == 1:
			neededWrite = 6
			logger.info(str(time.time()) + " set violation:true neededRead:" + str(neededRead) + " neededWrite:" + str(neededWrite))
		else:
			neededRead = 6
			neededWrite = 6
			logger.info(str(time.time()) + " set violation:true neededRead:" + str(neededRead) + " neededWrite:" + str(neededWrite))
		
	if thresholdVioReset:
		neededRead = 4
		neededWrite = 4
		logger.info(str(time.time()) + " set violation:false neededRead:" + str(neededRead) + " neededWrite:" + str(neededWrite))
	
	neededAccountLock.release()

class myThread (threading.Thread):
	def __init__(self, name, url):
		threading.Thread.__init__(self)
		self.name = name
		self.url = url
		self.counter = 0

	def run(self):
		reqAmounts = [10, 50, 80, 200, 100]
		global exitFlag
		while exitFlag != 1:
			neededProcess = self.getNeededProc()
			if len(neededProcess) > 0:
				reqAmount = reqAmounts[random.randint(0, len(reqAmounts)-1)]
				reqType = " "
				
				if neededProcess == 'r':
					# make get
					reqType = " get "
					self.modifyRunningCount(1, 'r')
					logger.info(str(time.time()) + " reqId:" + self.name + str(self.counter) + reqType + str(reqAmount) + " start")
					response = requests.get(self.url + '/'+ str(reqAmount))
				else:
					reqType = " post "
					self.modifyRunningCount(1, 'w')
					logger.info(str(time.time()) + " reqId:" + self.name + str(self.counter) + reqType + str(reqAmount) + " start")
					response = requests.post(self.url + '/'+ str(reqAmount))

				logger.info(str(time.time()) + " reqId:" + self.name + str(self.counter) + reqType + str(reqAmount) + " end")
				self.incrementTotal()
				self.counter = self.counter + 1
				if (reqType == " get "):
					self.modifyRunningCount(-1, 'r')
				else:
					self.modifyRunningCount(-1, 'w')
				setNeededType()


			

	def modifyRunningCount(self, c, type):
		global runningCountLock
		runningCountLock.acquire()

		if type == 'r':
			global runningReadCount
			runningReadCount = runningReadCount + c
		else:
			global runningWriteCount
			runningWriteCount = runningWriteCount + c
		
		runningCountLock.release()

	def getNeededProc(self):
		neededType = ""
		global neededAccountLock
		neededAccountLock.acquire()
		global neededRead
		global neededWrite
		global runningCountLock
		runningCountLock.acquire()
		global runningReadCount
		global runningWriteCount
		if random.randint(0, 1) == 0:
			if runningReadCount < neededRead:
				neededType = 'r'
			elif runningWriteCount < neededWrite:
				neededType = 'w'
		else:
			if runningWriteCount < neededWrite:
				neededType = 'w'
			elif runningReadCount < neededRead:
				neededType = 'r'
		runningCountLock.release()
		neededAccountLock.release()

		return neededType;

	def incrementTotal(self):
		global totalCountLock
		totalCountLock.acquire()
		global totalCount
		totalCount = totalCount + 1
		totalCountLock.release()

		global totalMax
		if totalCount > totalMax:
			global exitFlag
			exitFlag = 1

# Create new threads
totalMax = ITERATION_SIZE * 5
threads = []
url = "http://ec2-54-187-235-151.us-west-2.compute.amazonaws.com:8000"
for i in range(11):
	threads.append(myThread("Thread-" + str(i), url))

for t in threads:
	t.start()

for t in threads:
	t.join()
print ("Exiting Main Thread")
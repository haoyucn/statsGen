import threading
import time
import logging
import requests
import random
global exitFlag
exitFlag = 0

logging.info('So should this')

global runningCountLock
runningCountLock = threading.Lock()

global runningCount
runningCount = 0

global neededAccount
neededAccount = 4

global neededAccountLock
neededAccountLock = threading.Lock()

global totalCount
totalCount = 0

global totalCountLock
totalCountLock = threading.Lock()

global totalMax
totalMax = 300

logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

def setNeededAmount():
	global totalCountLock
	totalCountLock.acquire()
	global totalCount
	if totalCount % 40 > 15:
		na = 11
	else:
		na = 4
	global neededAccountLock
	neededAccountLock.acquire()
	global neededAccount
	neededAccount = na
	neededAccountLock.release()
	totalCountLock.release()
	logging.info(str(time.time()) + " setParallelMax:" + str(na))

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
			if self.needMoreProc():
				self.modifyRunningCount(1)
				reqAmount = reqAmounts(random.randint(0, len(reqAmounts)-1))
				reqType = " "
				if random.randint(0, 1):
					# make get
					reqType = " get "
					logging.info(str(time.time()) + " reqId:" + self.name + str(self.counter) + reqType + str(reqAmount) + " start")
					response = requests.get(self.url + '/'+ str(reqAmount))
				else:
					reqType = " post "
					logging.info(str(time.time()) + " reqId:" + self.name + str(self.counter) + reqType + str(reqAmount) + " start")
					response = requests.post(self.url + '/'+ str(reqAmount))

				logging.info(str(time.time()) + " reqId:" + self.name + str(self.counter) + reqType + str(reqAmount) + " end")
				self.incrementTotal()
				self.counter = self.counter + 1
				self.modifyRunningCount(-1)
				setNeededAmount()


			

	def modifyRunningCount(self, c):
		global runningCountLock
		runningCountLock.acquire()
		global runningCount
		runningCount = runningCount + c
		runningCountLock.release()

	def needMoreProc(self):
		global neededAccountLock
		neededAccountLock.acquire()
		global neededAccount
		if neededAccount < 5:
			neededAccountLock.release()
			return True
		neededAccountLock.release()
		return False

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
totalMax = 300
threads = []
url = ""
for i in range(11):
	threads.append(myThread("Thread-" + str(i), url))

for t in threads:
	t.start()

for t in threads:
	t.join()
print ("Exiting Main Thread")
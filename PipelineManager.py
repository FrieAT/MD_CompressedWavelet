
from IProcess import IProcess, EDataType

import multiprocessing as mp
from queue import Empty, Full
from math import floor, ceil
from shutil import get_terminal_size

class PipelineManager(IProcess):
	def __init__(self):
		IProcess.__init__(self)

		self.isManager = True
		self.mpQueue = None

	def toId(self):
		return ""

	def getType(self):
		return EDataType.PipelineManager

	def do_multiprocessing(self, imageData, multiCoreOverload = 1.0):

		threads = []
		maxItems = len(imageData.data)
		cpuCount = int(floor(mp.cpu_count() * multiCoreOverload))
		
		# Have at least one process running.
		if cpuCount < 1:
			cpuCount = 1
		
		itemsPerCpu = int(ceil(maxItems / cpuCount))

		self.mpQueue = mp.Queue()

		def updateProgress():
			self.printProgressBar(len(self.data), maxItems)
			try:
				imageData = self.mpQueue.get(True, 1)
				self.data.append(imageData)
			except Empty:
				pass

		self.printProgressBar(0, maxItems)

		try:
			for i in range(cpuCount):
				# Actually it is copied when the mp.Process is started as a 'spawn'.
				# Fork method is here not supported! Otherwise .copy() is needed.
				mpImageData = IProcess()
				mpImageData.do(imageData)
				mpImageData.data = mpImageData.data[(i * itemsPerCpu):((i+1) * itemsPerCpu)]

				# Start a process.
				p = mp.Process(target=PipelineManager.do, args=(self,mpImageData,False))
				threads.append(p)
				p.start()

				updateProgress()

			while not len(self.data) == maxItems:
				updateProgress()
			self.printProgressBar(maxItems, maxItems)

		finally:
			# Kill all used threads.
			for thread in threads:
				thread.terminate()

		return self

	def do(self, imageData, multiCore = True, multiCoreOverload = 1.0):
		self.data = []

		if multiCore:
			return self.do_multiprocessing(imageData, multiCoreOverload)

		if imageData:
			for d in imageData.data:
				imageData = IProcess.do(self, d)
				
				# If multiCore is started, put calculated imageData into multiprocessing.Queue.
				# The decision is made by checking if self.mpQueue is defined.
				if self.mpQueue:
					self.mpQueue.put(imageData, True, None)
				else:
					self.data.append(imageData)

		return self

	# Source: https://gist.github.com/greenstick/b23e475d2bfdc3a82e34eaa1f6781ee4
	def printProgressBar (self, iteration, total, prefix = None, suffix = None, decimals = 1, length = 50, fill = '█', autosize = True):
		if not prefix:
			prefix = self.getTypeAsString()+': '
		prefix = ' '+prefix
		if not suffix:
			suffix = ''
		percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
		styling = '%s |%s| %s%% %s' % (prefix, fill, percent, suffix)
		if autosize:
			cols, _ = get_terminal_size(fallback = (length, 1))
			length = cols - len(styling)
		filledLength = int(length * iteration // total)
		bar = fill * filledLength + '-' * (length - filledLength)
		print('\r%s' % styling.replace(fill, bar), end = '\r')
		# Print New Line on Complete
		if iteration == total: 
			print()


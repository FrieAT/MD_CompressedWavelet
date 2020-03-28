
from IProcess import IProcess, EDataType

import math

class EuclideanDistance(IProcess):
	def __init__(self):
		IProcess.__init__(self)

	def getType(self):
		return EDataType.EuclidDistance

	# Assuming imageData is the leaved-one-out element.
	# and self.features contains all other elements.
	def do(self, imageData):
		IProcess.do(self, imageData.data[0]) # Manager is identified by its first element.
		
		self.data = []

		chosenOne = imageData.data[0]

		for otherOne in imageData.data[1:]:
			if not len(otherOne.data) == len(chosenOne.data):
				raise Exception("OtherOne Length must be the same as ChosenOne! "+str(len(imageData.data))+" != "+str(len(chosenOne)))

			distance = 0.0
			for i in range(len(otherOne.data)):
				distance += math.pow((otherOne.data[i] - chosenOne.data[i]), 2)

			ed = EuclideanDistance()
			IProcess.do(ed, otherOne)
			ed.data = math.sqrt(distance)
			self.data.append(ed)

		return self

from IProcess import IProcess, EDataType

class kNearestNeighbour(IProcess):
	def __init__(self):
		IProcess.__init__(self)

	def getType(self):
		return EDataType.KNN

	# Assuming imageData.data are the (n - 1) images.
	# The image to check against is the imageData itself.
	def do(self, imageData):
		IProcess.do(self, imageData)

		self.data = sorted(imageData.data, key=lambda x: x.data)

		self.checkSort()

		return self

	def checkSort(self):
		arr = self.data
		for i in range(len(arr))[1:]:
			if arr[i - 1].data > arr[i].data:
				raise Exception("ERROR: Sorting failed! Data is not sorted ascending.")

	def getNeighbours(self, nearestNeighbours):
		return self.data[:nearestNeighbours]

	def getNeighbourByClass(self, nearestNeighbours):
		classes = {}
		for foundNeighbour in self.getNeighbours(nearestNeighbours):
			c = foundNeighbour.classifiedAs
			if c in classes:
				classes[c] += 1
			else:
				classes[c] = 0
		
		sorted_x = sorted(classes.items(), key=lambda kv: kv[1])
		return sorted_x[-1][0]
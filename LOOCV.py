
from IProcess import IProcess, EDataType
from ImageData import PipelineManager

#from euclideanDistance import euclideanDistance
#from kNearestNeighbour import kNearestNeighbour

class LOOCV(IProcess):
	def __init__(self):
		IProcess.__init__(self)	
		pass

	def toId(self):
		return self.getTypeAsString()

	def getType(self):
		return EDataType.LOOCV
	
	# Produce every combination of imageData.data
	# Every entry contains the same data array, but with a different index-0 element.
	# So we produce n * (1, (n - 1)) set for a future Leave-One-Out-Cross-Validation.
	def do(self, imageData):
		IProcess.do(self, imageData)

		self.data = []

		for i in range(len(imageData.data)):
			p = PipelineManager()
			p.data = imageData.data.copy()
			
			chosenOne = p.data.pop(i)
			p.data.insert(0, chosenOne)

			self.data.append(p)
		
		return self




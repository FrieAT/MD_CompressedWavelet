
from IProcess import IProcess, EDataType

from PIL import Image

class ConvertFormat(IProcess):

	def __init__(self, toMode = "RGB"):
		IProcess.__init__(self)

		self.imageMode = toMode

		self.copyExceptions += ['imageMode']

	def getType(self):
		return EDataType.ConvertFormat

	def toId(self):
		return str(__class__.__name__)+"_DTWL"+str(self.imageMode)

	def do(self, imageData):
		IProcess.do(self, imageData)

		self.data = []

		for img in imageData.data:
			if img:
				self.data.append(img.convert(mode=self.imageMode))

		return self

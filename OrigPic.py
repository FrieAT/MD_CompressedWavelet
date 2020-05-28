
from IProcess import IProcess, EDataType

from PIL import Image
import os.path

class OrigPic(IProcess):

	### Constructor reading a image from a path.
	### Reads entire image file in given format (default = RGB)
	### TODO: Color format to read in.
	### Mode References: https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
	def __init__(self, imagePath, mode = "RGBX"):
		IProcess.__init__(self)

		self.imagePath = imagePath
		self.imageMode = mode
		self.classifiedAs = "Undefined"
		self.imageDataSize = os.path.getsize(imagePath) / 1024. # Get size in KB.
		img = Image.open(imagePath)
		self.data = [ img.convert(mode=mode) ]

		self.copyExceptions += ['imagePath', 'imageMode', 'classifiedAs', 'imageDataSize']

		pass

	def setClass(self, newClass):
		self.classifiedAs = newClass

	def getClass(self):
		return self.classifiedAs

	def setMode(self, newMode):
		self.imageMode = newMode

	def toId(self):
		(tail, head) = os.path.split(self.imagePath)
		return self.imagePath+"_"+head # No head?

	def getType(self):
		return EDataType.OrigPic

	def getRawArray(self):
		return self.data[0].getdata()

	### Does nothing here, as this class is only supposed to read in the image file.
	def do(self, imageData):
		IProcess.do(self, imageData)

		self.id = self.toId()

		return self

from IProcess import IProcess, EDataType

from ScanAssets import ScanAssets

import os.path

class EncodeToFileList(IProcess):
	def __init__(self, inFormat, path):
		ScanAssets.checkDirPermission(None, path)

		if os.path.isdir(path):
			raise Exception("Please specify a file path for the encoding list.")

		IProcess.__init__(self)

		self.inFormat = inFormat
		self.imagePath = path
		self.scannedFrames = 0

		self.copyExceptions += ['inFormat', 'imagePath', 'scannedFrames']

		pass

	def getType(self):
		return EDataType.EncodeToFileList

	def toId(self):
		return str(__class__.__name__)+"_"+self.inFormat

	def do(self, imageData):
		IProcess.do(self, imageData)

		classifiedAs = imageData.data[0]

		with open(self.imagePath, 'w') as f:
			for origPic in imageData.data:
				f.write("file '"+os.path.abspath(origPic.imagePath)+"'\n")

		self.scannedFrames = len(imageData.data)

		self.data = [True] # Delete previous data.

		return self


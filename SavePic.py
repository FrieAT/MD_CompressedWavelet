from IProcess import IProcess, EDataType
from ImageData import ScanAssets

from PIL import Image
import os.path
from pathlib import Path
import shutil

class SavePic(IProcess):
	def __init__(self, assetPath, filterByClass = None):
		IProcess.__init__(self)
		self.assetSavePath = assetPath
		self.filterByClass = filterByClass

		ScanAssets.checkDirPermission(None, assetPath)

	def getType(self):
		return EDataType.SavePic

	def getSavePath(self):
		return self.imagePath

	def do(self, imageData):
		IProcess.do(self, imageData)

		# STUB: Missing processing over multiple Images. Only saving at last index.

		if self.filterByClass:
			if not self.filterByClass in self.classifiedAs:
				return self

		assetSavePath = os.path.join(self.assetSavePath, self.imagePath)
		(directoryPath, imageFile) = os.path.split(assetSavePath)

		Path(directoryPath).mkdir(parents=True, exist_ok=True)

		ScanAssets.checkDirPermission(None, assetSavePath)
		
		self.imagePath = assetSavePath

		# Ignore unsupported file types.
		if not assetSavePath.endswith(".jxr") and not assetSavePath.endswith(".bpg"):
			image = self.data[-1]
			image.save(assetSavePath)

		return self
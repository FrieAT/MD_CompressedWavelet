
from IProcess import IProcess, EDataType

from OrigPic import OrigPic

import os, os.path
import glob

class ScanAssets(IProcess):
	def __init__(self, assetPath, recursiveSearch = True, colorMode = "RGB"):
		IProcess.__init__(self)

		if recursiveSearch:
			permissions = [os.X_OK, os.R_OK]
		else:
			permissions = [os.R_OK]
		self.checkDirPermission(assetPath, permissions)

		#TODO: If recursive, check permission of all sub directories too.

		self.assetFolder = self.validateTrailingSlash(assetPath)
		self.indexOfAssets = {}
		self.recursiveSearch = recursiveSearch
		self.colorMode = colorMode
		pass

	def toId(self):
		return self.getTypeAsString()

	def getType(self):
		return EDataType.ScanAssets

	def validateTrailingSlash(self, path):
		(parentDir, currentDir) = os.path.split(path)
		path = parentDir
		if len(currentDir):
			path = os.path.join(path, currentDir)
		return path

	def checkDirPermission(self, directory, permissions = [os.W_OK, os.R_OK]):
		testPermissionFor = directory
		while not os.path.exists(testPermissionFor):
			testPermissionFor = os.path.abspath(os.path.join(testPermissionFor, os.pardir))
		for permission in permissions:
			if not os.access(testPermissionFor, permission):
				raise IOError("No permission to folder: "+testPermissionFor)
		pass

	### Transforms imageData with given WaveletTransform into a WaveletPic.
	### Index is used to set the image, to make the transforms from.
	def do(self, imageData):
		IProcess.do(self, imageData)
		self.data = [] # Delete previous data.

		files = glob.glob(os.path.join(self.assetFolder, '**', '*'), recursive=self.recursiveSearch) 
		className = ""
		for f in files:
			substitutedPath = os.path.join(f[len(self.assetFolder):]) #TODO: Still needed?
			(parentDir, fileName) = os.path.split(f)
			if os.path.isdir(f):
				while not parentDir == self.assetFolder:
					(parentDir, className) = os.path.split(parentDir)
				#print("Class: "+str(className))
				if not className in self.indexOfAssets and len(className):
					self.indexOfAssets[className] = []
			elif parentDir == self.assetFolder:
				# Ignore files, which are not in subdirectories of asset folder.
				pass
			else:
				try:
					image = OrigPic(f, mode = self.colorMode)
					image.setClass(className)
					image.do(None)
					self.indexOfAssets[className].append(image)
					self.data.append(image)
				except IOError:
					# Skip current file, because it is a not recognized image file.
					print("Skipping non image file: "+f+ " for class "+className)

		return self

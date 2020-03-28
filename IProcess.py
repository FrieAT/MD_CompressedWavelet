
from EType import EDataType

import copy

class CachedFileLoadedException(Exception):
    pass

class IProcess:

	def __init__(self):
		self.pipeline = []
		self.copyExceptions = ['copyExceptions', 'isChildOfManager']
		self.data = []
		self.isManager = False
		self.isChildOfManager = False
		self.id = ""

	def toId(self):
		'''
		Define a unique string based on the parameters of this class.
		The string will be appended on do()-method.
		With this method, self-object can be identified as e.g. cache files.
		'''
		return ""

	def getType(self):
		return EDataType.Undefined

	def getTypeAsString(self):
		baseType = str(self.getType())[len("EDataType."):]
		if len(self.pipeline) > 0:
			baseType += " -|"
			for pipe in self.pipeline:
				baseType += " " + str(pipe.getType())[len("EDataType."):]
		return baseType

	def __str__(self):
		output = "IData Type: "+str(self.getType())
		output += ("\nFile: "+self.imagePath)
		output += ("\nData count: "+str(len(self.data)))
		return output

	def isValidImageData(self, imageData):
		if imageData and not isinstance(imageData, IProcess):
			raise Exception("Expecting a IProcess object as a pipline-object.")
		return True

	def setManager(self, isManager):
		self.isManager = isManager

	def addPipeline(self, pipe):
		if not self.isValidImageData(pipe):
			return

		self.pipeline.append(pipe)
		pass

	def do(self, imageData):
		if not self.isValidImageData(imageData):
			print("ERROR: Not a valid Image Data!")
			return

		if self.isManager and len(self.toId()):
			imageData.id += "_" + self.toId()

		for pipe in self.pipeline:
			pipe.isChildOfManager = True
			if len(pipe.toId()):
				imageData.id += "_" + pipe.toId()

		# Traverse imageData through pipeline before processing of this IProcess.
		usingCachedData = False
		for pipe in self.pipeline:
			# Set imageData to modified object from pipeline.
			newPipe = copy.deepcopy(pipe)
			try:
				if usingCachedData:
					# If using cached data, only apply the properties from the next pipelines.
					IProcess.do(newPipe, imageData)
				else:
					newPipe.do(imageData)
			except CachedFileLoadedException:
				usingCachedData = True
			imageData = newPipe

		if self.isManager:
			imageData.isChildOfManager = False

		if imageData:
			if len(self.toId()) and not self.isChildOfManager:
				imageData.id += "_" + self.toId()

			if not self.isManager:
				# Copy all properties from old object to new object.
				copiedDict = imageData.__dict__.copy() #TODO: Is it neccessary to copy?
				for key in copiedDict:
					if not key in self.copyExceptions:
						self.__dict__[key] = copiedDict[key]

				return self # Returns itself.

			# If it is a manager self, return the new imageData.
			else:
				return imageData

		return None

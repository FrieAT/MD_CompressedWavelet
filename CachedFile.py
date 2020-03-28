from IProcess import IProcess, EDataType, CachedFileLoadedException

import pickle
import os, os.path
import hashlib

class CachedFile(IProcess):
	def __init__(self, cachePath, save = False, load = False):
		IProcess.__init__(self)
		self.cachePath = cachePath
		self.cacheSave = save
		self.cacheLoad = load
		self.copyExceptions += ['cachePath', 'cacheSave', 'cacheLoad', 'withinManager']

	def toId(self):
		'''
		Not needed for a uniqueness of a object.
		'''
		return ""

	def getType(self):
		return EDataType.CachedFile

	def getFilePath(self, idPipe = None):
		if not idPipe:
			idPipe = self.id
		# print("Hashing FilePath: "+idPipe)
		return os.path.join(self.cachePath, "data_" + str(hashlib.sha1(idPipe.encode("utf8")).hexdigest()) + ".pkl")

	def do(self, img):
		IProcess.do(self, img)

		cacheFilePath = self.getFilePath()

		if self.cacheLoad:
			# print("Trying loading features-data from file "+cacheFilePath+" ...")
			if os.path.isfile(cacheFilePath):
				try:
					with open(cacheFilePath, 'rb') as input:
						self.data = pickle.load(input)
						# print("Loaded features-data from file "+cacheFilePath+"!")
						if self.isChildOfManager:
							raise CachedFileLoadedException()
				except (IOError, EOFError):
					print("Skipping loading file "+cacheFilePath+", because it is corrupted / or no permission!")

		if self.cacheSave:
			# print("Trying saving features-data to file "+cacheFilePath+" ...")
			try:
				with open(cacheFilePath, 'wb') as output:
					pickle.dump(self.data, output, pickle.HIGHEST_PROTOCOL)
					# print("Saved features-data to file "+cacheFilePath+"!")
			except IOError:
				print("Warning, CachedFile "+cacheFilePath+" can not be saved due of a permission error!")
			except (KeyboardInterrupt, SystemExit):
				if os.path.isfile(cacheFilePath):
					os.unlink(cacheFilePath)
				raise
		return self
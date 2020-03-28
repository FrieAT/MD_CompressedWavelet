
from ImageData import PipelineManager, ScanAssets, WaveletPic, FVExtraction

import pickle
import os.path

'''
This class is just for compatibility reasons still here.
It has been refactored to use the new style pipelining, as a PipelineManager.
It is just a wrapper for all jupyter notebook's, which have used AssetPreperation.
STILL NOT RECOMMENDED TO USE THIS CLASS FOR FURTHER USES!
PLEASE DO NOT INERHIT EITHER FROM THIS CLASS!
'''
class AssetPreperation(PipelineManager):
	def __init__(self, waveletMode = 'haar', waveletLevel = 1, featureBoxSize = 4, multiCore = True, multiCoreOverload = 1.0):
		PipelineManager.__init__(self)
		
		# Properties are left due to compatibility reasons.
		self.assetFolder = ""
		self.indexOfAssets = {}
		self.images = []
		self.features = []
		self.waveletMode = waveletMode
		self.waveletLevel = waveletLevel
		self.featureBoxSize = featureBoxSize
		self.multiCore = multiCore
		self.multiCoreOverload = multiCoreOverload
		self.recursiveSearch = True
		pass

	def setAssetFolder(self, newAssetFolder, recursiveSearch=True):
		self.recursiveSearch = recursiveSearch
		self.assetFolder = newAssetFolder
		pass

	# Copies all assets into the test folder and makes a index of every class.
	# Does not modify data from previous class, as it has nothing todo with the pipeline.
	def do(self, imageData = None):
		# Pre-actions before pipelining.
		f = ScanAssets(self.assetFolder, recursiveSearch = self.recursiveSearch)
		f.do(imageData) # Non-Type because we have nothing before.

		self.images = f.data.copy() # Really big ram issue concerning.
		self.indexOfAssets = f.indexOfAssets

		self.addPipeline(WaveletPic(waveletMode = self.waveletMode, level = self.waveletLevel))
		self.addPipeline(FVExtraction(number_of_blocks_vertical = self.featureBoxSize, number_of_blocks_horizontal = self.featureBoxSize))

		# Do we have a cached file?
		featuresFileName = "features_data_WL"+str(self.waveletLevel)+"_W"+str(self.waveletMode)+"_FB"+str(self.featureBoxSize)+".pkl"
		featuresFile = os.path.join(self.assetFolder, "..", "features", featuresFileName)
		self.featuresFile = featuresFile
		recalculateFeatures = True;
		if os.path.isfile(featuresFile):
			print("Loading features-data from file "+featuresFileName+" ...")
			with open(featuresFile, 'rb') as input:
				self.features = pickle.load(input)
				if not len(self.features) == len(self.images):
					print("WARNING: Features data length does not equal image data!")
					self.features = []
				else:
					recalculateFeatures = False
					self.data = self.features.copy()
		else:
			print("WARNING: Features not found cached")

		if recalculateFeatures:
			PipelineManager.do(self, f, multiCore = self.multiCore, multiCoreOverload = self.multiCoreOverload)
			self.features = self.data.copy()

			# Write extracted features into file.
			with open(featuresFile, 'wb') as output:
				pickle.dump(self.features, output, pickle.HIGHEST_PROTOCOL)

		print("| --------- |")
		print("Loaded Images: "+str(len(self.images)))
		print("Loaded Features: "+str(len(self.features)))
		print("| --------- |")
		pass

		

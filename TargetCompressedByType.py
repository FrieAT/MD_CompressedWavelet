from IProcess import IProcess, EDataType

from SavePic import SavePic

import sys
import os
import os.path
import math
import subprocess
from PIL import Image
import skimage.io
import imageio
import time

class TargetCompressedByType(IProcess):
	def __init__(self, extension, compressTo, preserveCompressedOnly=True, path="./compressed/", overwrite = False):
		IProcess.__init__(self)
		self.extension = extension
		self.compressToKSize = compressTo
		self.quality = 100
		self.preserveCompressedOnly = preserveCompressedOnly
		self.compressedPath = path
		self.lossLess = False
		self.overwrite = overwrite

		self.copyExceptions += ['overwrite', 'lossLess', 'compressedPath', 'preserveCompressedOnly', 'quality', 'extension']

	def toId(self):
		return IProcess.toId(self) # STUB

	def getType(self):
		return EDataType.TargetCompressedByType

	def do(self, imageData):
		# For JPEG XR and BPG make some preperations.
		if self.extension == "jxr" or self.extension == "bpg":
			#print("File: "+imageData.imagePath)
			#print("Start Converting to bmp in order to encode jxr!")
			toFormat = "bmp"
			if self.extension == "bpg":
				toFormat = "png"

			lossless = TargetCompressedByType(toFormat, sys.maxsize, self.preserveCompressedOnly, path=self.compressedPath)
			lossless.do(imageData)
			imageData.data = lossless.data
			imageData.imagePath = lossless.imagePath
			self.compressedPath = "./"

		# Free storage for compressed file (compressed file is definitley < original file)
		s = SavePic(self.compressedPath)
		s.do(imageData)
		copiedSavePath = s.getSavePath()


		IProcess.do(self, s)
		self.data = [] # Delete previous data.

		img = s.data[-1]
		if img:
			supportedFileExtensions = []
			# JPEG
			supportedFileExtensions.append(["jpg", "jpeg", "jpe", "jif", "jfif", "jfi"])
			# JPEG XR
			supportedFileExtensions.append(["jp2", "j2k", "jpf", "jpx", "jpm", "mj2"])
			# JPEG 2000
			supportedFileExtensions.append(["jxr", "hdp", "wdp"])
			# BPG
			supportedFileExtensions.append(["bpg"])

			#if not len([True for i in supportedFileExtensions if i==self.extension]) > 0:
			#	raise Exception("Unknown format given.")

			lastQuality = 0
			compressedSavePath = os.path.splitext(copiedSavePath)[0]+'.'+self.extension
			binarySearch = [ self.quality ]
			i = self.quality
			while len(binarySearch) > 0: 
				quality = int(binarySearch.pop())

				if not self.overwrite and copiedSavePath == compressedSavePath:
					break
				elif self.extension == "bmp" or self.extension == "png":
					lastQuality = quality
					command = ["magick", "convert", "-compress", "none", copiedSavePath, compressedSavePath]
					self.lossLess = True
				else:
					command = ["magick", "convert", "-quality", str(quality), copiedSavePath, compressedSavePath]
				
				#print("COMMAND EXECUTING: " + ' '.join(command))

				# This here is a workaround for bpgenc as it randomly gets a segmentation fault.
				# If more than 10 times for a bpg an error occurs, than raise exception.
				bpgMaxErrorTries = 0
				supressStdErr = None
				if self.extension == "bpg":
					bpgMaxErrorTries = 10
					supressStdErr = subprocess.PIPE

				while True:
					try:
						if bpgMaxErrorTries == 0:
							supressStdErr = None
						subprocess.run(command, check=True, stderr=supressStdErr)
						break
					except subprocess.CalledProcessError as grepexc:    
						if self.extension == "bpg" and grepexc.returncode != 0 and bpgMaxErrorTries > 0:
							bpgMaxErrorTries -= 1
						else:
							raise grepexc


				self.imageDataSize = os.path.getsize(compressedSavePath) / 1024.0

				#print("Quality ABS: "+str(abs(lastQuality - quality))+" for "+copiedSavePath)
				
				i = i / 2.0

				if self.lossLess:
					break
				elif self.imageDataSize < self.compressToKSize and abs(lastQuality - quality) > 1 and (quality + i) < self.quality:
					binarySearch.append((quality + i))
				elif self.imageDataSize > self.compressToKSize and abs(lastQuality - quality) > 0:
					binarySearch.append((quality - i))
				lastQuality = quality
			
			if self.extension == "jxr" or self.extension == "bpg":
				self.data = imageData.data
				self.imagePath = compressedSavePath

				#print("Converting back to bmp for file: "+self.imagePath)

				# Convert back to a lossless / uncompressed format.
				toFormat = "bmp"
				if self.extension == "bpg":
					toFormat = "png"
				lossless = TargetCompressedByType(toFormat, sys.maxsize, self.preserveCompressedOnly, path="", overwrite = True)
				lossless.do(self)

				#print("Done! :D Compressed Size: "+str(self.imageDataSize))

				self.data = lossless.data
				self.imagePath = lossless.imagePath
			else:
				img = Image.open(compressedSavePath)
				self.data = [ img.convert(mode=self.imageMode) ]

				self.imagePath = compressedSavePath
		else:
			self.data.append(img)

		if not self.preserveCompressedOnly and not copiedSavePath == compressedSavePath:
			os.unlink(copiedSavePath)

		return self

		 
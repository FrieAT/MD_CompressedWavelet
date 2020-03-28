from IProcess import IProcess, EDataType

from SavePic import SavePic

import os
import os.path
import math
import subprocess
from PIL import Image

class TargetCompressedByType(IProcess):
	def __init__(self, extension, compressTo, preserveCompressedOnly=True):
		IProcess.__init__(self)
		self.extension = extension
		self.compressToKSize = compressTo
		self.quality = 100
		self.preserveCompressedOnly = preserveCompressedOnly

	def toId(self):
		return IProcess.toId(self) # STUB

	def getType(self):
		return EDataType.TargetCompressedByType

	def do(self, imageData):
		IProcess.do(self, imageData)
		self.data = [] # Delete previous data.

		# Free storage for compressed file (compressed file is definitley < original file)
		s = SavePic("./compressed/")
		s.do(imageData)

		img = s.data[-1]
		copiedSavePath = s.getSavePath()
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
			binarySearch = [ self.quality ]
			i = self.quality
			while len(binarySearch) > 0: 
				quality = int(binarySearch.pop())

				compressedSavePath = os.path.splitext(copiedSavePath)[0]+'.'+self.extension
				command = ["magick", "convert", "-quality", str(quality), copiedSavePath, compressedSavePath]
				
				#print(' '.join(command))

				subprocess.run(command, check=True)

				imageSize = os.path.getsize(compressedSavePath) / 1024.0

				#print("Quality ABS: "+str(abs(lastQuality - quality))+" for "+copiedSavePath)
				
				i = i / 2.0

				if imageSize < self.compressToKSize and abs(lastQuality - quality) > 1:
					binarySearch.append((quality + i))
				elif imageSize > self.compressToKSize and abs(lastQuality - quality) > 0:
					binarySearch.append((quality - i))
				lastQuality = quality
				

			# Re-set img to compressed Image.
			img = Image.open(compressedSavePath)
			img.convert(mode=self.imageMode)

		self.data.append(img)

		if not self.preserveCompressedOnly:
			os.unlink(copiedSavePath)

		return self

		 
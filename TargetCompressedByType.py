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
	def __init__(self, extension, compressTo, preserveCompressedOnly=True, path="./compressed/", lossLess = False):
		IProcess.__init__(self)
		self.extension = extension
		self.compressToKSize = compressTo
		self.quality = 100
		self.preserveCompressedOnly = preserveCompressedOnly
		self.compressedPath = path
		self.lossLess = lossLess

	def toId(self):
		return IProcess.toId(self) # STUB

	def getType(self):
		return EDataType.TargetCompressedByType

	def do(self, imageData):
		# For JPEG XR convert first to bmp.
		if self.extension == "jxr":
			bmp = TargetCompressedByType("bmp", sys.maxsize, self.preserveCompressedOnly, path=self.compressedPath)
			bmp.do(imageData)
			imageData.data = bmp.data
			imageData.imagePath = bmp.imagePath
			self.compressedPath = "./"
		# For BPG convert first to jpg.
		elif self.extension == "bpg":
			jpg = TargetCompressedByType("jpg", sys.maxsize, self.preserveCompressedOnly, path=self.compressedPath, lossLess = True)
			jpg.do(imageData)
			imageData.data = jpg.data
			imageData.imagePath = jpg.imagePath
			self.compressedPath = "./"
			time.sleep(1)

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

				if copiedSavePath == compressedSavePath:
					break
				elif self.extension == "bmp":
					lastQuality = quality
					command = ["magick", "convert", "-compress", "none", copiedSavePath, compressedSavePath]
				elif self.extension == "jxr":
					command = ["JxrEncApp", "-i", copiedSavePath, "-o", compressedSavePath, "-q", str(quality / 100.0), "-c", str(9)]
				else:
					command = ["magick", "convert", "-quality", str(quality), copiedSavePath, compressedSavePath]
				
				#print("COMMAND EXECUTING: " + ' '.join(command))

				subprocess.run(command, check=True)

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
				
			rawImage = None
			
			if self.extension == "bpg":
				img = None
			elif self.extension == "jxr":
				img = None
			else:
				rawImage = skimage.io.imread(compressedSavePath)
			
				img = Image.fromarray(rawImage)
				img = img.convert(mode="L")
			self.imagePath = compressedSavePath

		self.data.append(img)

		if not self.preserveCompressedOnly and not copiedSavePath == compressedSavePath:
			os.unlink(copiedSavePath)

		return self

		 
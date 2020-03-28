from IProcess import IProcess, EDataType

from PIL import Image
import numpy as np
import math
import cv2

class CropImageByClass(IProcess):

	def __init__(self):
		IProcess.__init__(self)
		self.cropped = True

	def getType(self):
		return EDataType.CroppedPic

	def toId(self):
		return str(__class__.__name__)

	def do(self, imageData):
		IProcess.do(self, imageData)
		self.data = [] # Delete previous data.

		className = imageData.classifiedAs
		img = np.array(imageData.data[0]) # STUB: Only tested with grayscale images.
		maxarea = 0
		max2 = 0

		'''
		PARAMETERS for classes:
		'''
		minThresholdValue = 0
		maxThresholdValue = 255
		rectangleThreshold = 0.5
		cropRatio = [ 1.0, 1.0, 1.0, 1.0]       #y, h, x, w
		invertImage = False

		if "FV-USM" in className:
			minThresholdValue = 40
			rectangleThreshold = 0.05
			cropRatio = [ 0.35, 0.75, 0.15, 0.8 ]
		elif "HKPU-FV" in className:
			minThresholdValue = 45
			rectangleThreshold = 0.95
			cropRatio = [ 0.36, 0.67, 0.15, 0.7 ]
			invertImage = True
		elif "IDIAP" in className:
			minThresholdValue = 45
			rectangleThreshold = 0.85
			cropRatio = [ 0.3, 0.7, 0.15, 0.8 ]
		elif "MMCBNU_6000" in className:
			minThresholdValue = 20
			rectangleThreshold = 0.8
			cropRatio = [ 0.17, 0.84, 0.0, 0.8 ]
		elif "PLUS-FV3-Laser_PALMAR" in className:
			minThresholdValue = 40
			rectangleThreshold = 0.2
			cropRatio = [ 0.25, 0.55, 0.4, 0.6 ]
		elif "SCUT_FVD" in className:
			minThresholdValue = 70
			rectangleThreshold = 0.6
			cropRatio = [ 0.25, 0.9, 0.3, 0.75 ]
		elif "SDUMLA-HMT" in className:
			minThresholdValue = 50
			rectangleThreshold = 0.3
			cropRatio = [ 0.3, 0.75, 0.05, 0.9 ]
		elif "THU-FVFDT" in className:
			minThresholdValue = 65
			rectangleThreshold = 0.22
			cropRatio = [ 0.2, 0.7, 0.43, 0.68 ]
		elif "UTFVP" in className:
			minThresholdValue = 40
			rectangleThreshold = 0.5
			cropRatio = [ 0.3, 0.65, 0.0, 0.8 ]
		else:
			raise Exception("Cropping class "+className+" not implemented!")

		if invertImage:
			img = ~img

		ret, threshed_img = cv2.threshold(img, minThresholdValue, maxThresholdValue, cv2.THRESH_BINARY)
		contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		(imWidth, imHeight) = img.shape
		imArea = imWidth * imHeight

		framemax = None
		frame2 = None

		for c in contours:
			# get the bounding rect
			x, y, w, h = cv2.boundingRect(c)
			# draw a green rectangle to visualize the bounding rect
			#cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), 2)
			area = w * h
			if area > maxarea:
				max2 = maxarea
				maxarea = area
				framemax = (x,y, w, h)
				if not frame2:
					frame2 = framemax
			elif area > max2:
				max2 = area
				frame2 = (x, y, w, h)

		spaceA = (1.0 / imArea * maxarea)
		spaceB = (1.0 / imArea * max2)
		if spaceA >= rectangleThreshold:
			frame2 = framemax
			#print("Framemax has"+str(spaceA)+" percent space!")
		elif spaceB >= rectangleThreshold:
			framemax = frame2
			#print("Frame2 has"+str(spaceB)+" percent space!")

		#if framemax[1] > frame2[1]:
		#	uborder = cv2.line(img, (framemax[0], framemax[1]+framemax[3]), (framemax[0]+framemax[2], framemax[1]+framemax[3]), (255, 0, 0), 1)
		#	oborder = cv2.line(img, (frame2[0], frame2[1]),(frame2[0]+frame2[2], frame2[1]), (255, 0, 0), 1)

		size = img.shape

		if "MMCBNU_6000" in className:
			cropX = 0
			cropWidth = size[1]
			cropY = framemax[1]
			cropHeight = 0 + (framemax[1]+framemax[3])
#		elif "PLUS-FV3-Laser_PALMAR" in className:
#			cropX = framemax[0]
#			cropWidth = framemax[0]+framemax[2]
#			cropY = framemax[1]
#x			cropHeight = 0 + (framemax[1]+framemax[3])
		elif "SDUMLA-HMT" in className:
			cropX = 0
			cropWidth = size[1] - 1
			cropY = frame2[1]
			cropHeight = 0 + (framemax[1]+framemax[3])
		elif "SCUT_FVD" in className:
			cropX = framemax[0]
			cropWidth = framemax[0] + framemax[2]
			cropY = framemax[1]
			cropHeight = framemax[1] + framemax[3]
		elif "THU-FVFDT" in className:
			cropX = framemax[0]
			cropWidth = framemax[0] + framemax[2]
			cropY = framemax[1]
			cropHeight = framemax[1] + framemax[3]
		else:
			cropX = 0
			cropWidth = size[1]
			cropY = frame2[1]
			cropHeight = 0 + (framemax[1]+framemax[3])

		'''
		if cropY >= imHeight:
			print("Fehler 1")
		if cropHeight >= imHeight:
			print("Fehler 2")
		if cropWidth >= imWidth:
			#cropWidth = imWidth - 1
			print("Fehler 3! KORRIGIERT")
		'''

		crop_img = img[cropY : cropHeight, cropX : cropWidth]

		partHeight, partWidth = crop_img.shape
		part_img = crop_img[math.floor(partHeight * cropRatio[0]): math.floor(partHeight * cropRatio[1]), math.floor(partWidth * cropRatio[2]): math.floor(partWidth * cropRatio[3])]

		if invertImage:
			part_img = ~part_img

		self.data = [ Image.fromarray(part_img) ]

		return self






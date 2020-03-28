from IProcess import IProcess, EDataType

from PIL import Image
import dtcwt
import numpy as np
import math
from dtcwt.utils import asfarray

import warnings

class DTCWaveletPic(IProcess):
	def __init__(self, level=1):
		IProcess.__init__(self)

		self.waveletLevel = level
		self.waveletLevelMax = level
		pass

	def getType(self):
		return EDataType.DTCWaveletPic

	def toId(self):
		return str(__class__.__name__)+"_DTWL"+str(self.waveletLevel)

	### Transforms imageData with given WaveletTransform into a DTCWaveletT.
	### Index is used to set the image, to make the transforms from.
	def do(self, imageData):
		
		warnings.filterwarnings("ignore")

		def warn(*args, **kwargs):
			pass

		warnings.warn = warn

		IProcess.do(self, imageData)
		self.data = [] # Delete previous data.

		processImage = imageData.data[-1].getdata()

		# Check for event length.
		(width, height) = processImage.size

		#print("Image Size: "+str(width)+" and "+str(height))

		if not width % 2 == 0 and not height % 2 == 0:
			processImage = processImage.resize((width - 1, height - 1))
		elif not width % 2 == 0:
			processImage = processImage.resize((width - 1, height))
		elif not height % 2 == 0:
			processImage = processImage.resize((width, height - 1))

		(width, height) = processImage.size

		processImageArr = np.array(processImage, np.uint8).reshape(height, width)

		#print("Image Shape: "+str(processImageArr.shape[0])+" and "+str(processImageArr.shape[1]))

		#coeffs2 = pywt.dwt2(processImage, self.waveletMode)
		transform = dtcwt.Transform2d()

		t = transform.forward(processImageArr, nlevels = self.waveletLevel)
		'''
		print(t.highpasses[1])
		print(t.lowpass)
		print(len(t.highpasses))
		print("|--------------|")

		print("Image Size: "+str(len(processImage)))
		print("HighPass Size: "+str(len(t.highpasses[0][0])))
		print("LowPass Size: "+str(len(t.lowpass[0])))
		print("HighPass Type: "+str(type(t.highpasses[0][0])))
		'''

		for level in reversed(range(self.waveletLevel)):
		    for slice_idx in reversed(range(t.highpasses[level].shape[2])):
		        highpass = np.abs(t.highpasses[level][:,:,slice_idx])
		        
		        # Interpolate to grayscale values.
		        #highpass_interpolated = np.interp(highpass, [np.amin(highpass), np.amax(highpass)], [255, 0])
		        
		        # Generate squared image result from highpass filter.
		        half_size = math.floor(math.sqrt(highpass.size) + 1)
		        slice_img = Image.frombuffer(self.imageMode, (half_size, half_size), highpass)

		        self.data.append(slice_img)

		# STUB: lowpass filter is not a result wich is wished, but ignored in further progressing.
		self.data.append(Image.fromarray(processImageArr))

		return self

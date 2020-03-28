
from IProcess import IProcess, EDataType

from PIL import Image

import pywt
import pywt.data

class WaveletPic(IProcess):
	def __init__(self, waveletMode='bior1.3', level=1):
		IProcess.__init__(self)

		# See: https://pywavelets.readthedocs.io/en/latest/regression/wavelet.html
		waveletFamilyValidated = False # Default setting.
		for waveletFamily in pywt.families():
			if waveletMode.startswith(waveletFamily):
				if not waveletMode in pywt.wavelist(waveletFamily):
					raise NotImplementedError(str(pywt.wavelist(waveletFamily)))
				else:
					waveletFamilyValidated = True
					break
		if not waveletFamilyValidated:
			raise NotImplementedError()

		self.waveletMode = waveletMode
		self.waveletLevel = 0
		self.waveletLevelMax = level
		pass

	def toId(self):
		return str(__class__.__name__)+"_WM"+self.waveletMode+"_WL"+str(self.waveletLevelMax)

	def getType(self):
		return EDataType.Wavelet

	### Transforms imageData with given WaveletTransform into a WaveletPic.
	### Index is used to set the image, to make the transforms from.
	def do(self, imageData):
		if self.waveletLevel == 0:
			IProcess.do(self, imageData)
			self.data = [] # Delete previous data.
		else:
			self.data = imageData.data[:-1] # Get details from previous transformation, without approx.Image
		
		self.waveletLevel += 1

		processImage = imageData.data[-1]
		coeffs2 = pywt.dwt2(processImage, self.waveletMode)
		LL, (LH, HL, HH) = coeffs2
		details = [HH, HL, LH, LL]
		for detail in details:
			self.data.append(Image.fromarray(detail, mode=self.imageMode))

		# Call itself recursive for more wavelet levels.
		if self.waveletLevel < self.waveletLevelMax:
			self.do(self)
		else:
			self.waveletLevel = 0 # Reset counter, for future re-wavelet-processing. :P

		return self

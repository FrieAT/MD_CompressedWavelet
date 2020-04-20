
# Source: https://notebooks.azure.com/salva/projects/Digital-Image-Processing/html/001%20Anisotropic%20Quality%20Index%20(AQI).ipynb
# Author: Salvador Gabarda

from IProcess import IProcess, EDataType

import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
from scipy.fftpack import fft, ifft
import math
from scipy import signal

class BIQAA(IProcess):

	def oriented_pattern(self,seq_length,angle):
		"""
		This function originates a pattern that is later used for the orientation of the operational pseudo-Wigner distribution
		computation window,     seq_length: sequence length in pixels,    angle: orientation in degrees.
		"""
		angle = np.mod(angle,180)
		# correction to set axes in the image (x: rows, y: columns) to observer cartesian coordinates x,y
		angle = np.mod((angle+90),180)
		angle =math.radians(angle)
		pi = math.pi
		h = int((seq_length/2))
		values = np.r_[float(-h):float(h+1)]
		new_positions = np.zeros([2*h+1, 2])
		for position in range(seq_length):
			if angle >= 0 and angle < pi/4:
				new_positions[position,0] = values[position]+h
				new_positions[position,1] = values[position]*math.tan(angle)+h
			elif angle >= pi/4 and angle < pi/2:
				new_positions[position,0] = values[position]*math.tan(pi/2-angle)+h
				new_positions[position,1] = values[position]+h
			elif angle >= pi/2 and angle < 3*pi/4:
				new_positions[position,0] = values[position]*math.tan(pi/2-angle)+h
				new_positions[position,1] = values[position]+h
			elif angle >= 3*pi/4 and angle <= pi:
				new_positions[position,0] = 1*values[position]+h
				new_positions[position,1] = values[position]*math.tan(angle)+h
			new_points = np.round_(new_positions)
		return new_points.astype(int)

	def image_arrangement (self,test_image,seq_length,angle,indices):
		"""
		arrangement operation for time reduction
		"""
		rows = test_image.shape[0]
		columns = test_image.shape[1]
		layers = np.zeros(((seq_length,rows,columns)))
		for k in range(seq_length):
			mask = np.zeros((seq_length,seq_length))
			mask[indices[k,0],indices[k,1]] = 1
			layers[k,:,:] = signal.convolve2d(test_image, mask, boundary='symm', mode='same')
		return layers

	def layer_product_function(self,layers,seq_length):
		"""
		product function of the Wigner distribution
		"""
		faces = layers.shape[0]
		rows =layers.shape[1]
		columns = layers.shape[2]
		layer_product = np.ones(((seq_length-1,rows,columns)))
		layers[faces-1,:,:]=layers[0,:,:]
		for i in range(faces-1):
			layer_product[i,:,:]= layers[i,:,:]*layers[faces-1-i]
		return layer_product

	def layer_wigner_distribution(self,test_image,seq_length,angle):
		"""
		Wigner distribution of test_image, seq_lengthe: odd number of pixels, e.g.: 9, angle: degrees, e.g.: 45
		"""
		indices = self.oriented_pattern(seq_length,angle)
		layers = self.image_arrangement (test_image,seq_length,angle,indices)
		layer_product = self.layer_product_function(layers,seq_length)
		distribution = fft(layer_product, axis = 0)
		distribution = np.real(distribution)
		# set zero frequency in central position
		Head = distribution[int(seq_length/2):seq_length,:,:]
		Tail = distribution[0:int(seq_length/2),:,:]
		distribution = np.append(Head,Tail, axis = 0)
		return distribution

	def renyi_entropy(self,distribution,order):
		"""
		This function calculates the Rényi entropy of an image based on its pseudo-Wigner distribution (distribution).
		The "order" variabe represents the exponential order of the Rényi entropy (3 is the most common value)
		"""
		eps = np.finfo(float).eps
		rows = distribution.shape[1]
		columns = distribution.shape[2]
		layers = distribution.shape[0]
		squared_wl = np.ones([layers,rows,columns])
		for layer in range(layers):
			# square distribution local values
			working_layer = distribution[layer,:,:]
			squared_wl[layer,:,:] = np.multiply(working_layer,working_layer)
		squared_wd = squared_wl
		# sum squared wigner distribution along coordinate 1
		sum_sq_wd = np.sum(squared_wd, axis = 0)
		# normalize squared values
		normalized_distribution =np.zeros([layers,rows,columns])
		for layer in range(layers):
			normalized_distribution[layer,:,:] = np.divide(squared_wd[layer,:,:],sum_sq_wd+eps)
		# raise elements to the power defined by input variable "order"
		power_nor_dis = np.power(normalized_distribution,order)
		# sum pixelwise
		entropy_1 = np.sum(power_nor_dis, axis = 0)+eps
		# pixelwise entropy
		entropy_2 =np.log2(entropy_1)
		entropy =(1/(1-order))*entropy_2
		super_threshold_indices = entropy < 0
		entropy[super_threshold_indices] = 0
		entropy = np.nan_to_num(entropy)
		# normalize entropy
		entropy = entropy*(1/np.log2(layers))
		return entropy

	def show_wigner_frequencies(self,distribution):
		"""
		Starting from the pseudo-Wigner distribution (distribution) of the input test image, this function gives a visualization
		of the frequency components of such distribution and images are saved in pdf's
		"""
		rows = distribution.shape[1]
		columns = distribution.shape[2]
		layers = distribution.shape[0]
		frequencies = np.zeros([layers,rows,columns])
		for layer in range(layers):
			frequency = distribution[layer,:,:]
			min_val =np.amin(frequency)
			frequency = frequency - min_val
			max_val = np.amax(frequency)
			frequency = (1/max_val)*frequency
			frequency = np.uint8(255*frequency)
			name = "wigner_distribution_" + str(layer) + ".pdf"
			msg = "Wigner distribution, frequency #" + str(layer)

			frequencies[layer,:,:]= frequency
		return frequencies

	def layer_image_anisotropy(self, test_image,seq_length,orientations,order):
		"""
		This function calculates a parameter that behaves as an objective measure of the quality of the image for Gaussian blur
		and Gaussian noise. It is based on the frequency content given by the pseudo-Wigner distribution.
		"""
		entropy_val = np.zeros([orientations])
		for orientation in range(orientations):
			angle = (180/orientations)*orientation
			#print( angle, " degrees distribution")
			distribution = self.layer_wigner_distribution(test_image,seq_length,angle)
			entropy_pixelwise = self,renyi_entropy(distribution,order)
			entropy = np.mean(entropy_pixelwise)
			#print("entropy is %.4f" % entropy)
			entropy_val[orientation] = entropy
		anisotropy = np.var(entropy_val)
		anisotropy = math.sqrt(anisotropy)

		return anisotropy

	"""
	def input_test_image(self,subfolder,name):
		total_name = subfolder + name
		input_image = mpimg.imread(total_name)
		image_dimension = len(input_image.shape)
		if image_dimension == 3:
			test_image = (1/3)*(input_image[:,:,0]+
			input_image[:,:,1]+input_image[:,:,2])
		else:
			test_image = input_image

		# convert image to regular gray levels
		test_image =np.uint8(255*test_image)
		return test_image
		"""

	def __init__(self):
		IProcess.__init__(self)

		self.orientations = 4
		self.order = 3
		self.seq_length = 9

	def toId(self):
		return str(__class__.__name__)

	def getType(self):
		return EDataType.BIQAA

	def do(self, imageData):
		IProcess.do(self, imageData)

		inputImgData = np.array(self.data[-1])

		self.anisotropy = self.layer_image_anisotropy(inputImgData,self.seq_length,self.orientations,self.order)

		return self

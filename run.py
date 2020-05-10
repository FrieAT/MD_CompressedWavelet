#!/usr/local/bin/python3.8

from ImageData import OrigPic, WaveletPic, ScanAssets, StationaryWaveletPic, CropImageByClass, DTCWaveletPic
from FVExtraction import FVExtraction
from AssetPreperation import AssetPreperation
from ImageData import LOOCV, EuclideanDistance, kNearestNeighbour, PipelineManager, CachedFile, TargetCompressedByType, NIQE, BIQAA, BRISQUE

from bokeh.plotting import figure, output_file, show
from bokeh.io import output_notebook

import os.path
import sys
import math

def main():
	statistics = open("graphs/niqe_score.txt", "w")
	statistics.write(';'.join(["FilePath", "NIQEScore", "Compressed", "Size", "MaxSize"])+"\n")

	'''
	print("NIQE Score for uncompressed images:")
	f = ScanAssets("./images", recursiveSearch = True)
	f.do(None)
	m1 = PipelineManager()
	m1.addPipeline(NIQE())
	m1.do(f)
	for img in m1.data:
		statistics.write(';'.join([img.imagePath, str(img.niqe_score), "0", str(img.imageDataSize), str(img.imageDataSize)])+"\n")
	'''

	compressToFormats = [ "jp2", "jpg" ]
	compressToKSizes = [30, 60, 120, 240, 480]

	for toFormat in compressToFormats:
		for toKSize in compressToKSizes:
			print("NIQE Score for compressed "+str(toFormat)+" image with size of "+str(toKSize)+"K:")
			f = ScanAssets("./images", recursiveSearch = True)
			f.do(None)
			m1 = PipelineManager()
			m1.addPipeline(TargetCompressedByType(toFormat, toKSize, True))
			m1.addPipeline(NIQE())
			m1.do(f, multiCoreOverload = 1.0)
			for img in m1.data:
				statistics.write(';'.join([img.imagePath, str(img.niqe_score), "1", str(img.imageDataSize), str(toKSize)])+"\n")

	exit(0)

	makeExcessiveTesting = False
	crop = True

	if makeExcessiveTesting:
		doWaveLevels = range(9)[1:]
		doFeatureBlockSizes = range(8)[1:]
	else:
		doWaveLevels = [1]
		doFeatureBlockSizes = [2]

	statistics = open("graphs/statistics.txt", "a")

	for crop in [False, True]:
		for wave in doWaveLevels:
			for fIndex in doFeatureBlockSizes:
				print("Calculating for WaveLevel "+str(wave)+" and FeatureBoxSize: "+str(math.pow(fIndex, 2)))

				statistics.write("\nCalculating for WaveLevel "+str(wave)+" and FeatureBoxSize: "+str(math.pow(2, fIndex)))

				f = ScanAssets("./images", recursiveSearch = True)
				f.do(None)
				print("Assets: "+str(len(f.data)))

				assets = len(f.data)

				m1 = PipelineManager()
				m1.addPipeline(CachedFile("./features", load = True))
				if crop:
					m1.addPipeline(CropImageByClass())
					statistics.write("\ncropped\n")
				else:
					statistics.write("\nuncropped\n")
				m1.addPipeline(WaveletPic(level = wave))
				m1.addPipeline(FVExtraction(number_of_blocks_vertical = fIndex, number_of_blocks_horizontal = fIndex))
				m1.addPipeline(CachedFile("./features", save = True))
				m1.do(f)

				l = LOOCV()
				l.do(m1)

				m2 = PipelineManager()
				m2.addPipeline(EuclideanDistance())
				m2.addPipeline(kNearestNeighbour())
				m2.do(l, multiCoreOverload = 0.01)

				for kNeighbours in [3, 5, 7]:
					statistics.write("\nkNeighbours: "+str(kNeighbours) + "\n")
					countsPerClass = {}
					index = 1

					correct = 0

					for img in m2.data:

						neighbourClass = img.getNeighbourByClass(kNeighbours)

						if not img.classifiedAs in countsPerClass:
							countsPerClass[img.classifiedAs] = {'positive':0,'negative':0,'falsePositive':0,'index':index}
							index += 1
						if not neighbourClass in countsPerClass:
							countsPerClass[neighbourClass] = {'positive':0,'negative':0,'falsePositive':0,'index':index}
							index += 1
						countsObj = countsPerClass[img.classifiedAs]

						if neighbourClass == img.classifiedAs:
							countsObj['positive'] += 1
							correct += 1
						else:
							countsObj['negative'] += 1
							countsPerClass[str(neighbourClass)]['falsePositive'] += 1

					output_file(os.path.join("graphs", "graph_w"+str(wave)+"_fb"+str(fIndex)+"_kNN"+str(kNeighbours)+".html"))

					statistics.write("Total: "+ str(correct)+"/"+str(assets)+"\n")
					statistics.write("Total: "+  "{:.3f}".format(correct/assets)+"\n")

					p = figure(title="graph_w"+str(wave)+"_fb"+str(fIndex)+"_kNN"+str(kNeighbours))
					farben = ["#ff0000", "#ffaa00", "#00aaff", "#888888", "#ffff00", "#000000", "#aaffaa", "#9900cc", "#333333"]
					for className, imgClass in countsPerClass.items():

						statistics.write(str(className)+": ")

						#statistics.write("Absolute Values:\n")
						#statistics.write("TP: "+str(imgClass['positive'])+"/"+str((imgClass['positive']+imgClass['negative']))+"\n")
						# statistics.write("FN: "+str(imgClass['negative'])+"\n")
						# statistics.write("FP: "+str(imgClass['falsePositive'])+"\n\n")

						#statistics.write("Relative Values:\n")
						#tp = imgClass['positive']/(imgClass['positive']+imgClass['negative'])
						#fn = 1 - tp
						#statistics.write("TP: "+"{:.3f}".format(tp)+"\n")
						# statistics.write("FN: "+"{:.3f}".format(fn)+"\n\n")

						#statistics.write("Precision (TP/(TP+FP)): ")
						#precision = imgClass['positive']/(imgClass['positive']+imgClass['falsePositive'])
						#statistics.write("{:.3f}".format(precision)+"\n")

						# statistics.write("Recall (TP/(TP+FN))): ")
						recall = imgClass['positive']/(imgClass['positive']+imgClass['negative'])
						statistics.write("{:.3f}".format(recall)+"\n")

						#statistics.write("\n")

						lineWidth = 0.25
						index = int(imgClass['index'])
						xPos = [index - lineWidth, index, index + lineWidth]
						yPos = [imgClass['positive'], imgClass['negative'], imgClass['falsePositive']]

						p.vbar(x=xPos, width=lineWidth, bottom=0, top=yPos, color=farben[index - 1], legend_label=className)

					#show(p)

	statistics.close()




	return

if __name__ == "__main__":
	main()

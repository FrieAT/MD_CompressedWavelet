#!/usr/local/bin/python3.8

from ImageData import OrigPic, WaveletPic, ScanAssets, StationaryWaveletPic, CropImageByClass, DTCWaveletPic
from FVExtraction import FVExtraction
from AssetPreperation import AssetPreperation
from ImageData import LOOCV, EuclideanDistance, kNearestNeighbour, PipelineManager, CachedFile, TargetCompressedByType, NIQE, BIQAA, ConvertFormat

from bokeh.plotting import figure, output_file, show
from bokeh.io import output_notebook

import os.path
import sys
import math

def main():
	makeExcessiveTesting = True
	crop = True
	toKSize = 30
	overload = 0.7
	toCompressBy = TargetCompressedByType.CompressBy.Ratio

	if makeExcessiveTesting:
		doWaveLevels = range(9)[1:]
		doFeatureBlockSizes = range(8)[1:]
	else:
		doWaveLevels = [1]
		doFeatureBlockSizes = [2]

	statistics = open("graphs/statistics.txt", "a")

	statistics.write(';'.join(["WaveLevel", "FeatureBoxSize", "ToFormat", "ToGoalCompress", "ByCompress", "Crop", "kNN", "Total", "Class", "ClassTotal"])+"\n");

	for wave in doWaveLevels:
		for crop in [False]:
			for toFormat in ["bpg", "jpg", "jp2", "jxr"]:
				for fIndex in doFeatureBlockSizes:
					statistics.flush()

					#print("Calculating for WaveLevel "+str(wave)+" and FeatureBoxSize: "+str(math.pow(fIndex, 2)))
					header = ';'.join([str(wave), str(math.pow(2, fIndex)), toFormat, str(toKSize), str(toCompressBy)])
					#statistics.write("\nCalculating for WaveLevel "+str(wave)+" and FeatureBoxSize: "+str(math.pow(2, fIndex)))
					#statistics.write(';'.join([str(wave), str(math.pow(2, fIndex)), toFormat, str(toKSize), str(toCompressBy)]))

					f = ScanAssets("./images", recursiveSearch = True)
					f.do(None)

					print("Assets: "+str(len(f.data)))

					assets = len(f.data)

					m3 = PipelineManager()
					m3.addPipeline(CachedFile("./features", load = True))
					m3.addPipeline(TargetCompressedByType(toFormat, toKSize, True, compressBy=toCompressBy))
					m3.addPipeline(ConvertFormat(toMode="L"))
					m3.addPipeline(CachedFile("./features", save = True))
					m3.do(f, multiCoreOverload = overload)

					m1 = PipelineManager()
					m1.addPipeline(CachedFile("./features", load = True))
					if crop:
						m1.addPipeline(CropImageByClass())
						header += (";cropped")
					else:
						header += (";uncropped")

					m1.addPipeline(WaveletPic(level = wave, waveletMode = "db3"))
					m1.addPipeline(FVExtraction(number_of_blocks_vertical = fIndex, number_of_blocks_horizontal = fIndex))
					m1.addPipeline(CachedFile("./features", save = True))
					m1.do(m3, multiCoreOverload = overload)

					mb1 = PipelineManager()
					mb1.addPipeline(CachedFile("./features", load = True))
					if crop:
						m1.addPipeline(CropImageByClass())
					mb1.addPipeline(ConvertFormat(toMode="L"))
					mb1.addPipeline(WaveletPic(level = wave, waveletMode = "db3"))
					mb1.addPipeline(FVExtraction(number_of_blocks_vertical = fIndex, number_of_blocks_horizontal = fIndex))
					mb1.addPipeline(CachedFile("./features", save = True))
					mb1.do(f, multiCoreOverload = overload)

					print("Sanity Check is working ...")

					if not len(m1.data) == len(mb1.data):
						print("ERROR: Compressed and Uncompressed data set not equal!");
						exit();

					m1.data.sort(key=lambda x: x.imagePath)
					mb1.data.sort(key=lambda x: x.imagePath)

					for i in range(len(m1.data)):
						compressedPath = ('.'.join(mb1.data[i].imagePath.split('.')[:-1]))
						originalPath = ('.'.join(mb1.data[i].imagePath.split('.')[:-1]))
						#print("DEBUG 4: "+mb1.data[i].imagePath+" in "+m1.data[i].imagePath)
						if not originalPath in compressedPath:
							print("ERROR: "+compressedPath+" not in "+originalPath+"!");
							exit();

					l = LOOCV()
					l.do(m1)

					lb = LOOCV()
					lb.do(mb1)

					print("Replacing uncompressed images, with compressed ones in LOOCV comparisons...")

					for i in range(len(l.data)):
						l.data[i].data = [ l.data[i].data[0] ] + lb.data[i].data[1:]

					l = LOOCV()
					l.do(m1)

					m2 = PipelineManager()
					m2.addPipeline(EuclideanDistance())
					m2.addPipeline(kNearestNeighbour())
					m2.do(l, multiCoreOverload = overload)

					for kNeighbours in range(20)[3:]:

						if kNeighbours % 2 == 0:
							continue

						#statistics.write(header + ";" + str(kNeighbours))
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

						#statistics.write("Total: "+ str(correct)+"/"+str(assets)+"\n")
						#statistics.write("Total: "+  "{:.3f}".format(correct/assets)+"\n")
						#statistics.write(";"+"{:.3f}".format(correct/assets))

						innerHeader = header + ";"+str(kNeighbours)+";"+"{:.3f}".format(correct/assets)

						p = figure(title="graph_w"+str(wave)+"_fb"+str(fIndex)+"_kNN"+str(kNeighbours))
						farben = ["#ff0000", "#ffaa00", "#00aaff", "#888888", "#ffff00", "#000000", "#aaffaa", "#9900cc", "#333333"]
						for className, imgClass in countsPerClass.items():

							statistics.write(innerHeader + ";"+str(className))

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
							statistics.write(";{:.3f}".format(recall)+"\n")

							#statistics.write("\n")

							lineWidth = 0.25
							index = int(imgClass['index'])
							xPos = [index - lineWidth, index, index + lineWidth]
							yPos = [imgClass['positive'], imgClass['negative'], imgClass['falsePositive']]

							p.vbar(x=xPos, width=lineWidth, bottom=0, top=yPos, color=farben[index - 1], legend_label=className)

						#show(p)
						#statistics.write("\n");

	statistics.close()




	return

if __name__ == "__main__":
	main()

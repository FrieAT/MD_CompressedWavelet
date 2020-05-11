from enum import Enum

class EDataType(Enum):
	Undefined = 0
	ScanAssets = 5
	OrigPic = 10
	CroppedPic = 11
	SavePic = 12
	ConvertFormat = 13
	EncodeToFileList = 14
	TargetCompressedByType = 15
	Wavelet = 20
	StWavelet = 21
	FeatureVector = 30
	LOOCV = 40
	EuclidDistance = 45
	KNN = 50
	NIQE = 60
	BIQAA = 61
	CachedFile = 998
	PipelineManager = 999
	DTCWaveletPic = 111

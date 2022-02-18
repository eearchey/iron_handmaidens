#%%
from argparse import FileType
import scipy.io
import pandas as pd
import sys
import os

class Converter():

	def __init__(self, root, fileType, labelMap, labelExclusion) -> None:
		self.root = root
		self.filetype = fileType
		self.labelMap = labelMap
		self.labelExclusion = labelExclusion

	def matToCsv(self, file):
		if self.filetype not in file:
			return

		mat = scipy.io.loadmat(file)

		if self.labelExclusion is not None:
			newMat = {}
			for key in mat:
				if key not in self.labelExclusion:
					newMat[key] = mat[key]
			mat = newMat

		if self.labelMap is not None:
			newMat = {}
			for key in self.labelMap:
				if key in mat:
					newMat[self.labelMap[key]] = mat[key]
				else:
					newMat[key] = mat[key]
			mat = newMat

		print(f'Converting {file}')
		df = pd.DataFrame.from_dict(mat)
		df.to_csv(file.split('.')[0]+'.csv')


	def convertDir(self, dir):
		for file in [os.path.join(self.root, file) for file in os.listdir(dir)]:
			print(file)
			self.matToCsv(file)

if __name__ == '__main__':
	rename = {
		'Shimmer_4680_TimestampSync_Unix_CAL':'Timestamp_4680',
		'Shimmer_4680_ECG_EMG_Status1_CAL':'Status_4680',
		'Shimmer_4680_EMG_CH1_24BIT_CAL':'CH1_4680',
		'Shimmer_4680_EMG_CH2_24BIT_CAL':'CH2_4680',
		'Shimmer_4680_Event_Marker_CAL':'Event_4680',
		'Shimmer_5470_TimestampSync_Unix_CAL':'Timestamp_5470',
		'Shimmer_5470_ECG_EMG_Status1_CAL':'Status_5470',
		'Shimmer_5470_EMG_CH1_24BIT_CAL':'CH1_5470',
		'Shimmer_5470_EMG_CH2_24BIT_CAL':'CH2_5470',
		'Shimmer_5470_Event_Marker_CAL':'Event_5470'
	}
	exclude = ['__head__', '__version__', '__globals__']
	converter = Converter(sys.argv[1], '.mat', rename, exclude)
	converter.convertDir(sys.argv[1])
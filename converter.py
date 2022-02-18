from argparse import FileType
import scipy.io
import pandas as pd
import sys
import os

class Converter():
	version = '1.0.0'

	def __init__(self, root, fileType, labelExclude=None, labelMap=None) -> None:
		self.root = root
		self.filetype = fileType
		self.labelExclude = labelExclude
		self.labelMap = labelMap

	def excludeKeys(self, oldDict: dict):
		newDict = {}
		for key in oldDict:
			if key not in self.labelExclude:
				newDict[key] = oldDict[key]
		return newDict

	def renameKeys(self, oldDict: dict):
		newDict = {}
		for key in oldDict:
			if key in self.labelMap:
				newDict[self.labelMap[key]] = oldDict[key]
			else:
				newDict[key] = oldDict[key]

		return newDict

	def matToCsv(self, infile, outfile=None):
		if self.filetype not in infile:
			print('Skipping'.ljust(20) + infile)
			return

		try:
			mat = scipy.io.loadmat(infile)
		except ValueError:
			print('Unable to convert'.ljust(20) + infile)
			print('File could not be loaded as mat')
			return

		if self.labelExclude is not None:
			mat = self.excludeKeys(mat)
		if self.labelMap is not None:
			mat = self.renameKeys(mat)

		try:
			mat = {key: mat[key].flatten() for key in mat}
			df = pd.DataFrame.from_dict(mat)
		except ValueError:
			print('Unable to convert'.ljust(20) + infile)
			print('File could not be loaded as df')
			return

		if outfile is None:
			outfile = infile.split('.')[0] + '.csv'

		print('Saving'.ljust(20) + outfile)
		df.to_csv(infile.split('.')[0]+'.csv', index=False)


	def convertDir(self, dir, recursive=False):
		if recursive:
			for (path, dirs, files) in os.walk(dir):
				for file in files:
					if file[0] != '.':
						self.matToCsv(os.path.join(path, file))
						print()
		else:
			files = [os.path.join(self.root, file) for file in os.listdir(dir)]
			for file in files:
				self.matToCsv(file)
				print()

if __name__ == '__main__':
	exclude = ['__header__', '__version__', '__globals__']
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
	converter = Converter(sys.argv[1], '.mat', exclude, rename)
	converter.convertDir(sys.argv[1], True)
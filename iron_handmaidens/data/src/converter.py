import os.path
import scipy.io
import pandas as pd

EXCLUDE = ['__header__', '__version__', '__globals__']
RENAME = {
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

class Converter():
	"""
	Class for converting mat files to csv files
	"""

	version = '1.0.0'

	def __init__(self, fileType: str='.mat', labelExclude: list=EXCLUDE, labelMap: dict=RENAME):
		self.filetype = fileType
		self.labelExclude = labelExclude
		self.labelMap = labelMap

	def exclude_keys(self, oldDict: dict) -> dict:
		newDict = {}
		for key in oldDict:
			if key not in self.labelExclude:
				newDict[key] = oldDict[key]
		return newDict

	def rename_keys(self, oldDict: dict) -> dict:
		newDict = {}
		for key in oldDict:
			if key in self.labelMap:
				newDict[self.labelMap[key]] = oldDict[key]
			else:
				newDict[key] = oldDict[key]
		return newDict

	def mat_to_df(self, infile: str) -> None:
		if self.filetype not in infile and type(infile) == str:
			print('Skipping'.ljust(20) + infile)
			return

		try:
			mat = scipy.io.loadmat(infile)
		except ValueError as err:
			print('Unable to convert'.ljust(20) + infile)
			print('File could not be loaded as mat')
			return

		if self.labelExclude is not None:
			mat = self.exclude_keys(mat)
		if self.labelMap is not None:
			mat = self.rename_keys(mat)

		try:
			mat = {key: mat[key].flatten() for key in mat}
			df = pd.DataFrame.from_dict(mat)
		except ValueError as err:
			print('Unable to convert'.ljust(20) + infile)
			print('File could not be loaded as df')
			return

		return df

	def mat_to_csv(self, infile: str, outfile: str=None):
		df = self.mat_to_df(infile)

		if outfile is None:
			head, tail = os.path.split(infile)
			outfile = os.path.join(head, tail.split('.')[0] + '.csv')

		print('Saving'.ljust(20) + outfile)
		df.to_csv(outfile, index=False)


	def dir_to_csv(self, dir: str, recursive: bool=False) -> None:
		if recursive:
			for (path, dirs, files) in os.walk(dir):
				for file in files:
					if file[0] != '.':
						self.mat_to_csv(os.path.join(path, file))

		else:
			files = [os.path.join(dir, file) for file in os.listdir(dir)]
			for file in files:
				self.mat_to_csv(file)

if __name__ == '__main__':
	from sys import argv
	converter = Converter()
	converter.dir_to_csv(argv[1])

import os.path
import scipy.io
import pandas as pd

class Converter():
	"""
	Class for converting mat files to csv files
	"""

	version = '1.0.0'

	def __init__(self, fileType: str='.mat', labelExclude: list=None, labelMap: dict=None) -> None:
		self.filetype = fileType
		self.labelExclude = labelExclude
		self.labelMap = labelMap

	def exclude_keys(self, oldDict: dict) -> dict:
		"""# List of columns in EMG data file that should be excluded from the conversion process."""
		newDict = {}
		for key in oldDict:
			if key not in self.labelExclude:
				newDict[key] = oldDict[key]
		return newDict

	def rename_keys(self, oldDict: dict) -> dict:
		"""# Mapping of old names to new names for the EMG data columns."""
		newDict = {}
		for key in oldDict:
			if key in self.labelMap:
				newDict[self.labelMap[key]] = oldDict[key]
			else:
				newDict[key] = oldDict[key]
		return newDict

	def mat_to_df(self, infile: str) -> pd.DataFrame:
		"""# Convert a matlab file to a pandas dataframe."""
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
			flatMat = {}
			for key in mat:
				try:
					flatMat[key] = mat[key].flatten()
				except:
					print('Unable to convert column: ' + key + ' in file: ' + (infile if type(infile) == str else 'Temorary file'))
			df = pd.DataFrame.from_dict(flatMat)
		except ValueError as err:
			print('Unable to convert'.ljust(20) + infile)
			print('File could not be loaded as df')
			return

		return df

	def mat_to_csv(self, infile: str, outfile: str=None) -> None:
		"""# Convert a matlab file to a csv file."""
		df = self.mat_to_df(infile)

		if outfile is None:
			head, tail = os.path.split(infile)
			outfile = os.path.join(head, tail.split('.')[0] + '.csv')

		print('Saving'.ljust(20) + outfile)
		df.to_csv(outfile, index=False)


	def dir_to_csv(self, dir: str, recursive: bool=False) -> None:
		"""# Convert all matlab files in a directory to csv files."""
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

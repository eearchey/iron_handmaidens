import pandas as pd

class Preprocess:
	"""
	Group of operations commonly done to file in order to prepare it to be rendered
	"""

	def __init__(self, df=pd.DataFrame(), period=(1/1024)):
		self.df = df
		self.period = period

	def calcTime(self):
		return self.df.index * self.period

	def absoluteValue(self, series):
		return abs(self.df[series])

	def RMS(self):
		pass

	def butterworth(self):
		pass

	def movingAverage(self, series, window=30):
		newDf = pd.DataFrame()

		if 'Time' in self.df:
			newDf['Time'] = self.df['Time']
		elif 'Timestamp_4680' in self.df:
			newDf['Time'] = self.df['Timestamp_4680']
		elif 'Timestamp_5470' in self.df:
			newDf['Time'] = self.df['Timestamp_5470']
		else:
			raise ValueError('Could not find timestamp in' + self.df)

		newDf['Moving Average'] = self.df[series].rolling(window).mean()

		return newDf
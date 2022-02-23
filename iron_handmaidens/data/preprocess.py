import pandas as pd
from plotly.offline import plot
import plotly.express as px

class Preprocess:
	"""
	Group of operations commonly done to file in order to prepare it to be rendered
	"""

	def __init__(self, df=pd.DataFrame(), period=None, frequency=None):
		self.df = df
		if period is not None:
			self.period = period
		elif frequency is not None:
			self.frequency = frequency
		else:
			self.period = 1024

	def __repr__(self) -> str:
		return f'Preprocess(DataFrame, {self.period}, {self.frequency})'

	def __str__(self) -> str:
		return self.df.head().to_string()

	def __getitem__(self, idx):
		columns = self.findColumns(idx)

		if len(columns) != 1:
			raise ValueError('More than one column found')

		return columns[0]

	def __add__(self, other):
		return self.merge(other)

	@classmethod
	def read_csv(cls, csv, period=1024) -> object:
		df = pd.read_csv(csv)

		return cls(df, period)

	@property
	def frequency(self):
		return (1/self.period)

	@frequency.setter
	def frequency(self, val):
		self.period = (1/val)

	def findColumns(self, name):
		columns = list(filter(lambda x: name in x, self.df.columns))

		if len(columns) == 0:
			raise ValueError('Column(s) could not be found')

		return columns

	def merge(self, other):
		if type(other) != Preprocess:
			raise TypeError('Trying to add something other than another dataframe')
		elif self.period != other.period:
			raise ValueError('Samples collected with different frequency/period')

		left, right = self.df, other.df
		for df, obj in [(left, self), (right, other)]:
			df[obj['Timestamp']] = df[obj['Timestamp']].astype(int)
			df = df.drop_duplicates(obj['Timestamp'])

		df = pd.merge(left, right, 'inner', left_on=self['Timestamp'], right_on=other['Timestamp'])

		df['Timestamp'] = df[self['Timestamp']]
		df = df.drop(self['Timestamp'], axis=1)
		df = df.drop(other['Timestamp'], axis=1)

		return Preprocess(df, self.period)

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

	def plot(self, x=None, y=None, cap=None):
		if x is None:
			x = self['Timestamp']
		if y is None:
			y = self.findColumns('CH')
		if cap is None:
			cap = len(self.df)

		fig = px.line(self.df[:cap], x, y)
		plt = plot(fig, output_type='div')

		return plt

if __name__ == '__main__':
	print('No main function')

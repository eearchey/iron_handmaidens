import pandas as pd
from plotly.offline import plot as plt
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
			raise ValueError('Column(s) could not be found:' + name)

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

	def normalize(self, channels=None):
		if channels is None:
			channels = self.findColumns('CH')

		for channel in channels:
			max = self.df[channel].max()
			min = self.df[channel].min()
			self.df[channel] = (self.df[channel] - min) / (max - min)

	def quartiles(self, q=[0.9, 0.5, 0.1], columns=None):
		if columns is None:
			columns = self.findColumns('CH')

		return self.df[columns].quantile(q)

	def figure(self, x=None, y=None, slice=None):
		if x is None:
			try:
				x = self['Elapse']
			except ValueError as err:
				x = self['Timestamp']
		if y is None:
			y = self.findColumns('CH')
		if slice is None:
			slice = slice(None)

		return px.line(self.df.iloc[slice], x, y)

	def plot(self, fig=None, x=None, y=None, slice=None):
		if fig is not None:
			return plt(fig, output_type='div')

		fig = self.figure(x, y, slice)

		return plt(fig, output_type='div')

	def run(self):
		self.df['Elapse'] = self.df.index * self.frequency
		self.normalize()
		return self.figure(slice=slice(None, None, 100))

if __name__ == '__main__':
	print('No main function')

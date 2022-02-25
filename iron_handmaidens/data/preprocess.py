import pandas as pd
import plotly.graph_objs as go
# import plotly.express as px
from plotly.offline import plot as plotly_plot

class Preprocess:
	"""
	Group of operations commonly done to file in order to prepare it to be rendered
	"""

	def __init__(self, df, period: float=None, frequency: float=None, maxDataPoints=1000):
		self.df = df

		if period is not None:
			self.period = period
		elif frequency is not None:
			self.frequency = frequency
		else:
			self.period = 1024

		self.maxDataPoints = maxDataPoints

	def __repr__(self) -> str:
		return f'Preprocess(DataFrame, {self.period}, {self.frequency})'

	def __str__(self) -> str:
		return self.df.head().to_string()

	def __getitem__(self, idx: str) -> str:
		columns = self.find_columns(idx)

		if len(columns) != 1:
			raise ValueError('More than one column found')

		return columns[0]

	def __add__(self, other: object):
		return self.merge(other)

	@classmethod
	def read_csv(cls, csv: str or object, period: float=1024):
		df = pd.read_csv(csv)

		return cls(df, period)

	@property
	def frequency(self) -> float:
		return (1/self.period)

	@frequency.setter
	def frequency(self, val: float):
		self.period = (1/val)

	@property
	def idxs(self) -> slice:
		return slice(None, None, len(self.df) // self.maxDataPoints)

	def find_columns(self, names: str or list) -> list:
		if type(names) != list:
			names = [names]

		columns = []
		for name in names:
			columns += list(filter(lambda x: name in x, self.df.columns))

		if len(columns) == 0:
			raise ValueError('Column(s) could not be found:' + name)

		return columns

	def merge(self, other: object):
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

		return Preprocess(df, period=self.period)

	def bandpassing(self):
		pass

	def RMS(self):
		pass

	def butterworth(self):
		pass

	def moving_average(self, colNames, window=7000):
		if type(colNames) != list:
			colNames = [colNames]

		df = pd.DataFrame()
		for col in colNames:
			df[col] = self.df[col].rolling(window).mean()

		return df

	def normalize(self, channels=None):
		if channels is None:
			channels = self.find_columns('CH')

		for channel in channels:
			max = self.df[channel].max()
			min = self.df[channel].min()
			self.df[channel] = (self.df[channel] - min) / (max - min)

	def quartiles(self, q: list=[0.9, 0.5, 0.1], columns: list=None):
		if columns is None:
			columns = self.find_columns('CH')

		return self.df[columns].quantile(q)

	def figure(self, x: str or list=None, y: str or list=None, visible: str=None):
		if x is None:
			try:
				x = self['Elapse']
			except ValueError as err:
				x = self['Timestamp']

		if y is None:
			y = self.find_columns(['RMS', 'Moving Average', 'CH'])

		fig = go.Figure()

		for line in y:
			newFig = go.Scatter(
				x=self.df[x].iloc[self.idxs],
				y=self.df[line].iloc[self.idxs],
				name=line
			)
			fig.add_trace(newFig)

		if visible is not None:
			fig.for_each_trace(lambda trace: trace.update(visible=True) if trace.name in visible else trace.update(visible='legendonly'))

		fig.update_layout(
			title="EMG Data",
			xaxis_title=x,
			yaxis_title="Normalized Values",
			legend_title="Data Source",
			# font=dict(
			# 	family="Courier New, monospace",
			# 	size=18,
			# 	color="RebeccaPurple"
			# )
		)

		return fig

	def plot(self, fig: object=None, x: list or str=None, y: list or str=None, visible=None):
		if fig is not None:
			return plotly_plot(fig, include_plotlyjs=False, output_type='div')

		fig = self.figure(x, y, visible)

		return plotly_plot(fig, include_plotlyjs=False, output_type='div')

	def run(self):
		channels = self.find_columns('CH')

		self.normalize()
		self.df['Elapse (s)'] = self.df.index * self.frequency
		self.df[['Moving Average ' + channel[2:] for channel in channels]] = self.moving_average(channels)


if __name__ == '__main__':
	print('No main function')

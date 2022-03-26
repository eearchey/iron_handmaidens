import pandas as pd
import plotly.graph_objs as go
from plotly.offline import plot as plotly_plot

from data.src.converter import Converter

class EMGData:
	"""
	Group of operations commonly done to file in order to prepare it to be rendered
	"""

	def __init__(self, df, channelNames: list, timeName: str, eventName: str, period: float, maxDataPoints: int, windowTime: float) -> None:
		self.df = df

		self.channelNames = channelNames
		self.timeName = timeName
		self.eventName = eventName

		self.period = period
		self.maxDataPoints = maxDataPoints
		self.windowTime = windowTime

	@classmethod
	def read_csv(cls, csv: str or object, channels: list, time: str, event: str, period: float=1024, maxDataPoints: int=1000, windowTime: float=1) -> 'EMGData':
		df = pd.read_csv(csv)

		return cls(df, channels, time, event, period, maxDataPoints, windowTime)

	@classmethod
	def read_mat(cls, mat: str or object, channels: list, time: str, event: str, period: float=1024, maxDataPoints: int=1000, windowTime: float=1) -> 'EMGData':
		df = Converter().mat_to_df(mat)
		df = df.astype(float)

		return cls(df, channels, time, event, period, maxDataPoints, windowTime)

	def __repr__(self) -> str:
		return f'EMGData(DataFrame, {self.period}, {self.frequency})'

	def __str__(self) -> str:
		return self.df.head().to_string()

	@property
	def frequency(self) -> float:
		return (1/self.period)

	@frequency.setter
	def frequency(self, val: float):
		self.period = (1/val)

	@property
	def idxs(self) -> slice:
		if len(self.df) < self.maxDataPoints:
			return slice(None)
		return slice(None, None, len(self.df) // self.maxDataPoints)

	@property
	def windowLength(self) -> int:
		return int(self.windowTime // self.frequency)

	@property
	def channels(self) -> pd.DataFrame or pd.Series:
		return self.df[self.channelNames]

	@channels.setter
	def channels(self, data: int or float or pd.Series or pd.DataFrame) -> None:
		self.df[self.channelNames] = data

	@property
	def time(self) -> pd.Series:
		return self.df[self.timeName]

	@time.setter
	def time(self, data: int or float or pd.Series) -> None:
		self.df[self.timeName] = data

	@property
	def event(self) -> pd.Series:
		return self.df[self.eventName]

	@event.setter
	def event(self, data: int or float or pd.Series) -> None:
		self.df[self.eventName] = data

	def __getitem__(self, idxs: str or list) -> str:
		columns = self.find_columns(idxs)

		if type(idxs) == str:
			if len(columns) != 1:
				raise ValueError('More than one column found while searching for: ' + idxs +
								'\nPass list to search for multiple column names')
			else:
				return columns[0]

		return columns

	def find_columns(self, names: str or list) -> list:
		if type(names) != list:
			names = [names]

		columns = []
		for name in names:
			columns += list(filter(lambda x: name in x, self.df.columns))

		if len(columns) == 0:
			raise ValueError('Column(s) could not be found:' + name)

		return columns

	def __add__(self, other: object):
		return self.merge(other)

	def merge(self, other: object):
		if type(other) != EMGData:
			raise TypeError('Trying to add something other than another dataframe')
		elif self.period != other.period:
			raise ValueError('Samples collected with different frequency/period')

		left, right = self.df.copy(), other.df.copy()
		for df, obj in [(left, self), (right, other)]:
			df[obj['Timestamp']] = df[obj['Timestamp']].astype('int64')
			df = df.drop_duplicates(obj['Timestamp'])

		df = pd.merge(left, right, 'inner', left_on=self['Timestamp'], right_on=other['Timestamp'])
		new = EMGData(df, self.channelNames, self.timeName, self.eventName, self.period, self.maxDataPoints, self.windowTime)

		try:
			timestamps = new[['Timestamp']]
		except ValueError as err:
			timestamps = []
		try:
			elapses = new[['Elapse']]
		except ValueError as err:
			elapses = []

		for colType, colName in [(timestamps, 'Timestamp'), (elapses, 'Elapse')]:
			if len(colType) > 1:
				new.df[colName] = new.df[colType[0]]
				for col in colType:
					new.df = new.df.drop(col, axis=1)

		return new

	def bandpassing(self, colNames):
		pass

	def RMS(self, colNames, slidingWindow):
		new = pd.DataFrame()

		if type(colNames) != list:
			colNames = [colNames]

		for col in colNames:
			new[col] = self.df[col] ** 2    #Square terms
			new[col] = new[col].rolling(int((slidingWindow/1000.0)//self.frequency)).mean()  #Calculate mean over slidingWindow
			new[col] = new[col] ** (1/2)      #Calculate square roots

		return new

	def butterworth(self):
		pass

	def moving_average(self, colNames):
		new = pd.DataFrame()

		if type(colNames) != list:
			colNames = [colNames]

		for col in colNames:
			new[col] = self.df[col].rolling(self.windowLength).mean()

		return new

	def normalize(self, colNames):
		new = pd.DataFrame()

		if type(colNames) is not list:
			colNames = [colNames]

		for col in colNames:
			max = self.df[col].max()
			min = self.df[col].min()
			new[col] = (self.df[col] - min) / (max - min)

		return new

	def quartiles(self, q: list or float=[0.9, 0.5, 0.1], columns: list or str=None):
		if columns is None:
			columns = self[['CH']]

		return self.df[columns].quantile(q)

	def find_events(self, eventsCol='Event'):
		new = pd.DataFrame()

		new['Toggle'] = self.df[self[[eventsCol]][0]].diff()
		new = self.df.loc[abs(new['Toggle']) == 3]

		return [(new.iloc[i], new.iloc[i+1]) for i in range(0, len(new)-1, 2)]

	def figure(self, x: str or list=None, y: str or list=None, visible: str=None, eventMarkers=None):
		if x is None:
			try:
				x = self['Elapse']
			except ValueError as err:
				x = self['Timestamp']

		if y is None:
			y = self[['RMS', 'Moving Average', 'CH']]

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

		if eventMarkers is not None:
			for start, stop in self.find_events(eventMarkers):
				fig.add_vrect(start['Elapse (s)'], stop['Elapse (s)'], fillcolor='green', opacity=0.15)

		fig.update_layout(
			title="EMG Data",
			xaxis_title=x,
			yaxis_title="Normalized Values",
			legend_title="Data Source",
		)

		return fig

	def plot(self, fig: object=None, x: list or str=None, y: list or str=None, visible=None, eventMarkers=None):
		if fig is not None:
			return plotly_plot(fig, include_plotlyjs=False, output_type='div')

		fig = self.figure(x, y, visible, eventMarkers)

		return plotly_plot(fig, include_plotlyjs=False, output_type='div')

	def preprocess(self):
		new = EMGData(self.df.copy(), self.channelNames, self.timeName, self.eventName, period=self.period, maxDataPoints=self.maxDataPoints, windowTime=self.windowTime)

		channels = self[['CH']]

		new.df['Elapse (s)'] = new.df[new['Timestamp']].diff().fillna(0).cumsum() / 1000

		new.df[['Moving Average ' + channel[2:] for channel in channels]] = new.moving_average(channels)
		new.df[['RMS ' + channel[2:] for channel in channels]] = new.RMS(channels, 100)

		lines = new[['RMS', 'Moving', 'CH']]
		new.df[lines] = new.normalize(lines)

		return new


if __name__ == '__main__':
	print('No main function')

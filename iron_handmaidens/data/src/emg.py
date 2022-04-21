import pandas as pd
from copy import deepcopy
from scipy.signal import butter, sosfilt
import plotly.graph_objs as go
from plotly.offline import plot as plotly_plot

from data.src.converter import Converter

class EMGData:
	"""
	Organize, process, and plot EMG data. Data is stored in a pandas DataFrame.
	"""

	def __init__(self, df, channelNames: list, timeName: str, eventName: str, frequency: float, maxDataPoints: int, windowTime: float) -> None:
		self.df = df

		self.channelNames = channelNames
		self.timeName = timeName
		self.eventName = eventName

		self.frequency = frequency
		self.maxDataPoints = int(maxDataPoints)
		self.windowTime = windowTime

	@classmethod
	def read_csv(cls, csv: str or object, channelNames: list, timeName: str, eventName: str, frequency: float=1024, maxDataPoints: int=1000, windowTime: float=1) -> 'EMGData':
		"""
		# Create EMGData object from a csv file.

		Parameters
		---
		csv : str or filelike object
			Path or filelike object for desired csv file containing EMG data.
		channelNames : list
			List of column names for EMG data channels.
		timeName : str
			Name of column containing time data.
		eventName : str
			Name of column containing event data.
		frequency : float, default 1024
			Sampling rate of EMG data in Hz.
		maxDataPoints : int, default 1000
			Maximum number of data points to be DISPLAYED by plots/figures; this will not affect the number of data points stored in the object.
		windowTime : float, default 1
			Time in seconds for moving average window.

		Returns
		---
		data : EMGData
			EMG data from csv file contained in EMGData object.
		"""
		df = pd.read_csv(csv)

		return cls(df, channelNames, timeName, eventName, frequency, maxDataPoints, windowTime)

	@classmethod
	def read_mat(cls, mat: str or object, channelNames: list, timeName: str, eventName: str, frequency: float=1024, maxDataPoints: int=1000, windowTime: float=1) -> 'EMGData':
		"""
		# Create EMGData object from a mat file.

		Parameters
		---
		mat : str or filelike object
			Path or filelike object for desired csv file containing EMG data.
		channelName : list
			List of column names for EMG data channels.
		timeName : str
			Name of column containing time data.
		eventName : str
			Name of column containing event data.
		frequency : float, default 1024
			Sampling rate of EMG data in Hz.
		maxDataPoints : int, default 1000
			Maximum number of data points to be DISPLAYED by plots/figures; this will not affect the number of data points stored in the object.
		windowTime : float, default 1
			Time in seconds for moving average window.

		Returns
		---
		data : EMGData
			EMG data from mat file contained in EMGData object.
		"""
		df = Converter().mat_to_df(mat).astype(float)

		return cls(df, channelNames, timeName, eventName, frequency, maxDataPoints, windowTime)

	def copy(self) -> 'EMGData':
		"""
		# Create a copy of the EMGData object.
		This new object is a deep copy, meaning that the dataframe is copied as well. All subsequent changes to the dataframe will not affect the original object.

		Parameters
		---
		None

		Returns
		---
		copy : EMGData
			Deep copy of EMGData object
		"""
		return EMGData(	self.df.copy(),
						deepcopy(self.channelNames),
						deepcopy(self.timeName),
						deepcopy(self.eventName),
						frequency=deepcopy(self.frequency),
						maxDataPoints=deepcopy(self.maxDataPoints),
						windowTime=deepcopy(self.windowTime))

	def __repr__(self) -> str:
		"""The class represended as a string."""
		return f'EMGData(DataFrame, {self.channelNames}, {self.timeName}, {self.eventName}, {self.frequency}, {self.maxDataPoints}, {self.windowTime})'

	def __str__(self) -> str:
		"""The class' most valuable information represented as a string."""
		return self.df.head().to_string()

	@property
	def period(self) -> float:
		"""Derive the period from the frequency. Units will be seconds."""
		return 1 / self.frequency

	@period.setter
	def period(self, val: float):
		self.frequency = 1 / val

	@property
	def idxs(self) -> slice:
		"""Slice of dataframe that limits its size to the maximum data points."""
		if len(self.df) < self.maxDataPoints:
			return slice(None)
		return slice(None, None, len(self.df) // self.maxDataPoints)

	@property
	def windowLength(self) -> int:
		"""Derive the window length from the window time over the period. Units will be seconds."""
		return int(self.windowTime // self.period)

	@property
	def channels(self) -> pd.DataFrame or pd.Series:
		"""Slice of the dataframe containing the EMG channels."""
		return self.df[self.channelNames]

	@channels.setter
	def channels(self, data: int or float or pd.Series or pd.DataFrame) -> None:
		self.df[self.channelNames] = data

	@property
	def time(self) -> pd.Series:
		"""Slice of the dataframe containing the time data."""
		return self.df[self.timeName]

	@time.setter
	def time(self, data: int or float or pd.Series) -> None:
		self.df[self.timeName] = data

	@property
	def event(self) -> pd.Series:
		"""Slice of the dataframe containing the event data."""
		return self.df[self.eventName]

	@event.setter
	def event(self, data: int or float or pd.Series) -> None:
		self.df[self.eventName] = data

	def find_columns(self, names: str or list) -> list:
		"""
		# Find columns with similar names.

		Parameters
		---
		names : str or list
			Name(s) of column(s) to find.

		Returns
		---
		columns : str or list
			The output of the find_columns function will always match the input, or there will be an exception.

		Raises
		---
		ValueError
			Type of columns found does not match type of names input.
		"""

		columns = []
		for name in names:
			columns += list(filter(lambda x: name in x, self.df.columns))

		if len(columns) == 0:
			raise ValueError('Column(s) could not be found:' + name)
		elif type(names) is str:
			if len(columns) > 1:
				raise ValueError('Multiple columns found with similar names: ' + str(columns) + '\nTo search for multiple columns please pass a list.')
			else:
				return columns[0]

		return columns

	def merge(self, other: 'EMGData') -> 'EMGData':
		"""
		# Merge two sets of EMG data together.

		Parameters
		---
		other : EMGData
			EMGData object to merge with.

		Returns
		---
		merged : EMGData
			New EMGData object containing a deep copy of the two dataframes merged together.

		Raises
		---
		ValueError
			The two dataframes are not compatible.
		"""
		if type(other) != EMGData:
			raise TypeError('Trying to add something other than another dataframe')
		elif self.channelNames == other.channelNames:
			raise ValueError('You cannot merge EMG data that has the same channel names.')
		elif self.frequency != other.frequency:
			raise ValueError('Samples collected with different frequency')

		left, right = self.df.copy(), other.df.copy()
		for df, obj in [(left, self), (right, other)]:
			df[obj.timeName] = obj.time.astype('int64')
			df = df.drop_duplicates(obj.timeName)

		df = pd.merge(left, right, 'inner', left_on=self.timeName, right_on=other.timeName)
		new = EMGData(df, self.channelNames + other.channelNames, self.timeName, self.eventName, self.frequency, self.maxDataPoints, self.windowTime)

		timestamps = new.find_columns(['Timestamp'])
		try:
			elapses = new.find_columns(['Elapsed'])
		except ValueError as err:
			elapses = []

		for colType, colName in [(timestamps, 'Timestamp'), (elapses, 'Elapse')]:
			if len(colType) > 1:
				new.df[colName] = new.df[colType[0]]
				for col in colType:
					new.df = new.df.drop(col, axis=1)
		if len(timestamps) > 1:
			new.timeName = 'Timestamp'

		return new


	def RMS(self, colNames, slidingWindow):
		"""
		# Calculate the Root-Mean-Square values for the specified columns.

		Parameters
		---
		colNames : str or list
			Name(s) of column(s) to return the RMS values for.

		Returns
		---
		RMS : pd.Series or pd.DataFrame
			Dataframe containing the input columns with calculates RMS values.
		"""
		new = pd.DataFrame()

		if type(colNames) != list:
			colNames = [colNames]

		for col in colNames:
			new[col] = self.df[col] ** 2    #Square terms
			new[col] = new[col].rolling(int((slidingWindow/1000.0)//self.period)).mean()  #Calculate mean over slidingWindow
			new[col] = new[col] ** (1/2)      #Calculate square roots

		return new


	def bandpassing(self, colNames):
		"""
		# Calculate the Bandpass values for the specified columns.

		Parameters
		---
		colNames : str or list
			Name(s) of column(s) to return the Bandpass values for.

		Returns
		---
		bandpassing : pd.Series or pd.DataFrame
			Dataframe containing the input columns bandpassed to specified cutoffs.
		"""
		if type(colNames) != list:
			colNames = [colNames]

		new = self.df[colNames].copy()

		#subtract mean from columns
		means = new.mean()
		new = means - new

		#rectify the signal
		new = new.abs()
		signal = new.to_numpy(dtype='float32')

		#bandpass the signal
		signal = signal.T

		#Could be treated as dynamic input variables
		order = 2
		lowcut = 3
		highcut = 0.01

		sos = butter(order, lowcut, 'lowpass', fs=1024, output='sos')

		signal = sosfilt(sos, signal)

		sos = butter(order, highcut, 'highpass', fs=1024, output='sos')

		signal = sosfilt(sos, signal)

		signal = signal.T
		for idx, col in enumerate(colNames):
			new[col] = signal[:,idx]

		return new

	def moving_average(self, colNames):
		"""
		# Calculate the moving average for the specified columns.

		Parameters
		---
		colNames : str or list
			Name(s) of column(s) to return the moving_average for.

		Returns
		---
		moving_average : pd.Series or pd.DataFrame
			Dataframe containing the input columns with calculates moving averages.
		"""
		new = pd.DataFrame()

		if type(colNames) != list:
			colNames = [colNames]

		for col in colNames:
			new[col] = self.df[col].rolling(self.windowLength).mean()

		return new

	def normalize(self, originalChannels, colNames: str or list=None) -> pd.Series or pd.DataFrame:
		"""
		# Normalize the data in the specified columns between 0-1.

		Parameters
		---
		colNames : str or list
			Name(s) of column(s) to normalize.

		Returns
		---
		normalized : pd.Series or pd.DataFrame
			Dataframe containing the input columns normalized between 0-1.
		"""
		colNames = colNames or self.channelNames

		new = pd.DataFrame()

		if type(colNames) is not list:
			colNames = [colNames]

		print(originalChannels, colNames)
		for col in colNames:
			if col in originalChannels:
				print(col)
				new[col] = self.df[col]
			else:
				max = self.df[col].max()
				min = self.df[col].min()
				new[col] = (self.df[col] - min) / (max - min)

		return new

	def quartiles(self, q: list or float=[0.9, 0.5, 0.1], columns: list or str=None) -> pd.DataFrame:
		"""
		# Calculate the specified quartiles of the data in the specified columns.

		Parameters
		---
		q : list or float, default [0.9, 0.5, 0.1]
			List of the quartiles to calculate, or a single quartile to calculate.
		columns : list or str, default self.channelNames
			Name(s) of column(s) to calculate the quartiles of.

		Returns
		---
		quartiles : pd.DataFrame
			Dataframe containing the specified quartiles of the specified columns.
		"""
		columns = columns or self.channelNames


		quartileTable = self.df[columns].quantile(q)

		percentileDictionary = {}
		for percentile in q:
			if percentile == 1.0:
				percentileDictionary[float(percentile)] = "Max"
			elif percentile == 0.0:
				percentileDictionary[float(percentile)] = "Min"
			else:
				percentileDictionary[float(percentile)] = str(int(percentile*100)) + "th"

		quartileTable = quartileTable.rename(index=percentileDictionary)
		quartileTable = quartileTable.rename_axis("Percentile")
		return quartileTable

	def find_events(self, eventsCol: str=None) -> list:
		"""
		# Find the beginning and ending indices of events in the data.

		Parameters
		---
		eventsCol : str, default self.eventName
			Name of the column containing the events.

		Returns
		---
		events : list
			List of tuples containing the beginning and ending indices of events.
		"""
		eventsCol = eventsCol or self.eventName
		new = pd.DataFrame()

		new['Toggle'] = self.df[eventsCol].diff()
		new = self.df.loc[abs(new['Toggle']) == 3]

		return [(new.iloc[i], new.iloc[i+1]) for i in range(0, len(new)-1, 2)]

	def figure(self, x: str=None, y: str or list=None, visible: list=None, eventMarkers: str=None) -> go.Figure:
		"""
		# Create a plotly express figure from the data.

		Parameters
		---
		x : str, default self.timeName
			Name of the column to use as the x-axis.
		y : str or list, default self.find_columns(['RMS', 'Moving Average', 'CH'])
			Name(s) of the column(s) to use as the y-axis.
		visible : list, default to all columns
			Name of the columns to make visible by default.
		eventMarkers : str, default to don't show
			Name of the column containing the events.

		Returns
		---
		fig : go.Figure
			Plotly express figure containing the EMG data. Data is sampled based on the maximum number of data points allowed.
		"""
		x =  x or self.timeName
		y = y or self.find_columns(['RMS', 'Moving Average', 'CH', 'Bandpass'])

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
			yaxis_title="Processed Values",
			legend_title="Data Source",
		)

		return fig

	def fig_to_html(self, fig: go.Figure) -> str:
		"""
		# Convert a plotly express figure to an HTML div string.

		Parameters
		---
		fig : go.Figure
			Plotly express figure to convert to an HTML div string.

		Returns
		---
		html : str
			HTML div string containing the plotly express figure.
		"""
		return plotly_plot(fig, include_plotlyjs=False, output_type='div')

	def data_to_html(self, x: str=None, y: list or str=None, visible=None, eventMarkers=None) -> str:
		"""
		# Convert EMG data to a plotly express figure contained inside of an HTML div string.

		Parameters
		---
		x : str, default self.timeName
			Name of the column to use as the x-axis.
		y : list or str, self.channelNames
			Name(s) of the column(s) to use as the y-axis.
		visible : list, default all visible
			Name of the columns to make visible by default.
		eventMarkers : str, default no events marked
			Name of the column containing the events.

		Returns
		---
		html : str
			HTML div string containing the plotly express figure.
		"""
		fig = self.figure(x, y, visible, eventMarkers)

		return self.fig_to_html(fig)

	def preprocess(self) -> 'EMGData':
		"""
		# Process the data to make it ready for analysis.

		Returns
		---
		new : EMGData
			EMGData object containing the processed data.
		"""
		new = self.copy()

		new.df['Elapse (s)'] = new.time.diff().fillna(0).cumsum() / 1000
		new.timeName = 'Elapse (s)'

		originalChannels = self.channelNames

		#Bandpass original Channels
		newChannels = ['Bandpass ' + channel[2:] for channel in self.channelNames]
		bandpassChannels = newChannels
		new.df[newChannels] = new.bandpassing(self.channelNames)
		new.channelNames += newChannels

		#Moving Average of Bandpass
		newChannels = ['Moving Average ' + channel[2:] for channel in self.channelNames]
		new.df[newChannels] = new.moving_average(bandpassChannels)
		new.channelNames += newChannels

		#RMS of Bandpass
		newChannels = ['RMS ' + channel[2:] for channel in self.channelNames]
		new.df[newChannels] = new.RMS(bandpassChannels, 100)
		new.channelNames += newChannels

		#Normalize all channels except original channels
		new.channels = new.normalize(originalChannels)     #re-implement with MVC

		return new


if __name__ == '__main__':
	print('No main function')

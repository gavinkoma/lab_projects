import numpy
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys

inFile = sys.argv[1]

def inputdata():
	#im not looping through all of your data, so we are using sys.argv to allow you to choose your data
	#python acc.py "input file"
	inFile = sys.argv[1]
	file_path = inFile  

	#read in text file. first split into two columns separated by ->
	df = pd.read_csv(file_path, header=None, delimiter=' -> ')

	#splitting the timestamp column into three separate columns
	split_timestamp = df[0].str.split(':', expand=True)
	df['Hour'] = split_timestamp[0].astype(int)
	df['Minute'] = split_timestamp[1].astype(int)

	#split seconds and milliseconds, converting to numbers
	seconds_and_milliseconds = split_timestamp[2].str.split('.', expand=True)
	df['Second'] = seconds_and_milliseconds[0].astype(int)
	df['Milliseconds'] = seconds_and_milliseconds[1].astype(int)

	df = df.drop(0, axis=1)

	#check dataframe to see if it worked
	#now we have hour minute second and millisecond
	print(df)

	#split the second column into separate columns for data point and coordinates
	split_data = df[1].str.split(',', expand=True)
	df['DataPoint'] = split_data[0].astype(int)
	df['X'] = split_data[1].astype(float)
	df['Y'] = split_data[2].astype(float)
	df['Z'] = split_data[3].astype(float)

	#dropping the original column '1' that contained the combined data
	df = df.drop(1, axis=1)

	#check dataframe to see if it worked
	#now we have x, y, z 
	#good
	print(df)

	#grouping by timestamp and calculate the mean of X, Y, Z, and Milliseconds values
	#doing it this way because we have 4 data points PER one timestamp
	grouped_data = df.groupby(['Hour', 'Minute', 'Second', 'Milliseconds']).agg({
		'DataPoint':'mean',
	    'X': 'mean',
	    'Y': 'mean',
	    'Z': 'mean'
	}).reset_index()

	#check dataframe as always, data is good
	#hour, minute, second, millisecond, datapoint, X, Y, Z
	print(grouped_data)
	return(grouped_data)


def min_max(grouped_data):
	#call proper dataframe from previous function
	df=grouped_data

	#calculate maximum and average values for X, Y, and Z
	#just a method for pulling extra info per each rat
	max_values = df[['X', 'Y', 'Z']].max()
	avg_values = df[['X', 'Y', 'Z']].mean()

	#creating bar plots for maximum and average values
	#could use different but its fine for visualization
	#put these in one graphic total one on top of other
	fig, axs = plt.subplots(2, 1, figsize=(8, 10))

	#bar plot for maximum values
	axs[0].bar(max_values.index, max_values.values, color='skyblue')
	axs[0].set_title('Maximum X, Y, Z Values')
	axs[0].set_ylabel('Values')

	#bar plot for average values
	axs[1].bar(avg_values.index, avg_values.values, color='lightgreen')
	axs[1].set_title('Average X, Y, Z Values')
	axs[1].set_ylabel('Values')

	plt.tight_layout()
	plt.show()


def soot_ball_graph(grouped_data):
	#call proper dataframe again
	df=grouped_data
	fig = plt.figure(figsize=(10, 8))
	ax = fig.add_subplot(111, projection='3d')

	#plotting X, Y, and Z values as a line plot in 3D
	#this doesnt account for distance so we gotta do that
	ax.plot(df['X'], df['Y'], df['Z'])

	ax.set_xlabel('X-axis')
	ax.set_ylabel('Y-axis')
	ax.set_zlabel('Z-axis')
	ax.set_title('3D Line Plot of X, Y, Z Values')

	plt.show()


def over_distance(grouped_data):
	#call dataframe
	df=grouped_data
	max_data_point = df['DataPoint'].max()
	total_distance = 5  # Total distance in feet

	#ccale the DataPoints to represent traversal over 5 feet
	df['ScaledDistance'] = (df['DataPoint'] / max_data_point) * total_distance

	fig = plt.figure(figsize=(10, 8))
	ax = fig.add_subplot(111, projection='3d')

	#plotting traversal of X, Y, and Z values over 5 feet in 3D
	ax.plot(df['ScaledDistance'], df['X'], df['Y'], label='Traversal', linestyle='-')

	ax.set_xlabel('Distance (Feet)')
	ax.set_ylabel('X-axis')
	ax.set_zlabel('Y-axis')

	ax.set_title('Traversal of X, Y, Z values over 5 Feet as a single line in 3D')
	ax.legend()

	plt.show()


def main():
	grouped_data=inputdata()
	min_max(grouped_data)
	soot_ball_graph(grouped_data)
	over_distance(grouped_data)


main()

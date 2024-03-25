#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: gavin



march 19, 2024
file pathway search is implemented with a user input sys arg
creation of csv of peak frame list tuple is created

graph of one video was output to check, start with graph creation next

march 22, 20204
plot works, not sure why i need to call the function first prior to def
automate pulling the rat name into the csv asap, that will help 
need to ask what min frame before is --> peak frames need to be 
	obtained for all in ms
velocity calculations need to be done but in order to that we 
	need to get the plexi_x and the plexi_y values from imageJ

"""
import datetime
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

def file_pathway():
	from datetime import datetime
	import csv
	now = datetime.now()

	pathway = input("Directory Pathway Please: ")
	pathway = str(pathway)

	#input adds an extra space at the end, we need to remove this:
	# using negative indexing
	pathway = pathway[:-1]
	print(pathway+"/")

	os_command = "find {} -type f -name '*.csv'".format(pathway)
	x = os.popen(os_command).read()
	x = x.split('\n')
	x = x[:-1]

	os_command = "find {} -type f -name '*.mp4'".format(pathway)
	y = os.popen(os_command).read()
	y = y.split('\n')
	y_vid = y[:-1]

	def prompt_peak_frame(file_path):
	    peak_frame = input(f"For the file path '{file_path}', what is the peak frame? ")
	    return peak_frame

	file_peak_frame_tuples = []
	for file_path in x:
		peak_frame = prompt_peak_frame(file_path)
		file_peak_frame_tuples.append((file_path,peak_frame))

	for file_path, peak_frame in file_peak_frame_tuples:
		print(file_path, "-> Peak Frame:",peak_frame)

	csv_filename = "file_data_{}.csv".format(now.strftime("%Y_%m_%d_%H_%M_%S"))
	with open(csv_filename,'w',newline='') as csvfile:
		fieldnames = ['file_path','peak_frame','start_frame','num_frame','around_peak_frame','marker']
		writer = csv.DictWriter(csvfile,fieldnames = fieldnames)

		writer.writeheader()
		for file_path,peak_frame in file_peak_frame_tuples:
			writer.writerow({'file_path': file_path,
							'peak_frame': peak_frame,
							'start_frame': int(0),
							'num_frame': int(1000),
							'around_peak_frame': int(200),
							'marker': str('wrist')
							})
	print("CSV written succesfully!")
	return pathway,x,y_vid

pathway,x,y_vid = file_pathway()

pathway = "/Users/gavinkoma/Documents/lab_projects/thomas_reaching/"

#need to pull the most recent csv file here
def pull_recent_csv(pathway):
	# Read the existing CSV file
	existing_data = []
	with open("existing_file.csv", "r") as f:
	    reader = csv.reader(f)
	    for row in reader:
	        existing_data.append(row)

	# Check if the lengths match
	if len(existing_data) != len(new_column_data):
	    print("Lengths of existing data and new column data do not match.")
	    exit()

	# Add the new column to the existing data
	for i, row in enumerate(existing_data):
	    row.append(new_column_data[i])

	# Write the modified data back to the CSV file
	with open("existing_file.csv", "w", newline="") as f:
	    writer = csv.writer(f)
	    writer.writerows(existing_data)


	return()





def pull_frame(df):
	file_paths_column = df['file_path']
	import subprocess

	def perform_action(directory):
		# Your custom action here
		print(f"Performing action in directory: {directory}")
		# For example, you can list files in the directory or do any other operation
		ffmpeg_command =[
			"ffmpeg",
			"-i",
			file_path,
			"-ss",
			"1",
			"-q:v",
			"2",
			directory]

		subprocess.run(ffmpeg_command)

	for file_path in file_paths_column:
		directory = os.path.dirname(file_path)  # Extract the directory part of the file path
	    if os.path.exists(directory) and os.path.isdir(directory):
	        os.chdir(directory)  # Enter the directory
	        perform_action(directory)  # Perform your action in the directory
	        os.chdir('..')  # Move back to the parent directory
		else:
	    	print(f"Directory does not exist: {directory}")
	return

pull_frame(df)
'''

def load_file_():
	idx = pd.IndexSlice
	plt.rc('legend',fontsize=8)
	pathway = input("MetaData File Please: ")
	pathway = str(pathway)
	pathway = pathway[:-1]
	print(pathway+"/")

	def fixtheindex(df):
	  if isinstance(df.index[0],str):
	    print("Fixing index.")
	    df.index = range(0,len(df))
	  return(df)

	md=pd.read_csv('{}'.format(pathway))
	# %% okay laod them on to same time
	dfs=[]
	for ind in range(len(md)):
	  df=pd.read_csv(md.loc[ind,'file_path'],index_col=0,header=[0,1,2])
	  df=fixtheindex(df)
	  df.loc[:,idx[:,:,['x','y']]]=df.loc[:,idx[:,:,['x','y']]].rolling(6,center=True).mean()
	  dfs.append(df)
	md=pd.read_csv('{}'.format(pathway))
	return md,dfs

md,dfs = load_file_()

def fixtheindex(df):
	if isinstance(df.index[0],str):
    	print("Fixing index.")
    	df.index = range(0,len(df))
	return(df)

def plot_reach(fn):
	df = pd.read_csv(fn,index_col = 0, header = [0,1,2])
	df = fixtheindex(df)
	xco = df.loc[:,idx[:,:,'x']]
	yco = df.loc[:,idx[:,:,'y']]

	#skeee yeeee
	fig, axes = plt.subplots(nrows = 2, ncols = 1)
	xco.plot(ax=axes[0])
	yco.plot(ax=axes[1])

	fig.suptitle(fn,fontsize=4)
	axes[0].set_ylabel('x coord')
	axes[1].set_xlabel('frame')
	axes[1].set_ylabel('y coord')
	axes[1].invert_yaxis()

	#save
	#axes[0].axhline(xwall)
	#axes[1].axhline(700-ywall)
	fig.savefig(fn.split('.')[0]+'.png')
	return

#we need to define the plexi_x and the plexi_y of the videos 
ind=0
idx = pd.IndexSlice
plot_reach(md.iloc[ind]['file_path'])#,md.loc[ind,'plexi_x'],md.loc[ind,'plexi_y'])
plt.show()
fn=md.iloc[ind]['file']
#xwall=md.loc[ind,'plexi_x']
#ywall=md.loc[ind,'plexi_y']


'''


xmin,ymin,xpk,ypk,rchdur,dx,dy,velx,vely =[],[],[],[],[],[],[],[],[]
for ind in range(len(md)):
	print(md.loc[ind,'file_path'])
	df=pd.read_csv(md.loc[ind,'file_path'],index_col=0,header=[0,1,2])
	df=fixtheindex(df)
	df.columns=df.columns.droplevel('scorer')
    xmin.append(df.loc[md['minframebef'][ind],idx[md['marker'][ind],'x']]/pixpermm)
    ymin.append(df.loc[md['minframebef'][ind],idx[md['marker'][ind],'y']]/pixpermm)
    xpk.append(df.loc[md['peakframe'][ind],idx[md['marker'][ind],'x']]/pixpermm)
    ypk.append(df.loc[md['peakframe'][ind],idx[md['marker'][ind],'y']]/pixpermm)
    rchdur.append( (md['peakframe'][ind] - md['minframebef'][ind])/fps )
    dx.append( (xpk[-1]-xmin[-1])/pixpermm  )
    dy.append( (ypk[-1]-ymin[-1])/pixpermm )
    velx.append( dx[-1]/rchdur[-1] )
    vely.append( dy[-1]/rchdur[-1] )
mdwv=md.copy()
mdwv=mdwv.assign(xmin=xmin,ymin=ymin,xpk=xpk,ypk=ypk,rchdur=rchdur,dx=dx,dy=dy,velx=velx,vely=vely)
mdwv.to_csv('reachfiles_generated_wvelocities.csv')



'''
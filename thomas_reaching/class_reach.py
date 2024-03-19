#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: gavin



march 19, 2024
file pathway search is implemented with a user input sys arg
creation of csv of peak frame list tuple is created

graph of one video was output to check, start with graph creation next


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
		fieldnames = ['file_path','peak_frame']
		writer = csv.DictWriter(csvfile,fieldnames = fieldnames)

		writer.writeheader()
		for file_path,peak_frame in file_peak_frame_tuples:
			writer.writerow({'file_path': file_path,
							'peak_frame': peak_frame
							})

	print("CSV written succesfully!")

	return pathway,x

pathway,x = file_pathway()

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

ind=0
plot_reach(md.iloc[ind]['file_path'],md.loc[ind,'plexi_x'],md.loc[ind,'plexi_y'])
plt.show()
fn=md.iloc[ind]['file']
xwall=md.loc[ind,'plexi_x']
ywall=md.loc[ind,'plexi_y']




















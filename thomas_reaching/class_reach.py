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
import subprocess
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages


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
	root_directory = pathway

	def get_csv_paths(root_dir):
		data = []

		#walk through
		for root, dirs, files in os.walk(root_dir):
			for file in files:
				if file.endswith(".csv") and "metadata" not in file.lower():
					rel_path = os.path.relpath(root,start=root_dir)
					dirs_list = rel_path.split(os.path.sep)
					dirs_list.append(file)
					data.append(dirs_list)

		return data

	csv_file_paths = get_csv_paths(root_directory)
	df = pd.DataFrame(csv_file_paths)

	os_command = "find {} -type f -name '*.csv' ! -iname '*metadata*' -exec ls {{}} \;".format(pathway)
	x = os.popen(os_command).read()
	x = x.split('\n')
	x = x[:-1]

	def prompt_peak_frame(file_path):
	   peak_frame = input(f"For the file path '{file_path}', what is the peak frame? ")
	   return peak_frame

	file_peak_frame_tuples = []

	for input_ in x:
		#print(input_)
		peak_frame = prompt_peak_frame(input_)
		file_peak_frame_tuples.append((input_,peak_frame))

	for file_path, peak_frame in file_peak_frame_tuples:
		print(file_path, "-> Peak Frame:",peak_frame)

	df = df.rename(columns={0:'exp_type'})
	df = df.rename(columns={1:'cam_num'})
	df = df.rename(columns={2:'ratnum'})
	df = df.rename(columns={3:'date'})
	df = df.rename(columns={4:'csv_name'})

	file_peak_frame_tuples = pd.DataFrame(file_peak_frame_tuples)
	file_peak_frame_tuples = file_peak_frame_tuples.rename(columns={0:'file_path'})
	file_peak_frame_tuples = file_peak_frame_tuples.rename(columns={1:'peak_frame'})
	tryatt = pd.concat([df,file_peak_frame_tuples],axis=1)

	length = len(tryatt)
	tryatt['start_frame'] = 0
	tryatt['num_frame'] = 1000
	tryatt['around_peak_frame']= 200
	tryatt['marker'] = 'wrist'
	tryatt['plexi_x'] = ''
	tryatt['plexi_y'] = ''
	tryatt['plexipixwidth'] = ''
	tryatt['pixpermm'] = ''
	#tryatt['video_path'] = y_vid
	tryatt['goodbad'] = 'good'
	tryatt['fixind'] = 0

	csv_filename = "file_data_{}.csv".format(now.strftime("%Y_%m_%d_%H_%M_%S"))

	tryatt.to_csv(csv_filename,index=False)
	print("CSV written succesfully!")
	df = tryatt


	return df

df = file_pathway()

def read_most_recent_csv(directory_path):
    # Get a list of all CSV files in the directory
    csv_files = [file for file in os.listdir(directory_path) if file.endswith(".csv")]

    #if there are CSV files in the directory
    if csv_files:
        #find the most recent CSV file based on modification time
        most_recent_file = max(csv_files, key=lambda x: os.path.getmtime(os.path.join(directory_path, x)))
        
        #fonstruct the full path to the most recent CSV file
        most_recent_file_path = os.path.join(directory_path, most_recent_file)
        
        #read the most recent CSV file into a pandas DataFrame
        df = pd.read_csv(most_recent_file_path)
        
        return df,most_recent_file_path

    else:
        print("No CSV files found in the directory.")
        return None

#output the first frame of every video
directory_path = '/Users/gavinkoma/Documents/lab_projects/thomas_reaching'
df,most_recent_file_path = read_most_recent_csv(directory_path)
md = read_most_recent_csv(directory_path)

#this will be used to pull a file name from every video in the subdirectories. 
def extract_first_frame(video_path):
	video_directory = os.path.dirname(video_path)
	os.chdir(video_directory)

	video_filename = os.path.basename(video_path)
	video_name_without_extension = os.path.splitext(video_filename)[0]

	output_file_name = f"{video_name_without_extension}.jpg"

		#run ffmpeg command to extract the first frame
    ffmpeg_command = [
        "ffmpeg",
        "-i", video_filename,
        "-ss", "00:00:01",  #time to extract frame from (adjust as needed)
        "-vframes", "1",     #number of frames to extract
        "-q:v", "2",         #quality of the extracted frame
        output_file_name
    ]

    subprocess.run(ffmpeg_command)

def populate_videos():

	pathway = input("Directory Pathway Please: ")
	pathway = str(pathway)

	os_command = "find {} -type f -name '*.mp4'".format(pathway)
	y = os.popen(os_command).read()
	y = y.split('\n')
	video_paths = y[:-1]
	return video_paths

video_paths = populate_videos()

for video_path in video_paths:
	extract_first_frame(video_path)

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
	#fig.savefig(fn.split('.')[0]+'.png')
	return

#we need to define the plexi_x and the plexi_y of the videos 
#this outputs the first graph
def create_pdf_singleplot(md):
	ind=0
	idx = pd.IndexSlice
	plot_reach(md.iloc[ind]['file_path'])#,md.loc[ind,'plexi_x'],md.loc[ind,'plexi_y'])
	#plt.show()
	fn=md.iloc[ind]['file_path']

	pdf_pages = PdfPages('singleplots.pdf')

	with PdfPages('singleplots.pdf') as pdf_pages:
		for file_ in md['file_path']:
			plot_reach(file_)
			pdf_pages.savefig()
			plt.close()

	pdf_pages.close()
create_pdf_singleplot(md)


def load_file_():
	idx = pd.IndexSlice
	plt.rc('legend',fontsize=8)
	pathway = input("Guidance Data File Please: ")
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

'''
#this does not work god dammit
cleaned_df_list = [df.fillna(0) for df in dfs]

metadata_df = md  

for index, row in metadata_df.iterrows():
	marker_of_interest = row['marker']
	experiment_type = row['exp_type']
	peak_frame = row['peak_frame']
	start_frame = max(0, peak_frame - 100)
	end_frame = min(len(data_df), peak_frame + 101)

	file_path = row['file_path']
	data_df = pd.read_csv(file_path,skiprows=1)
	x_values = data_df[('wrist')]
    
	color = {'preinj': 'blue', 'post_slash': 'green', 'postDTA': 'red'}
	plt.plot(range(len(x_values)), x_values, color=color[experiment_type], label=experiment_type)

plt.xlabel('frame_number')
plt.ylabel('x_values')
plt.title('x interest')
#plt.show() 
'''

#FUCK
#why dont we start by populating a list of dataframes that correspond to the values we are hunting for
#we want two lists: left and right
#we want these lists to index wrist AND 'good'

dataframes_to_plot = []
count =0
range_values = [tuple()]
right = []
left = []
for ind in range(len(md)):
	rng=range(round((md.loc[ind,'peak_frame']-(md.loc[ind,'around_peak_frame']/2))), \
		round((md.loc[ind,'peak_frame']+(md.loc[ind,'around_peak_frame']/2))))
	range_values.append(rng)
#for index,row in md.iterrows():
for index,row in md.iterrows():
	if row['goodbad'] == 'good' and row['handedness'] == 'right':
		secondary_df = pd.read_csv(row['file_path'])
		new_headers = secondary_df.iloc[:2]
		secondary_df = secondary_df.iloc[2:]
		secondary_df.columns = new_headers.values.tolist()
		secondary_df = secondary_df['wrist','x']
		right.append(secondary_df)
		count = count+1
print("total right hand df: " + str(count))

count = 0
for index,row in md.iterrows():
	if row['handedness'] == 'left':
		secondary_df = pd.read_csv(row['file_path'])
		new_headers = secondary_df.iloc[:2]
		secondary_df = secondary_df.iloc[2:]
		secondary_df.columns = new_headers.values.tolist()
		secondary_df = secondary_df['wrist','x']
		left.append(secondary_df)
		count = count+1
print("total left hand df: " + str(count))

#dataframes pull wrist successfully and create a new list of x data values
#we need to slice each of these data frames in the list around the peak frame values supplied in
#our metadata csv

# STUFF BELOW WORKING
# TODO
# 1. In code below, after newdf=(dfs[ind].loc[rng,idx[:,md.loc[ind,'marker'],'x']].reset_index() - md.loc[ind,'plexi_x'])/md.loc[ind,'pixpermm']
# do if(hand==left) then x=-x.
idx=pd.IndexSlice
fps=250
md=pd.read_csv("file_data_2024_03_26_13_40_28.csv")
# workin ghere
f=plt.figure(2)
f.clf()
#f.set_figheight(1.32)
#f.set_figwidth(2.87)
#f=plt.figure(figsize=(2.87,1,32))
#cols={'inhib':'green','control':'blue','excite':'red','norm':'black'}
subs=[]
cols = {'preinj': 'blue', 'post_slash': 'green', 'postDTA': 'red'}
# create mapping of unique treatments to themselves
legendlabs = dict(zip(md.loc[:,'exp_type'].unique(),md.loc[:,'exp_type'].unique()))
for ind in range(len(md)):
  rng=range(round((md.loc[ind,'peak_frame']-(md.loc[ind,'around_peak_frame']/2))), \
      round((md.loc[ind,'peak_frame']+(md.loc[ind,'around_peak_frame']/2))))
  # YIKES should not do this here and below in newdf for export... should be same compute...
  #xco=(dfs[ind].loc[:,idx[:,md.loc[ind,'marker'],'x']] - md.loc[ind,'plexi_x'])/md.loc[ind,'pixpermm']
  if md.loc[ind,'goodbad']=='good':
    repdf=md.loc[[ind]*len(rng)].reset_index() # repeated meta entries of md
    repdf['frame']=repdf.index
    newdf=(dfs[ind].loc[rng,idx[:,md.loc[ind,'marker'],'x']].reset_index() - md.loc[ind,'plexi_x'])/md.loc[ind,'pixpermm']
    newdf.columns=newdf.columns.droplevel([0,1])
    newdf['frame']=newdf.index
    outdf=newdf.join(repdf,on='frame',rsuffix='_md').rename({'exp_type':'treatment'},axis='columns')
    #outdf['time']=(outdf['frame']-md.loc[ind,'aroundpeakframes']/2)/fps
    outdf['time']=(outdf['frame'])/fps
    if any(np.isnan(outdf['x'])):
      print('Found nans in ',md.loc[0,'file'], ' interpolating...')
      outdf['x']=outdf['x'].interpolate()
    subs.append(outdf)
    #plt.plot( outdf['time'], outdf['time'], c=cols[md.loc[ind,'exp_type']], label=legendlabs[md.loc[ind,'exp_type']] )
    # should plot outdf here not xco!
    plt.plot( outdf['time'], outdf['x'], \
      c=cols[md.loc[ind,'exp_type']], label=legendlabs[md.loc[ind,'exp_type']] )
    plt.text( outdf['time'][round(md.loc[ind,'around_peak_frame']/4)], outdf['x'][round(md.loc[ind,'around_peak_frame']/4)], 
    	str(ind) )
    #plt.plot( outdf['time'], np.array(xco.iloc[rng].droplevel([0,1],axis='columns')), \
    #  c=cols[md.loc[ind,'exp_type']], label=legendlabs[md.loc[ind,'exp_type']] )
    legendlabs[md.loc[ind,'exp_type']]='_'+legendlabs[md.loc[ind,'exp_type']]
#    plt.plot( range(md.loc[ind,'aroundpeakframes']), \
#      xco.loc[ round((md.loc[ind,'peakframe']-(md.loc[ind,'aroundpeakframes']/2))): \
#      round((md.loc[ind,'peakframe']+(md.loc[ind,'aroundpeakframes']/2))-1) ], c=cols[md.loc[ind,'exp_type']])
#plt.axhline(md.loc[1,'plexi_x'])
plt.axhline(0)
plt.xlabel('time (s)')
plt.ylabel('wrist x (mm)')
plt.legend(title='treatment')
plt.title('Individual reaches by treatment')
plt.annotate('Wall', xy=(0.2, 0),  xycoords='data',
            xytext=(0.2, 10), textcoords='data',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='center', verticalalignment='center',
            )
ad = pd.concat(subs).reset_index()
ad.to_csv('alldata_x.csv')
plt.savefig('indivreach_x.pdf')

# try the seaborn
# %% plot with shaded errors
# Plot the responses for different events and regions
f3=plt.figure(3)
f3.clf()
sns.lineplot(x="time", y="x",ci="sd",hue="treatment",palette=cols,data=ad)
plt.axhline(0)
plt.xlabel('time (s)')
plt.ylabel('wrist x (mm)')
plt.title('Mean $\pm$ S.D. reaches by treatment')
plt.annotate('Wall', xy=(0.2, 0),  xycoords='data',
            xytext=(0.2, 10), textcoords='data',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='center', verticalalignment='center',
            )
plt.savefig('meansdreach_x.pdf')


## end stuff we got through.




























# %% okay laod them on to same time
dfs=[]
idx=pd.IndexSlice
for ind in range(len(md)):
  df=pd.read_csv(md.loc[ind,'file_path'],index_col=0,header=[0,1,2])
  df=fixtheindex(df)
  df.loc[:,idx[:,:,['x','y']]]=df.loc[:,idx[:,:,['x','y']]].rolling(6,center=True).mean()
  dfs.append(df)


# %% function that loads and plots one file
def plotreachkinfile(fn,xwall,ywall):
  df=pd.read_csv(fn,index_col=0,header=[0,1,2])
  # some files have file names as the index, manually annotated i think.
  # fix...
  #if isinstance(df.index[0],str):
  #  print("Fixing index.")
  #  df.index = range(0,len(df))
  df=fixtheindex(df)
  # plot the x coords and
  # get x and y coordinates
  xco = df.loc[:,idx[:,:,'x']]
  yco = df.loc[:,idx[:,:,'y']]
  # plot it up:
  fig, axes = plt.subplots(nrows=2, ncols=1)
  xco.plot(ax=axes[0])
  yco.plot(ax=axes[1])
  fig.suptitle(fn,fontsize=4)
  axes[0].set_ylabel('x coord')
  axes[1].set_xlabel('frame')
  axes[1].set_ylabel('y coord')
  axes[1].invert_yaxis()
  # save it
  axes[0].axhline(xwall)
  axes[1].axhline(700-ywall)
  fig.savefig(fn.split('.')[0]+'.png')
  #plt.show()

if 0:
  ind=0
  plotreachkinfile(md.iloc[ind]['file'],md.loc[ind,'plexi_x'],md.loc[ind,'plexi_y'])
  plt.show()
  fn=md.iloc[ind]['file']
  xwall=md.loc[ind,'plexi_x']
  ywall=md.loc[ind,'plexi_y']

f=plt.figure(2)
f.clf()

#we have metadata loaded
#clean the NaNs from the list of dataframes
#cleaned_df_list = [df.fillna(0) for df in dfs]
fps=250
f=plt.figure(2)
f.clf()
md = pd.read_csv(most_recent_file_path)
cols={'preinj':'green','post_slash':'blue','postDTA':'red'}
subs=[]
legendlabs = dict(zip(md.loc[:,'exp_type'].unique(),md.loc[:,'exp_type'].unique()))
for ind in range(len(md)):
	rng=range(round((md.loc[ind,'peak_frame']-(md.loc[ind,'around_peak_frame']/2))),round((md.loc[ind,'peak_frame']+(md.loc[ind,'around_peak_frame']/2))))
if md.loc[ind,'goodbad']=='good': #and md.loc[ind,'handedness']=='right':
	repdf=md.loc[[ind]*len(rng)].reset_index() # repeated meta entries of md
	repdf['frame']=repdf.index
	newdf=(dfs[ind].loc[rng,idx[:,md.loc[ind,'marker'],'x']].reset_index() - md.loc[ind,'plexi_x'])/md.loc[ind,'pixpermm']
	newdf.columns=newdf.columns.droplevel([0,1])
	newdf['frame']=newdf.index
	outdf=newdf.join(repdf,on='frame',rsuffix='_md').rename({'exp_type':'treatment'},axis='columns')
	outdf['time']=(outdf['frame'])/fps
	if any(np.isnan(outdf['x'])):
		print('Found nans in ',md.loc[0,'file_path'], ' interpolating...')
		outdf['x']=outdf['x'].interpolate()
	subs.append(outdf)
	plt.plot( outdf['time'], outdf['x'], c=cols[md.loc[ind,'exp_type']], label=legendlabs[md.loc[ind,'exp_type']] )
	legendlabs[md.loc[ind,'exp_type']]='_'+legendlabs[md.loc[ind,'exp_type']]


'''
plt.axhline(0)
plt.xlabel('time (s)')
plt.ylabel('wrist x (mm)')
plt.legend(title='treatment')
plt.title('Individual reaches by treatment')
plt.annotate('Wall', xy=(0.2, 0),  xycoords='data',
            xytext=(0.2, 10), textcoords='data',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='center', verticalalignment='center',
            )
ad = pd.concat(subs).reset_index()
ad.to_csv('alldata_x.csv')
plt.savefig('indivreach_x.pdf')
'''





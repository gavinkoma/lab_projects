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
	root_directory = pathway

	def get_csv_paths(root_dir):
		data = []

		#walk through
		for root, dirs, files in os.walk(root_dir):
			for file in files:
				if file.endswith(".csv"):
					rel_path = os.path.relpath(root,start=root_dir)
					dirs_list = rel_path.split(os.path.sep)
					dirs_list.append(file)
					data.append(dirs_list)

		return data

	csv_file_paths = get_csv_paths(root_directory)
	df = pd.DataFrame(csv_file_paths)

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

	for input_ in x:
		#print(input_)
		peak_frame = prompt_peak_frame(input_)
		file_peak_frame_tuples.append((input_,peak_frame))

	for file_path, peak_frame in file_peak_frame_tuples:
		print(file_path, "-> Peak Frame:",peak_frame)

	df = df.rename(columns={0:'exp_type'})
	df = df.rename(columns={1:'ratnum'})
	df = df.rename(columns={2:'date'})
	df = df.rename(columns={3:'csv_name'})

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
	

	csv_filename = "file_data_{}.csv".format(now.strftime("%Y_%m_%d_%H_%M_%S"))

	tryatt.to_csv(csv_filename,index=False)
	print("CSV written succesfully!")

	return df

df = file_pathway()







'''
def get_csv_paths(root_dir):
	date = []

	#walk through
	for root, dirs, files in os.walk(root_dir):
		for file in files:
			if file.endswith(".csv"):
				rel_path = os.path.relpath(root,start=root_dir)
				dirs_list = rel_path.split(os.path.sep)
				dirs_list.append(file)
				data.append(dirs_list)

	return data
'''


csv_file_paths = get_csv_paths(root_directory)
df = pd.DataFrame(csv_file_paths)

def read_most_recent_csv(directory_path):
    # Get a list of all CSV files in the directory
    csv_files = [file for file in os.listdir(directory_path) if file.endswith(".csv")]

    # If there are CSV files in the directory
    if csv_files:
        # Find the most recent CSV file based on modification time
        most_recent_file = max(csv_files, key=lambda x: os.path.getmtime(os.path.join(directory_path, x)))
        
        # Construct the full path to the most recent CSV file
        most_recent_file_path = os.path.join(directory_path, most_recent_file)
        
        # Read the most recent CSV file into a pandas DataFrame
        df = pd.read_csv(most_recent_file_path)
        
        return df,most_recent_file_path

    else:
        print("No CSV files found in the directory.")
        return None


#output the first frame of every video
directory_path = '/Users/gavinkoma/Documents/lab_projects/thomas_reaching'
df,most_recent_file_path = read_most_recent_csv(directory_path)
# print(most_recent_file)
y_vid = pd.DataFrame(y_vid)
y_vid.columns = ['video_path']
df = pd.concat([df,y_vid],axis = 1)
df["plexi_x"] = ''
df["plexi_y"] = ''
df.to_csv(most_recent_file_path,index = False)



#this will be used to pull a file name from every video in the subdirectories. 
def extract_first_frame(video_path):
	video_directory = os.path.dirname(video_path)
	os.chdir(video_directory)

	video_filename = os.path.basename(video_path)
	video_name_without_extension = os.path.splitext(video_filename)[0]

	output_file_name = f"{video_name_without_extension}.jpg"

		# Run ffmpeg command to extract the first frame
    ffmpeg_command = [
        "ffmpeg",
        "-i", video_filename,
        "-ss", "00:00:01",  # Time to extract frame from (adjust as needed)
        "-vframes", "1",     # Number of frames to extract
        "-q:v", "2",         # Quality of the extracted frame
        output_file_name
    ]

    subprocess.run(ffmpeg_command)

video_paths = df["video_path"]
for video_path in video_paths:
	extract_first_frame(video_path)






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
import matplotlib.pyplot as plt
import pandas as pd 
import os
idx = pd.IndexSlice

#lets view and assess the data first 
ajay = pd.read_hdf("/Users/gavinkoma/Documents/lab_projects/ajay_kinematics/data/alldata.h5")
ajay = ajay.iloc[3:]
#view as below, see head:
print(ajay.head(4))
#we have collarbone --> shoulder --> elbow --> wrist 
datadir='../data'
ds = ajay
ds.index=ds.index.set_names(['video','frame'])

dsj = ds.groupby(['video'],group_keys=False)


# get intersection of videos in metadata and dataset
#vids=list(set(ds.index) & set(ds.index.get_level_values('video').unique()))

#alright lets make a few plots i guess, would be worth it to assess what were looking at 
#we can groupby video name and then plot those for our assessment 
#probably will take a good bit though just because of the overall size

def create_plots(x,y):
	#we will want a line plot that shows the x and y coordinates
	#and we will want to calculate the angle around the elbow 
	#maybe calculate the angle around the shoulder as well 
	#height? velocity? distance? 
	pass 

def calc_vel():
	pass

def calc_heigh():
	pass




# create_plots(ajay)






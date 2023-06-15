import matplotlib.pyplot as plt
import pandas as pd 
import os
idx = pd.IndexSlice

#lets view and assess the data first 
ajay = pd.read_hdf("/Users/gavinkoma/Documents/lab_projects/ajay_kinematics/data/alldata.h5")
#ajay = ajay.iloc[3:]
#view as below, see head:
print(ajay.head(4))
#we have collarbone --> shoulder --> elbow --> wrist 
#lets take a second and see what keys were working with
for k in ajay.keys():
	print(k)

#the colon behind collarbone means all scoreers 
first = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Collarbone',['x','y']]]
elb = ajay.loc[idx[:,:],idx[:,'Elbow',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
wri = ajay.loc[idx[:,:],idx[:,'Wrist',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')


euc = (elb-wri).rename(columns={"x":"dx",
								"y":"dy"})


#we should probably do the joint angles

euc["ewdist"]=np.sqrt((euc["dx"]**2)+(euc["dy"]**2))



first.index.get_level_values('video').unique()

#alright lets make a few plots i guess, would be worth it to assess what were looking at 
#we can groupby video name and then plot those for our assessment 
#probably will take a good bit though just because of the overall size
#lets make a lil val for the euc distance location

def euc_distance():
	pass 

def create_plots():
	pass 

def calc_vel():
	pass

def calc_height():
	pass




# create_plots(ajay)






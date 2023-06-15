import os 
import matplotlib.pyplot as pls
import pandas as pd
import numpy as np 
idx = pd.IndexSlice

#lets take a second to read in the data we are looking at 
ajay = pd.read_hdf("/Users/gavinkoma/Documents/lab_projects/ajay_kinematics/data/alldata.h5")

#lets take a second and see what keys were working with
for k in ajay.keys():
	print(k)

#read in the x & y of the wrist, elbow, shoulder, and back
wri = ajay.loc[idx[:,:],idx[:,'Wrist',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
elb = ajay.loc[idx[:,:],idx[:,'Elbow',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
shou = ajay.loc[idx[:,:],idx[:,'Shoulder',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
back = ajay.loc[idx[:,:],idx[:,'Collarbone',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')


def calc_diff(part1,part2):
	return (part1-part2).rename(columns={"x":"dx",
								"y":"dy"})

def euc_dist(diff):
	return np.sqrt((diff["dx"]**2)+(diff["dy"]**2))

#calculate whhichever euclidean distances we want to do 
elb_wri = calc_diff(elb,wri)
euc_elb_wri = euc_dist(elb_wri)








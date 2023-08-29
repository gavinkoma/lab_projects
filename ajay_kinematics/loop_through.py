
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np 
import math
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
col = ajay.loc[idx[:,:],idx[:,'Collarbone',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')

def calc_diff(part1,part2):
	return (part1-part2).rename(columns={"x":"dx",
								"y":"dy"})

def euc_dist(diff):
	return np.sqrt((diff["dx"]**2)+(diff["dy"]**2))

#calculate whhichever euclidean distances we want to do 
#we might as well do all of them and this is fine because we can 
#just pass the previously written functions these values
elb_wri = calc_diff(elb,wri)
euc_elb_wri = euc_dist(elb_wri)

sho_elb = calc_diff(shou,elb)
euc_sho_elb = euc_dist(sho_elb)

col_sho = calc_diff(col,shou)
euc_col_elb = euc_dist(col_sho)

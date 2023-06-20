
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

#read in the x & y of the wrist, elbow, shoulder, and back
wri = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Wrist',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
elb = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Elbow',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
shou = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Shoulder',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
col = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Collarbone',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')

#we need to create tuples of coordinates, elbow should be in the middle of all!
def tuple_line(data):
	#pass whatever values you need to tuple
	return list(data.itertuples(index=False, name=None))

# #pass the new tuple lists to make one conjoined list of paired coordinates
# #for calculation of segment angles
# def merge_tuples(list1, list2):
# 	return [(list1[i], list2[i]) for i in range(0, len(list1))]

# #for calculation of segment angles
# def merge(list1, list2):
# 	return tuple(zip(list1, list2))

def mydot(vA,vB):
	return vA[:,0]*vB[:,0] + vA[:,1]*vB[:,1]

def normalization(a):
	return np.sqrt(np.sum(a**2,axis=1))

def joint_angle_elbow(wri,elb,shou):
	# #merge the tuples so they are actually lines
	# wri_elb = merge_tuples(wri_tuple,elb_tuple)
	# elb_shou = merge_tuples(elb_tuple,shou_tuple)
	line_ba = np.array(elb) - np.array(wri)
	line_bc = np.array(elb) - np.array(shou)
	cosine_angle = mydot(line_ba,line_bc) / (normalization(line_ba) * normalization(line_bc))
	cosine_angle = np.degrees(np.arccos(cosine_angle))
	plt.ion()
	plt.figure()
	plt.show()
	plt.plot(range(len(cosine_angle)),cosine_angle)
	return print(cosine_angle)

#put our values in a nice vector form
wri_vector_x_ = -np.diff(wri.iloc[:,0])
wri_vector_y_ = -np.diff(wri.iloc[:,1])

elb_vector_x_ = -np.diff(elb.iloc[:,0])
elb_vector_y_ = -np.diff(elb.iloc[:,1])

shou_vector_x_ = -np.diff(shou.iloc[:,0])
shou_vector_y_ = -np.diff(shou.iloc[:,1])

joint_angle_elbow(wri,elb,shou)

#segment angles are in reference to the ground ! 
#we need a line that can function as the reference to the ground 
#lets suppose that the following works:
#it would be nice to make this kind of dynamic lol 

#keep shoulder and elbow line the same 
#make a new line from elbow to maybe like 50 points over
#we want the x coordinate to change and leave the y coordinate to be same
#lets create these new lists for these data points pls 

#list your inputs from top to bottom, this is important because this 
#is how i want to design this function

def reference_line(extend):
	reference_line_elbow = []
	reference_elbow = pd.DataFrame()
	for val in extend.iloc[:,0]:
		x_val = val + 50
		#print(x_val)
		reference_line_elbow.append(x_val)
	extend['ref_x'] = reference_line_elbow

	reference_line_elbow = []
	for val in extend.iloc[:,1]:
		y_val = val
		#print(x_val)
		reference_line_elbow.append(y_val)
	extend['ref_y'] = reference_line_elbow
	return extend

shoulder_new = reference_line(shou)
shoulder_new.drop(shoulder_new.columns[[0, 1]], axis=1, inplace=True)
elb_new = reference_line(elb)
elb_new.drop(elb_new.columns[[0, 1]], axis=1, inplace=True)
wrist_new = reference_line(wri)
wrist_new.drop(wrist_new.columns[[0, 1]], axis=1, inplace=True)
wri = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Wrist',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
elb = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Elbow',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
shou = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Shoulder',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')

#our new issue is that the reference line will give us a value of 0 and that literally makes 
#taking the cosine impossible --> look at tan? 

#we want dy/dx, so we want y2-y1/x2-x1 --> shoulder2-elbow2/shoulder1-elbow1
line_ba = np.array(shou) - np.array(elb_new)







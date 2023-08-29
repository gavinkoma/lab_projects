
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


#alright i might have fucked up bc how do i add this onto the actually dataframe
#that i have to work on???? right now it just outputs values....


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
#wri = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Wrist',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
#elb = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Elbow',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
#shou = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Shoulder',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')
#col = ajay.loc[idx['2023-05-25_10_25_46',:],idx[:,'Collarbone',['x','y']]].droplevel(["scorer","bodyparts"],axis='columns')

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

	#one thing that we will want to keep in mind is that the data here only pertains
	#to the angle calculated from the shoulder --> elbow <-- wri
	#dont forget that we still need to calculate the shoulder angle
	plt.plot(range(len(cosine_angle)),cosine_angle)
	plt.xlabel("time points")
	plt.ylabel("segmented cosine angle")
	plt.title("elbow angle progression during reach")
	return print(cosine_angle)

def joint_angle_shou(elb,shou,col):
	# #merge the tuples so they are actually lines
	# wri_elb = merge_tuples(wri_tuple,elb_tuple)
	# elb_shou = merge_tuples(elb_tuple,shou_tuple)
	line_ba = np.array(shou) - np.array(elb)
	line_bc = np.array(shou) - np.array(col)
	cosine_angle = mydot(line_ba,line_bc) / (normalization(line_ba) * normalization(line_bc))
	cosine_angle = np.degrees(np.arccos(cosine_angle))
	plt.ion()
	plt.figure()
	plt.show()
	plt.plot(range(len(cosine_angle)),cosine_angle)
	plt.xlabel("time points")
	plt.ylabel("segmented cosine angle")
	plt.title("elbow angle progression during reach")
	return print(cosine_angle)

#put our values in a nice vector form
wri_vector_x_ = -np.diff(wri.iloc[:,0])
wri_vector_y_ = -np.diff(wri.iloc[:,1])

elb_vector_x_ = -np.diff(elb.iloc[:,0])
elb_vector_y_ = -np.diff(elb.iloc[:,1])

shou_vector_x_ = -np.diff(shou.iloc[:,0])
shou_vector_y_ = -np.diff(shou.iloc[:,1])

joint_angle_elbow(wri,elb,shou)
joint_angle_shou(elb,shou,col)

#list your inputs from top to bottom, this is important because this 
#is how i want to design this function

# def prep(extend):
# 	reference_line_elbow = []
# 	reference_elbow = pd.DataFrame()
# 	for val in extend.iloc[:,0]:
# 		x_val = val
# 		#print(x_val)
# 		reference_line_elbow.append(x_val)
# 	extend['ref_x'] = reference_line_elbow

# 	reference_line_elbow = []
# 	for val in extend.iloc[:,1]:
# 		y_val = val
# 		#print(x_val)
# 		reference_line_elbow.append(y_val)
# 	extend['ref_y'] = reference_line_elbow
# 	return extend

#our new issue is that the reference line will give us a value of 0 and that literally makes 
#taking the cosine impossible --> look at tan? 

#we want dy/dx, so we want y2-y1/x2-x1 --> shoulder2-elbow2/shoulder1-elbow1
#So in the attached, for angle 1, you want to do do atan2(y,x) 
#where y=By-Ay and x=Bx-Ax. Ay Bx etc mean the y coordinate of point A, 
#and Bx the x coordinate of B etc.

def segment_angle_func(body1,body2):	
	#pull out body coordinates
	x_1 = body1.iloc[:,0]
	y_1 = body1.iloc[:,1]
	x_2 = body2.iloc[:,0]
	y_2 = body2.iloc[:,1]

	#find differences between the vertices
	dy = (y_2-y_1)
	dx = (x_2-x_1)

	#calculate the angle in radians
	angle = np.arctan2(dy,dx)

	#this is in radian
	#print(angle)

	#change to degree
	def to_degree(angle):
		return np.rad2deg(angle)

	#perform radians --> degree change and show
	return to_degree(angle)

seg_colshou = segment_angle_func(col,shou)
seg_shouelb = segment_angle_func(shou,elb)
seg_elbwri = segment_angle_func(elb,wri)


#we should probably take the max and min values of these rats maybe as well?
#the more features we can pull then the better for our clusters
def mean(data):
	return ((sum(data))/len(data))

#output the mean degree value
mean_seg_colshou = mean(seg_colshou)
mean_seg_shouelb = mean(seg_shouelb)
mean_seg_elbwri = mean(seg_elbwri)

#we should also reference the reach window and use those frames as an index too 
#maybe at that point we can use those to calc the mean/speed values and be like very official 

#in this case maybe we can pull the frames but im not sure if this is really worth it
#actually it is, we would need to pull the peak frame and lets say we pull the previous like 100
#frames, we can take the velocity in terms of distance per second 
#so pull the values first --> we will need x & y components of this

#im just going to keep storming around here for now 
#lets say we have points of the wrist (which we do)

def velocidad(data):
	#pass the data you want to assess
	x = data.iloc[:,0]
	y = data.iloc[:,1]

	#pull the max values
	indexmax_x = np.argmax(x)
	print("index of max x value: " + str(indexmax_x))
	indexmax_y = np.argmax(y)
	print("index of max y value: " + str(indexmax_y))

	x_prev = indexmax_x - 100
	y_prev = indexmax_y - 100 

	def createList(r1,r2):
		return list(range(r1,r2+1))

	range_x = createList(x_prev,indexmax_x)
	range_y = createList(y_prev,indexmax_y)

	#velocity is ∆x over ∆t along the hypotenuse 
	#and the height is ∆h over ∆t
	#and then we can calculate sinø = (oppostie/hyp)
	#opp = hyp * sinø
	#∆h/∆t = v*sinø
	#lets just assume we only need ∆h/∆t = v*sinø
	#where v = sinø/(∆h/∆t) OR (sinø*∆t)/∆t

	#we most likely want atan2 to calculate that sin angle
	#we have two new values that raise above ground level to account for
	#index the values first because we need the min and max

	# indexx_prev = data.iloc[[x_prev]]
	# print(indexx_prev)
	# indexx_max = data.iloc[[indexmax_x]]
	# print(indexx_max)
	indexy_prev = data.iloc[[y_prev]]
	print(indexy_prev)
	indexy_max = data.iloc[[indexmax_y]]
	print(indexy_max)

	#this takes body1 & body2, but we can pass out prev cood & the peak cood
	def find_sin(lower,higher):
		#pull out body coordinates
		x_2 = higher['x'].reset_index(drop=True)
		#print(x_1)
		y_2 = higher['y'].reset_index(drop=True)
		#print(y_1)
		x_1 = lower['x'].reset_index(drop=True)
		#print(x_2)
		y_1 = lower['y'].reset_index(drop=True)
		#print(y_2)

		#find differences between the vertices
		dx = (x_2-x_1)
		dy = (y_2-y_1)

		#calculate the angle in radians
		angle = np.arctan2(dy,dx)

		#this will return the angle from positive x and the ray 
		#from the origin to the point (our ∆x/∆y) which is perfect
		#because we want to calculate the sinø for our velocity
		#change to degree
		def to_degree(angle):
			return np.rad2deg(angle)

		return to_degree(angle),dy

	sin,dy = find_sin(indexy_prev,indexy_max)

	#good we are getting a fuckin angle woooO!

	#now we want to do our actual velocity calculation
	#where v = sinø/(∆h/∆t) OR (sinø*∆t)/∆h
	#we can let ∆h be ∆y (change in height)

	#for now we can assume that fps = 50 until we get the real value
	def velu(sin,dy):
		print(sin)
		print(dy)
		fps = 20
		return (sin*(100/fps)/dy) #100 frames / 50 frames per second = 2 seconds

	velocity = velu(sin,dy)
	print(velocity)

velocidad(wri)
velocidad(elb)









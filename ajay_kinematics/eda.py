import matplotlib.pyplot as plt
import pandas as pd 

#lets view and assess the data first 
ajay = pd.read_hdf("/Users/gavinkoma/Documents/lab_projects/ajay_kinematics/data/alldata.h5")

#view as below, see head:
print(ajay.head(4))
#we have collarbone --> shoulder --> elbow --> wrist 
print(ajay.iloc[1,:])

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






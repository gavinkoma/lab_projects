import matplotlib.pyplot as plt
import pandas as pd 
import os
import numpy as np
idx = pd.IndexSlice

#lets view and assess the data first 
<<<<<<< HEAD
ajay = pd.read_hdf("/Users/gavinkoma/Documents/lab_projects/ajay_kinematics/data/alldata.h5")
#ajay = ajay.iloc[3:]
=======
ajay = pd.read_hdf(r"C:\Users\siyad\Documents\Spence Lab\lab_projects\ajay_kinematics\data\alldata.h5")
#ajay = pd.read_hdf("/Users/gavinkoma/Documents/lab_projects/ajay_kinematics/data/alldata.h5")
ajay = ajay.iloc[3:]
>>>>>>> refs/remotes/origin/main
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

#%%

# xy coords of the bodyparts
wri = ajay.loc[:,idx[:,'Wrist',['x','y']]].droplevel(['scorer','bodyparts'],axis='columns')
elb = ajay.loc[:,idx[:,'Elbow',['x','y']]].droplevel(['scorer','bodyparts'],axis='columns')
sho = ajay.loc[:,idx[:,'Shoulder',['x','y']]].droplevel(['scorer','bodyparts'],axis='columns')
col = ajay.loc[:,idx[:,'Collarbone',['x','y']]].droplevel(['scorer','bodyparts'],axis='columns')

#%%

# difference between the body parts
eucelbwri = (elb-wri).rename(columns={'x':'dx_ew','y':'dy_ew'})
eucshoelb = (elb-sho).rename(columns={'x':'dx_se','y':'dy_se'})
euccolshe = (sho-col).rename(columns={'x':'dx_cs','y':'dy_cs'})

#%%

# the actual distance calculations asf
eucelbwri['ewdist']=np.sqrt(eucelbwri['dx_ew']**2+eucelbwri['dy_ew']**2)
eucshoelb['sedist']=np.sqrt(eucshoelb['dx_se']**2+eucshoelb['dy_se']**2)
euccolshe['csdist']=np.sqrt(euccolshe['dx_cs']**2+euccolshe['dy_cs']**2)


#%%

# max and averages
height = ajay.loc[:,idx[:,'Wrist','y']].droplevel(['scorer','bodyparts'],axis='columns') - ajay.loc[:,idx[:,'Collarbone','y']].droplevel(['scorer','bodyparts'],axis='columns')
vid_1 = height.loc[idx['2023-05-25_10_25_46',:]]
vid_2 = height.loc[idx['2023-05-02_10_37_13',:]]
# there has to a better way ctfu

#%%
vid_names = ajay.index.unique('video')

max_height = pd.DataFrame()
avg_height = pd.DataFrame()
for x in vid_names:
    vid = height.loc[idx[x,:]]
    max_h = vid.max(axis=0)
    avg_h = vid.mean(axis=0)
    
    
#%% a place to fuck around

numbas = [1,2,3,4,5,6]

add_to = pd.DataFrame()
for x in numbas:
    current = x
    add_to.append(current)

# -*- coding: utf-8 -*-
"""
Created on Jun 7th, 2023
@author: aspence

NEW AJAY STUDY DATA FROM 2023- Mar 1 to May 31 Analysis...

environment: dog
NOTE: On spence M1 mac this environment is in Rosetta - use x86 terminal not standard!

cd ~/Library/CloudStorage/OneDrive-TempleUniversity/ajay20220823/code
conda activate dog
ipython

needed conda install openpyxl
for pandas.read_excel

Load rat DLC output single munged h5 file from 2023 and compute 2D joint angles from single view.
Then run blinded joint angle analyses and make plots.

Goal: 
1. Before cutting strides.
  - Median and IQR of 2 joint angles by stride over time points.
2. Plot everything into subfolder... individual trials joint angles.
3. Find auto stride cut methods... find good strides... then would like
4. Joint angle versus stride pct with rat over time. Then across rats.

TODO: Change index level 2 to frame from 0.

=== 2D Joint Angle code from web ===
https://manivannan-ai.medium.com/find-the-angle-between-three-points-from-2d-using-python-348c513e2cd
import math
 def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang
 print(getAngle((5, 0), (0, 0), (0, 5)))

or

import numpy as np
a = np.array([6,0])
b = np.array([0,0])
c = np.array([0,6])
ba = a - b
bc = c - b
cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
angle = np.arccos(cosine_angle)
print np.degrees(angle)

BASE ON MICHE:
This file is used to find the perspective correction of the top camera points tracked in DLC
-Uses a .yaml file to process all of the files in a loop and saves to one .csv file 
-It will search for the dog's name and spacing from the file name, and match it with the proper spacing conditions (real world measurements)
    - TODO: need to add the measurements of other dogs 
- homography transformation: https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga4abc2ece9fab9398f2e560d53c8c9780
- Pandas multi-indexing: https://pandas.pydata.org/pandas-docs/stable/user_guide/advanced.html
After the points are transformed into real-world coordinates, move on to filtering
"""
import numpy as np
import matplotlib
from scipy.signal import butter, lfilter, freqz
import pandas as pd
import matplotlib.pyplot as plt
import math
import argparse
import os
from os.path import join as osjoin
import re
idx = pd.IndexSlice

def mydot(a,b):
  return a[:,0]*b[:,0] + a[:,1]*b[:,1]
def mynorm(a):
  return np.sqrt(np.sum(a**2,axis=1))

def angle2D(data,a,b,c):
  # so vec diff from Collarbone to Shoulder is
  ba=np.array(data.loc[:,idx[:,[b],['x','y']]]) - np.array(data.loc[:,idx[:,[a],['x','y']]])
  bc=np.array(data.loc[:,idx[:,[b],['x','y']]]) - np.array(data.loc[:,idx[:,[c],['x','y']]])
  cosine_angle = mydot(ba,bc) / (mynorm(ba) * mynorm(bc))
  return np.degrees(np.arccos(cosine_angle))
  #print(np.degrees(angle))

def valthresh(data,a,b,c):
  # so vec diff from Collarbone to Shoulder is
  ba=np.array(data.loc[:,idx[:,[b],['x','y']]]) - np.array(data.loc[:,idx[:,[a],['x','y']]])


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# needed conda install openpyxl
# get the metadata
datadir='../data'
md=pd.read_excel(os.path.join(datadir,'allvids2023filled_afterAJS.xlsx'),index_col=1,converters={'video':str}).drop(columns='Unnamed: 0')
md=md[md['analyze']=='yes']
# Ok at this point no nan or anything in md.
# what we can analyze has a yes in metadata analyze column and is present
# in the index of the full data.
# read the data set:
ds=pd.read_hdf(os.path.join(datadir,'alldata.h5'))
ds.index=ds.index.set_names(['video','frame'])
# get videos in the data set:
ds.index.get_level_values('video').unique()
# create data frame of valid values (all likelyhood > 0.95), will join in later.
valflag=pd.DataFrame({'valid':(ds.loc[:,idx[:,:,['likelihood']]]>0.95).all(axis=1)})
# get intersection of videos in metadata and dataset
vids=list(set(md.index) & set(ds.index.get_level_values('video').unique()))
# Okay first let's make a new ds with just the two joint angles...
# Test code below on first video from ds:
if 0:
  order = 2
  fs = 250.0       
  cutoff = 20
  v1=ds.loc[idx['2023-05-25_10_25_46',:]]
  sho=butter_lowpass_filter(angle2D(v1,'Collarbone','Shoulder','Elbow'), cutoff, fs, order)
# Well that works! write a func that returns a df:
def jointAngles(df):
  sho=butter_lowpass_filter(angle2D(df,'Collarbone','Shoulder','Elbow'), cutoff, fs, order)
  elb=butter_lowpass_filter(angle2D(df,'Shoulder','Elbow','Wrist'), cutoff, fs, order)
  return pd.DataFrame(data={'sho':sho, 'elb':elb},index=df.index)
def jointAnglesNoFilter(df):
  sho=angle2D(df,'Collarbone','Shoulder','Elbow')
  elb=angle2D(df,'Shoulder','Elbow','Wrist')
  return pd.DataFrame(data={'sho':sho, 'elb':elb},index=df.index)

# Now use in a sweet groupby:
#dsj = ds.groupby(['video']).apply(lambda gdf: gdf.join( myfilter(gdf[cols]).add_suffix('_filt' ) ))
#dsj = ds.groupby(['video'],group_keys=False).apply(lambda gdf: jointAngles(gdf) )
dsj = ds.groupby(['video'],group_keys=False).apply(lambda gdf: jointAnglesNoFilter(gdf) )
# jun 8th 2023 [508465 rows x 2 columns]
'''
Wow. works?
In [97]: dsj = ds.groupby(['video']).apply(lambda gdf: jointAngles(gdf) )
<ipython-input-97-485e39fd391b>:1: FutureWarning: Not prepending group keys to the result index of transform-like apply. In the future, the group keys will be included in the index, regardless of whether the applied function returns a like-indexed object.
To preserve the previous behavior, use

  >>> .groupby(..., group_keys=False)

To adopt the future behavior and silence this warning, use

  >>> .groupby(..., group_keys=True)
  dsj = ds.groupby(['video']).apply(lambda gdf: jointAngles(gdf) )
'''
# Make a plotter... plot them all and look.
# dsj.loc[idx['2023-05-25_10_25_46',:],:]
def plotJointAngle(d,savedir='../figures/jointanglesStudy2_2023'):
  t=np.arange(1000)/250.0
  figure = plt.figure(0)
  plt.clf()
  figure.set_size_inches(6,3)
  plt.plot(t,np.vstack([d['sho'],d['elb']]).T)
  plt.legend(("Shoulder","Elbow"))
  plt.xlabel('Time (sec)')
  plt.ylabel('Angle (deg)')
  # ylim 20-160
  #plt.ylim((20,170))
  #plt.tight_layout()
  vn=d.index.get_level_values('video')[0]
  # so that works on basic data or after join, check for rat
  if 'rat' in d.columns:
    vn=vn+"_rat"+str(d['rat'].iloc[0])
  if 'speed' in d.columns:
    vn=vn+"_speed"+str(d['speed'].iloc[0])
  plt.title(vn)
  plt.savefig(os.path.join(savedir,vn+".pdf"),bbox_inches="tight")

def plotJointAngleVal(d,savedir='../figures/jointanglesStudy2_2023'):
  if any(d['valid']):
    t=np.arange(1000)/250.0
    figure = plt.figure(0)
    plt.clf()
    figure.set_size_inches(6,3)
    t=t[d['valid']]
    d=d[d['valid']]
    plt.scatter(t,d['sho'])
    plt.scatter(t,d['elb'])
    plt.legend(("Shoulder","Elbow"))
    plt.xlabel('Time (sec)')
    plt.ylabel('Angle (deg)')
    # ylim 20-160
    #plt.ylim((20,170))
    #plt.tight_layout()
    vn=d.index.get_level_values('video')[0]
    # so that works on basic data or after join, check for rat
    if 'rat' in d.columns:
      vn=vn+"_rat"+str(d['rat'].iloc[0])
    if 'speed' in d.columns:
      vn=vn+"_speed"+str(d['speed'].iloc[0])
    plt.title(vn)
    plt.savefig(os.path.join(savedir,vn+".pdf"),bbox_inches="tight")

# join the data sets
jd=dsj.join(md,how='inner')
# [431000 rows x 5 columns]
# figure out how to get rat and speed from a single video
if 0:
  d=jd.loc[idx['2023-05-25_10_25_46',:],:]
  # ok did it, see plotjointangleabove

# make all the plots...
# jd.groupby(['video']).apply(lambda gdf: plotJointAngle(gdf,savedir='../figures/jointanglesStudy2_2023'))
# ok there's a lot of garbage. let's plot just where all markers found with lh > 0.95...

# then we'll use groupby to 
# 0. convert times to time objects
# 1. filter?
# 2. compute the two joint angles for all points with enough markers
# 3. cmpute median, iqr, min, max of each angle per trial
# 4. analyze and boxplot by rat and time

jdf=jd.join(valflag,how='inner')
# [431000 rows x 6 columns]
jdf.groupby(['video']).apply(lambda gdf: plotJointAngleVal(gdf,savedir='../figures/jointanglesStudy2_2023'))
# oh wow 431 pdfs! think it works. they look ok, too!

# Ok I think if we strip the first 0.5 second and only include these >0.95 samples, and use
# robust measures, median and IQR (no max/min), we may get something ok.
# Also, actually just try without the lowpass... maybe that will fix beginning.
# Fixed! Ok I thinks it's usuable for first pass!
# Now to fix the time objects, compute the aggregate measures, and plot:
# Actually can fix time later...

def iqr(d):
  return (np.quantile(d,0.75)-np.quantile(d,0.25))

'''
jdf.groupby(['video']).apply(lambda gdf: gdf.iloc[0:1,:])
jdf.groupby(['video']).agg(sho_med=('sho','median'))
jdf.groupby(['video']).apply(lambda gdf: pd.DataFrame({'sho_med':gdf['sho'].median()}))
jdf.groupby(['video']).apply(lambda gdf: gdf.iloc[0:1,:].join(pd.DataFrame({'sho_med':gdf['sho'].median()})))
jdf.groupby(['video']).apply(lambda gdf: gdf.iloc[0:1,:].join(pd.DataFrame({'sho_med':gdf['sho'].median()})))
jdf[jdf['valid']==True].groupby(['video']).apply(lambda gdf: gdf.iloc.join(gdf['sho'].median()))
'''

# Phew. Agg still not trivial.
jdfa=jdf[jdf['valid']==True].groupby(['video']).agg(
  sho_med=('sho','median'),
  sho_iqr=('sho',iqr),
  elb_med=('elb','median'),
  elb_iqr=('elb',iqr),
  rat=('rat','first'),
  speed=('speed','first'))
# [429 rows x 6 columns]

jdfa['timestamp']=jdfa.index.map( lambda x: datetime.datetime.strptime(x,'%Y-%m-%d_%H_%M_%S') )
jdfa['days'] = (jdfa['timestamp'] - jdfa['timestamp'][0]).dt.days
jdfa['date']=jdfa['timestamp'].map(lambda x: x.strftime('%Y-%m-%d'))
# drop 13th, only rat 8, recorded again 
# ok data cleaning:
# https://tuprd.sharepoint.com/:x:/r/sites/SpenceLab/_layouts/15/Doc.aspx?sourcedoc=%7BBD1B475F-A213-4FBE-8429-7EA586ABAA24%7D&file=AjayPilotVideosAnalysis.xlsx&action=default&mobileredirect=true
# can ditch mar 13th, 11 days, only rat 8, was recorded again
jdfa=jdfa[jdfa['date']!='2023-03-13']
jdfa['weeks']=jdfa['days'].map(lambda x: round(x/7))
# Ok the above week rounding combined thee 4/18 and 4/20 data collection 48 49 days. sohudl clean up graph.

def timePlot(var="sho_med",ylab='Shoulder Angle (median)',
  title='Shoulder Angle vs Time Median per Video',save='shoulder_median',
  savedir='../figures/jointanglesStudy2_2023',speed=8):
  sns.catplot(
      data=jdfa[jdfa['speed']==speed], x="weeks", y=var, hue="rat",
      capsize=.2, errorbar="se",
      kind="point", height=6, aspect=.75,
  )
  plt.xlabel('weeks (0=Mar 1, 2023)')
  plt.ylabel(ylab)
  plt.title(title+'_speed_'+str(speed))
  plt.savefig(os.path.join(savedir,save+"_speed_"+str(speed)+"_.pdf"),bbox_inches="tight")
  plt.ion()
  plt.show()


# shoulder med
timePlot() # 8
# these dont' make sense as no data before week 5
timePlot(speed=12)
timePlot(speed=16)

# elbow med speed 8
timePlot("elb_med","Elbow Angle (median)","Elbow Angle vs Time Median","elbow_median")
# mar 1 is before injury.
# mar 23 is after injury.

# shoulder iqr 8
timePlot("sho_iqr","Shoulder Angle (iqr)","Sho Ang vs Time IQR","shoulder_iqr")
# elb iqr 8
timePlot("elb_iqr","Elbow Angle (iqr)","Elbow Ang vs Time IQR","elbow_iqr")

# Interesting... no idea what it means, but examinng shoulder you see
# rats 1, 3, 4 are more extended at last week
# rats 6, 7, 8 are more flexed...
# somehwat similar clustering in elbow angle median at 8 cm/s
# are first ones treated? could stride cut... could also get smart and just
# do some bigger machine learning classification thing on everything eg raw waves...
# HOLY S**T THOSE WERE EXACTLY CORRECT ANIMAL NUMBERS!!!!
# Make grouped plot... drop rats 2 and 5; 1, 3, 4 are stim, red line, 6, 7, 8 are control, black line
# Week 0 = week -1
# Drop dead rats
jdfag = jdfa[~jdfa['rat'].isin([2,5])]
jdfag['treatment']=jdfag['rat']
jdfag.loc[jdfag['rat'].isin([1,3,4]),'treatment']='stim'
jdfag.loc[jdfag['rat'].isin([6,7,8]),'treatment']='control'
jdfag['week']=jdfag['weeks']-1

# Plot up!
def timePlotGrp(var="sho_med",ylab='Shoulder Angle (degrees; median)',
  title='Shoulder Angle vs Week',save='shoulder_median',
  savedir='../figures/jointanglesStudy2_2023',speed=8):
  sns.catplot(
      data=jdfag[jdfag['speed']==speed], x="week", y=var, hue="treatment",
      capsize=.2, errorbar="se",
      kind="point",  palette=sns.color_palette(["#FF0000", "#000000"]), height=3, aspect=1,
  )
  plt.xlabel('Week')
  plt.ylabel(ylab)
  plt.title(title+'_speed_'+str(speed))
  plt.savefig(os.path.join(savedir,save+"_grped_speed_"+str(speed)+"_.pdf"),bbox_inches="tight")
  plt.ion()
  plt.show()

timePlotGrp()
timePlotGrp("elb_med","Elbow Angle (degrees; median)","Elbow Angle vs Week","elbow_median")

#iqr, why not
# shoulder iqr 8
timePlotGrp("sho_iqr","Shoulder ROM (iqr)","Shoulder Range of Motion","shoulder_iqr")
# elb iqr 8
timePlotGrp("elb_iqr","Elbow ROM (iqr)","Elbow Range of Motion","elbow_iqr")

# Traceability... looks like we could use R geom_text_repel()
# I want to look and see why the joint angles are so large for the three treatment rats in last
# week. Is it real or bug? What data points lead to that?


# Auto stride cut/detect: what does wrist x - shoulder x look like? swings obvious?


if 0:
  timePlot(speed=12)
  #timePlot("sho_iqr","Shoulder Angle (iqr)","Sho Ang vs Time IQR","shoulder_iqr.pdf")
  timePlot("elb_med","Elbow Angle (median)","Elbow Angle vs Time Median","elbow_median")
  timePlot("elb_med","Elbow Angle (median)","Elbow Angle vs Time Median","elbow_median",speed=12)
  timePlot("elb_med","Elbow Angle (median)","Elbow Angle vs Time Median","elbow_median",speed=16)
  #timePlot("elb_iqr","Elbow Angle (iqr)","Elbow Ang vs Time IQR","elbow_iqr.pdf")


if 0:
  jdfa.reset_index(inplace=True)
  jdfa.index = jdfa.index.map( lambda x: datetime.datetime.strptime(x,'%Y-%m-%d_%H_%M_%S') )
  # Okay now need to round the times to the day, then group...
  jdfa.index = (jdfa.index - jdfa.index[0]).days
  jdfai = jdfa.reset_index().rename(columns={'video':'days'})
  sns.boxplot(x="video", y="sho_med",hue='rat',data=jdfai)

  sns.catplot(
      data=jdfai, x="days", y="sho_med", hue="rat",
      capsize=.2, palette="YlGnBu_d", errorbar="se",
      kind="point", height=6, aspect=.75,
  )

for f in os.listdir(datadir):
  if f.endswith('200000.h5'):
    print("  Found h5 file", f, "including.")
    #with open(osjoin(os.getcwd(),t['datadir'],f),'rb') as fle:
      # Import the h5 file because it's awesomely smaller (a binary) and contains
         # all the hierarchical multiindex goodness without parsing the csv.
    data=pd.read_hdf(osjoin(os.getcwd(),datadir,f))
    order = 2
    fs = 250.0       
    cutoff = 20
    sho=butter_lowpass_filter(angle2D(data,'Collarbone','Shoulder','Elbow'), cutoff, fs, order)
    elb=butter_lowpass_filter(angle2D(data,'Shoulder','Elbow','Wrist'), cutoff, fs, order)
    t=np.arange(1000)/250.0
    plt.clf()
    figure = plt.gcf() # get current figure
    figure.set_size_inches(6,3)
    plt.plot(t,np.vstack([sho,elb]).T)
    plt.legend(("Shoulder","Elbow"))
    plt.xlabel('Time (sec)')
    plt.ylabel('Angle (deg)')
    # ylim 20-160
    plt.ylim((20,170))
    # frames 130-850 on 11_12_21
    if '11_12_21' in f:
      plt.xlim((130.0/250.0,850.0/250.0))
      plt.title('Moderate Injury')
    if '10_12_36' in f:
      plt.xlim((0/250.0,750.0/250.0))
      plt.title('Severe Injury')
    if '11_53_05' in f:
      plt.xlim((562.5/250.0,812/250.0))
      plt.title('Normal Animal')
    if '11_48_18' in f:
      plt.xlim(2.3,4)
      plt.title('Normal Animal')
    if 'test' in f:
      plt.xlim(2.3,4)
      plt.title('Normal Animal')
    #plt.tight_layout()
    plt.savefig(f.split('.')[0]+".pdf",bbox_inches="tight")

plt.ion()
plt.show()

# scratch/testing area:
if 0:
  # get coords... ok this gets nice pd data frame with all hierarchical we want!
  data.loc[:,idx[:,['Collarbone'],['x','y']]]
  # get coords... ok this gets nice pd data frame with all hierarchical we want!
  data.loc[:,idx[:,['Collarbone'],['x','y']]].unstack() - data.loc[:,idx[:,['Shoulder'],['x','y']]].unstack()


import numpy as np
import matplotlib, math, argparse, os, re, yaml, datetime, sys, subprocess
from scipy.signal import butter, lfilter, freqz
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from os.path import join as osjoin
idx = pd.IndexSlice
from matplotlib.backends.backend_pdf import PdfPages

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

with open("config.yml", "r") as yamlfile:
  cfgp = yaml.load(yamlfile,Loader=yaml.FullLoader)
  print("Read successful")
  print(cfgp)

md=pd.read_csv(cfgp['data_dir'], index_col=1,converters={'videopath':str})
md=md[md['analyze']=='yes']


# import os
# import pandas as pd

# #find all csv files analyzed
# def find_csv_files(directory):
#     csv_files = []
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             if file.endswith('.csv'):
#                 csv_files.append(os.path.join(root, file))
#     return csv_files

# #errors reading csv files
# def read_csv_with_encoding(file, header=[0,1,2],skiprows=None):
#   #i have never had to specify encoding before wtf
#     try:
#         return pd.read_csv(file, encoding='utf-8', header,skiprows=None)  #try with utf-8 encoding
#     except UnicodeDecodeError:
#         return pd.read_csv(file, encoding='ISO-8859-1', header,skiprows=None)  #fallback to ISO-8859-1

# #make the big alldata file
# def aggregate_csv_files(directory):
#     csv_files = find_csv_files(directory)
#     dataframes = []

#     if not csv_files:
#         raise ValueError("No CSV files found in the directory.")

#     #read the first file with header
#     first_file = csv_files[0]
#     df_first = read_csv_with_encoding(first_file) 
#     df_first['video_name'] = os.path.basename(first_file).replace('.csv', '')
#     dataframes.append(df_first)

#     #add filename column & add other data
#     for file in csv_files[1:5]:
#         df = read_csv_with_encoding(file, header=None,skiprows=2)  #skip headers for subsequent files
#         df['video_name'] = os.path.basename(file).replace('.csv', '') 
#         dataframes.append(df)

#     #add into one big data frame
#     aggregated_df = pd.concat(dataframes, ignore_index=True)
#     return aggregated_df

# #call
# directory_path = cfgp['video_root_path']
# aggregated_dataframe = aggregate_csv_files(directory_path)

# #tocsv
# output_file_path = cfgp['project_path']+str('aggregated_file.csv')
# aggregated_dataframe.to_csv(output_file_path, index=False)

#cannot figure out how to make the stupid headers go away
#sos

###


#well this way worked 
import os, pandas as pd
alldat=[]
for dirpath, sub_directories, files in os.walk(cfgp['video_root_path']):
   for file in files:
     folder_name = os.path.split(dirpath)[1] # this folder contains the .mp4
     source = os.path.join(dirpath, file)
     if file.endswith("DLC_resnet50_forelimbAug24shuffle1_200000.h5"):
       alldat.append(source)
adf=[]
for f in alldat:
   d0=pd.read_hdf(f)
   # Convert index to dataframe
   old_idx = d0.index.to_frame()
   # Insert new level at specified location
   old_idx.insert(0, 'video', f.split('/')[-1])
   # Convert back to MultiIndex
   d0.index = pd.MultiIndex.from_frame(old_idx)
   adf.append(d0)
adf=pd.concat(adf)
adf.to_hdf(cfgp['project_path']+str('alldata.h5'),key='df')

datadir=cfgp['data_dir']
md=pd.read_csv(datadir,index_col=1,converters={'video':str})
md=md[md['analyze']=='yes']
# for 2024 data the index was called "filename" change to 'video' to merge with joint angles df below
md.index=md.index.set_names('video')


ds=pd.read_hdf('alldata.h5')
ds.index=ds.index.set_names(['video','frame'])

# 20241022 patch longe names for 2024 study
# Our way which took an hour:
#dsi=ds.index.to_frame()
#dsi['video']=dsi['video'].str.replace('DLC_resnet50_forelimbAug24shuffle1_200000.h5','.mp4')
#nv=ds.index.to_frame()['video'].str.replace('DLC_resnet50_forelimbAug24shuffle1_200000.h5','.mp4')
#ds.index=pd.MultiIndex.from_frame(dsi)
# Chatgpt 5 min:
ds.index = ds.index.set_levels( ds.index.levels[0].str.replace('DLC_resnet50_forelimbAug24shuffle1_200000.h5','.mp4') , level='video')

ds.index.get_level_values('video').unique()

valflag=pd.DataFrame({'valid':(ds.loc[:,idx[:,:,['likelihood']]]>0.95).all(axis=1)})

vids=list(set(md.index) & set(ds.index.get_level_values('video').unique()))


if 0:
  order = 2
  fs = 250.0       
  cutoff = 20
  v1=ds.loc[idx['2023-05-25_10_25_46',:]]
  sho=butter_lowpass_filter(angle2D(v1,'Collarbone','Shoulder','Elbow'), cutoff, fs, order)

def jointAngles(df):
  sho=butter_lowpass_filter(angle2D(df,'Collarbone','Shoulder','Elbow'), cutoff, fs, order)
  elb=butter_lowpass_filter(angle2D(df,'Shoulder','Elbow','Wrist'), cutoff, fs, order)
  return pd.DataFrame(data={'sho':sho, 'elb':elb},index=df.index)

def jointAnglesNoFilter(df):
  sho=angle2D(df,'Collarbone','Shoulder','Elbow')
  elb=angle2D(df,'Shoulder','Elbow','Wrist')
  return pd.DataFrame(data={'sho':sho, 'elb':elb},index=df.index)

#dsj = ds.groupby(['video'],group_keys=False).apply(lambda gdf: jointAngles(gdf) )
dsj = ds.groupby(['video'],group_keys=False).apply(lambda gdf: jointAnglesNoFilter(gdf) )
# jun 8th 2023 [508465 rows x 2 columns]

# dsj.loc[idx['2023-05-25_10_25_46',:],:]
def plotJointAngle(d,savedir=cfgp['project_path']):
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

def plotJointAngleVal(d,savedir=cfgp['project_path']):
  if any(d['valid']): #i will have to change this
    t=np.arange(len(d['sho']))/250.0
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
jdf = jdf[~jdf['rat'].isin([27,33,22,26,36,28,25,32])]
# [431000 rows x 6 columns] <- prior dataset
jdf.groupby(['video']).apply(lambda gdf: plotJointAngleVal(gdf,savedir='figures/'))
# oh wow 431 pdfs! think it works. they look ok, too!

# Ok I think if we strip the first 0.5 second and only include these >0.95 samples, and use
# robust measures, median and IQR (no max/min), we may get something ok.
# Also, actually just try without the lowpass... maybe that will fix beginning.
# Fixed! Ok I thinks it's usuable for first pass!
# Now to fix the time objects, compute the aggregate measures, and plot:
# Actually can fix time later...


def iqr(d):
  return (np.quantile(d,0.75)-np.quantile(d,0.25))

# Phew. Agg still not trivial. No l onger care about speed.
jdfa=jdf[jdf['valid']==True].groupby(['video']).agg(
  sho_med=('sho','median'),
  sho_iqr=('sho',iqr),
  elb_med=('elb','median'),
  elb_iqr=('elb',iqr),
  rat=('rat','first') )
# [429 rows x 6 columns]

# Starting times:
'''
rat
23    mar8
24    mar8
29    mar8
30    mar8
21    mar8
31    week11
34    week11
35    week11
'''

jdfa['timestamp'] = jdfa.index.map( lambda x: datetime.datetime.strptime(x[0:19],'%Y-%m-%d_%H_%M_%S') )
# These rats started mar 8
jdfa.loc[jdfa['rat'].isin([23,24,29,30,21]), 'start_timestamp'] = jdfa['timestamp'][0]
# These ones all started together later
jdfa.loc[jdfa['rat'].isin([31,34,35]), 'start_timestamp'] = jdfa.loc[jdfa['rat'].isin([31])]['timestamp'][0]
jdfa['days'] = (jdfa['timestamp']-jdfa['start_timestamp']).dt.days
jdfa['date'] = jdfa['timestamp'].map(lambda x: x.strftime('%Y-%m-%d'))
jdfa['weeks'] = jdfa['days'].map(lambda x: round(x/7))

jdfa.loc[jdfa['rat'].isin([21, 31]), 'exp_group'] = 'SCI'
jdfa.loc[jdfa['rat'].isin([23, 30]), 'exp_group'] = 'MCS+NT3'
jdfa.loc[jdfa['rat'].isin([29, 35]), 'exp_group'] = 'NT3'
jdfa.loc[jdfa['rat'].isin([24, 34]), 'exp_group'] = 'MCS'

'''
In [175]: jdfa.value_counts(jdfa.rat)
Out[175]: 
rat
23    265
24    253
29    194
30    134
21    113
31     71
34     63
35     63
'''

# Oops have 2 cams now.. cam 1 is right side same as last study, use that.
jdfaR=jdfa[jdfa.index.get_level_values('video').str.contains('camcommerb1')]
jdfaL=jdfa[jdfa.index.get_level_values('video').str.contains('camcommerb2')]
jdfaR.groupby('exp_group')['sho_med'].plot(legend=True)
jdfaL.groupby('exp_group')['sho_med'].plot(legend=True)

def timePlot(indata,var='sho_med', ylab="Shoulder Angle (median)", group='rat',
  title = 'Shoulder Angle vs. Time Median by Rat', save="shoulder_median",
  savedir = os.path.join(cfgp['figs'],str('final_figs'))):
  #fig,axs = plt.subplots(2,2, figsize=(25,25))
  #fig = plt.figure()
  #ax1 = fig.add_subplot(121)
  g =   sns.catplot(
    data = indata, x='weeks', y=var, hue=group,
    capsize = 2, #errorbar = 'se',
    kind = 'point',height=6, aspect=.75
    )
  plt.xlabel('weeks')
  plt.ylabel(ylab)
  plt.title(title)
  plt.savefig(os.path.join(savedir,save+"_cat.pdf"),bbox_inches='tight')
  plt.ion()
  plt.show()

timePlot(jdfaR,group='exp_group',save="R_sho_med",title='RIGHT Shoulder Angle vs. Time Median by Rat')
timePlot(jdfaL,group='exp_group',save="L_sho_med",title='LEFT Shoulder Angle vs. Time Median by Rat')
timePlot(jdfa,group='exp_group',save="sho_med",title='Both Shoulders Angle vs. Time Median by Rat')

def timePlotLine(indata,var='sho_med', ylab="Shoulder Angle (median)", group='rat',
  title = 'Shoulder Angle vs. Time Median by Rat', save="shoulder_median",
  savedir = os.path.join(cfgp['figs'],str('final_figs'))):
  #fig,axs = plt.subplots(2,2, figsize=(25,25))
  fig = plt.figure()
  #ax1 = fig.add_subplot(121)
  g =   sns.lineplot(
    data = indata, x='weeks', y=var, hue=group
    )
  plt.xlabel('weeks')
  plt.ylabel(ylab)
  plt.title(title)
  plt.savefig(os.path.join(savedir,save+"_"+group+"_line.pdf"),bbox_inches='tight')
  plt.ion()
  plt.show()

timePlotLine(jdfaR,group='exp_group',save="R_sho_med",title='RIGHT Shoulder Angle vs. Time Median by Rat')
timePlotLine(jdfaL,group='exp_group',save="L_sho_med",title='LEFT Shoulder Angle vs. Time Median by Rat')
timePlotLine(jdfa,group='exp_group',save="sho_med",title='Both Shoulders Angle vs. Time Median by Rat')

timePlotLine(jdfaR,var='sho_iqr',group='exp_group',save="R_sho_iqr",title='RIGHT Shoulder Angle vs. Time IQR by Rat')
timePlotLine(jdfaL,var='sho_iqr',group='exp_group',save="L_sho_iqr",title='LEFT Shoulder Angle vs. Time IQR by Rat')
timePlotLine(jdfa,var='sho_iqr',group='exp_group',save="sho_iqr",title='Both Shoulders Angle vs. Time IQR by Rat')

timePlotLine(jdfaR,var='elb_iqr',group='exp_group',save="R_elb_iqr",title='RIGHT Elbow Angle vs. Time IQR by Rat',ylab='Elbow Angle (IQR)')
timePlotLine(jdfaL,var='elb_iqr',group='exp_group',save="L_elb_iqr",title='LEFT Elbow Angle vs. Time IQR by Rat',ylab='Elbow Angle (IQR)')
timePlotLine(jdfa,var='elb_iqr',group='exp_group',save="elb_iqr",title='Both Elbow Angle vs. Time IQR by Rat',ylab='Elbow Angle (IQR)')

timePlotLine(jdfaR,var='elb_med',group='exp_group',save="R_elb_med",title='RIGHT Elbow Angle vs. Time Median by Rat',ylab='Elbow Angle (median)')
timePlotLine(jdfaL,var='elb_med',group='exp_group',save="L_elb_med",title='LEFT Elbow Angle vs. Time Median by Rat',ylab='Elbow Angle (median)')
timePlotLine(jdfa,var='elb_med',group='exp_group',save="elb_med",title='Both Elbow Angle vs. Time Median by Rat',ylab='Elbow Angle (median)')

# ===== now by rat
timePlotLine(jdfaR,save="R_sho_med",title='RIGHT Shoulder Angle vs. Time Median by Rat')
timePlotLine(jdfaL,save="L_sho_med",title='LEFT Shoulder Angle vs. Time Median by Rat')
timePlotLine(jdfa,save="sho_med",title='Both Shoulders Angle vs. Time Median by Rat')

timePlotLine(jdfaR,var='sho_iqr',save="R_sho_iqr",title='RIGHT Shoulder Angle vs. Time IQR by Rat')
timePlotLine(jdfaL,var='sho_iqr',save="L_sho_iqr",title='LEFT Shoulder Angle vs. Time IQR by Rat')
timePlotLine(jdfa,var='sho_iqr',save="sho_iqr",title='Both Shoulders Angle vs. Time IQR by Rat')

timePlotLine(jdfaR,var='elb_iqr',save="R_elb_iqr",title='RIGHT Elbow Angle vs. Time IQR by Rat',ylab='Elbow Angle (IQR)')
timePlotLine(jdfaL,var='elb_iqr',save="L_elb_iqr",title='LEFT Elbow Angle vs. Time IQR by Rat',ylab='Elbow Angle (IQR)')
timePlotLine(jdfa,var='elb_iqr',save="elb_iqr",title='Both Elbow Angle vs. Time IQR by Rat',ylab='Elbow Angle (IQR)')

timePlotLine(jdfaR,var='elb_med',save="R_elb_med",title='RIGHT Elbow Angle vs. Time Median by Rat',ylab='Elbow Angle (median)')
timePlotLine(jdfaL,var='elb_med',save="L_elb_med",title='LEFT Elbow Angle vs. Time Median by Rat',ylab='Elbow Angle (median)')
timePlotLine(jdfa,var='elb_med',save="elb_med",title='Both Elbow Angle vs. Time Median by Rat',ylab='Elbow Angle (median)')

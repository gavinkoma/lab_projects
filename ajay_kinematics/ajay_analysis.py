vidslist=['/zfsr01/storage/ajay20220823/cam2/2022-09-22_11_10_28/fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-22_11_12_45/fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-22_11_16_57/fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-29_11_53_05/fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-29_12_31_27/fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-29_12_33_23/fr_wbgam_h264_nearlossless_safe.mp4'
]

# ap4 sep 22 markers visible whoel time, but slow
# '/zfsr01/storage/ajay20220823/cam2/2022-09-22_11_12_45/fr_wbgam_h264_nearlossless_safe.mp4

# ap6 sep 22 ok
#'/zfsr01/storage/ajay20220823/cam2/2022-09-22_11_16_57/fr_wbgam_h264_nearlossless_safe.mp4'

# USE FOR TRAIN AND GRANT! Ap6 sep 29.. 8cm #2 good markers vis whole time
# '/zfsr01/storage/ajay20220823/cam2/2022-09-29_12_33_23/fr_wbgam_h264_nearlossless_safe.mp4'

# Ok running:
terminal
conda activate DLC-GPU
ipython3
import tf stuff.....
import dlc...
vidslist=['/zfsr01/storage/ajay20220823/cam2/2022-09-22_11_10_28/2022-09-22_11_10_28_fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-22_11_12_45/2022-09-22_11_12_45_fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-22_11_16_57/2022-09-22_11_16_57_fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-29_11_53_05/2022-09-29_11_53_05_fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-29_12_31_27/2022-09-29_12_31_27_fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-29_12_33_23/2022-09-29_12_33_23_fr_wbgam_h264_nearlossless_safe.mp4'
]
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,shuffle=1,save_as_csv=True)
dlc.create_labeled_video('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,draw_skeleton=True)

# open config.yaml and edit numframees2pick: 10. from 6 vids = 60.
# then tried:
dlc.extract_outlier_frames('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,automatic=True)
# But DUH all movies have same name so it puts etracted frames in same dir and clobbers. kinda silly.
# should add the timestamp to the raw dumps. why not. at the end. just do it.
# Doh. for now manually going to rename the vids.
# how do the automagically chosen outliers look? they take a long time to kmeans etract.... pulling 320 frames of 1000 and clustering to get 10!
# -> actually these looked good. definitely diverse!
# did it update my config file video list? oops i had it open on subl... problems?
# no it added! without a ? and :... interesting. that was original ones? symlinked? it's copying now...
#  manually removing file names from config.yaml and redoing.
vidslist=['/zfsr01/storage/ajay20220823/cam2/2022-09-22_11_10_28/2022-09-22_11_10_28_fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-22_11_12_45/2022-09-22_11_12_45_fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-22_11_16_57/2022-09-22_11_16_57_fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-29_11_53_05/2022-09-29_11_53_05_fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-29_12_31_27/2022-09-29_12_31_27_fr_wbgam_h264_nearlossless_safe.mp4',
'/zfsr01/storage/ajay20220823/cam2/2022-09-29_12_33_23/2022-09-29_12_33_23_fr_wbgam_h264_nearlossless_safe.mp4'
]
dlc.extract_outlier_frames('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,automatic=True)
# oops it couldn't find the renamed videos... because i hadn't anlayzed them. note this is with updated vidlist...
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,shuffle=1,save_as_csv=True)
# worked! new analysis files in the video dirs with the unique names. now extracting: (note skipped making labeled vids, they will be same anyways)
dlc.extract_outlier_frames('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,automatic=True)
# when done will
# 1. check config.yaml for correct paths to new unique files.. YES THERE
# 2. check labeled vids dir for frames and unique folders. YES THERE
# 3. check videos folder for vids.. not links! why? did we have copy=True  NO THEY ARE LINKS! All good.
# 4. Run the refiner gui:
dlc.refine_labels('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml')
# OKay done! did 6 videos, 10 each, using instructions from this page:
# https://guillermohidalgogadea.com/openlabnotebook/refining-your-dlc-model/
# now merge:

'''
The following folder was not manually refined,... /zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/labeled-data/.DS_Store
The following folder was not manually refined,... /zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/labeled-data/fr_wbgam_h264_nearlossless_safe
The following folder was not manually refined,... /zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/labeled-data/._.DS_Store
Please label, or remove the un-corrected folders.

deleted fr...

(base) spencelab@agatha:~$ cd /zfsr01/storage/ajay20220823/
(base) spencelab@agatha:/zfsr01/storage/ajay20220823$ ls
ajay_analysis.py  cam2                    forelimb-BR-2022-08-24_BACKUPBEFOREREFINE_AJS
cam1              forelimb-BR-2022-08-24  tmill_logs
(base) spencelab@agatha:/zfsr01/storage/ajay20220823$ cd forelimb-BR-2022-08-24
(base) spencelab@agatha:/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24$ ll
total 89
drwxrwxr-x  7 spencelab spencelab   10 Aug 25 09:00 ./
drwxrwxr-x  7 spencelab spencelab   10 Oct  3 10:12 ../
-rw-rw-r--  1 spencelab spencelab 2673 Oct  3 16:27 config.yaml
drwxrwxr-x  3 spencelab spencelab    5 Aug 25 09:03 dlc-models/
-rwxr--r--  1 spencelab spencelab 4096 Aug 25 09:00 ._.DS_Store*
-rwxr--r--  1 spencelab spencelab 8196 Aug 25 09:52 .DS_Store*
drwxrwxr-x  3 spencelab spencelab    5 Aug 25 09:01 evaluation-results/
drwxrwxr-x 13 spencelab spencelab   15 Oct  3 17:24 labeled-data/
drwxrwxr-x  3 spencelab spencelab    5 Aug 25 09:01 training-datasets/
drwxrwxr-x  2 spencelab spencelab   14 Oct  3 16:27 videos/
(base) spencelab@agatha:/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24$ rm .DS_Store 
(base) spencelab@agatha:/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24$ rm ._.DS_Store 
(base) spencelab@agatha:/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24$

OOPS HAD TO GO INSIDE LABELED! THEN RM 
'''
dlc.merge_datasets('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml')
# worked!
#In [15]: dlc.merge_datasets('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml')
#Merged data sets and updated refinement iteration to 1.
#Now you can create a new training set for the expanded annotated images (use create_training_dataset).

dlc.create_training_dataset('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',num_shuffles=1)
#The training dataset is successfully created. Use the function 'train_network' to start training. Happy training!

# okay now lets retrain starting with old params!
# COPIED THE PATH FROM ITERATION-0 INTO ITERATION 1 POSE CFG: MADE IT THIS LINE:
# init_weights: /zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/dlc-models/iteration-0/forelimbAug24-trainset95shuffle1/train/snapshot-200000
dlc.train_network('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',maxiters=200000)
# err might be going. heating up... long output below...
'''
Starting training....
iteration: 1000 loss: 0.0039 lr: 0.005
iteration: 2000 loss: 0.0037 lr: 0.005
iteration: 3000 loss: 0.0035 lr: 0.005
'''
# ok it worked but i'm getting warnings about one of the zfs drives failing now... yikes! ordering replacement and bringing home 
# the mirror to duplicate it ASAP!
dlc.evaluate_network('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',Shuffles=[1],plotting=True)
# ok hmm. looks good in evaluation pics but only one test from the newer dates! random sample luck?
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,shuffle=1,save_as_csv=True)
# ok says video already analyzed... but with the old network? yeah that's what it seems like by time stamp.
# hmm manually deleted the data for 11-10-28
# now it's redoing that one
dlc.create_labeled_video('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,draw_skeleton=True)
# and when redone it looked awesome!
# manually delted the rest... and reanalyzed and remade vids
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,shuffle=1,save_as_csv=True)
dlc.create_labeled_video('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,draw_skeleton=True)
# WOW THEY LOOK GOOD. PERFECT WHEN VISIBLE EXCEPT:
# 11_53_05 BLIPS OVER TO EYE A TINY BIT
# 12_33_23 one blip to tail marker

# Okay now doing more:
'''
In [1]: vids=['/zfsr01/storage/ajay20220823/cam2/2022-09-29_11_48_18/2022-09-29_11_48_18_fr_wbgam_h26
   ...: 4_nearlossless_safe.mp4', '/zfsr01/storage/ajay20220823/cam2/2022-09-29_11_50_45/2022-09-29_1
   ...: 1_50_45_fr_wbgam_h264_nearlossless_safe.mp4', '/zfsr01/storage/ajay20220823/cam2/2022-09-29_1
   ...: 1_51_42/2022-09-29_11_51_42_fr_wbgam_h264_nearlossless_safe.mp4' , '/zfsr01/storage/ajay20220
   ...: 823/cam2/2022-09-29_11_54_06/2022-09-29_11_54_06_fr_wbgam_h264_nearlossless_safe.mp4' ,'/zfsr
   ...: 01/storage/ajay20220823/cam2/2022-09-29_11_45_33/2022-09-29_11_45_33_fr_wbgam_h264_nearlossle
   ...: ss_safe.mp4' ]
'''

# 2023-06-06 We have a ton of wonderful new Ajay data let's run analyze videos and see if it works on the dark ones.
'''
conda activate DLC-GPU
ipython3
import tensorflow as tf
gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.7)
sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
import deeplabcut as dlc

dlc.analyze_videos(config5,vidz,shuffle=1,save_as_csv=True)
dlc.create_labeled_video(config5,vidz,draw_skeleton=True)
dlc.plot_trajectories(config5,vidz)
'''
vidslist=['/zfsr01/storage/ajay20220823/cam2/2023-03-01_14_27_16/fr_wbgam_h264.mp4']
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,shuffle=1,save_as_csv=True)
dlc.create_labeled_video('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,draw_skeleton=True)

# ok that wasn't so bad actually. only struggled with blips to the eye. at some points.
# let's do one across all time points to see how bad the dark stuff is going to be.
vidslist=['/zfsr01/storage/ajay20220823/cam2/2023-03-13_11_49_40/fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-03-23_09_44_43/fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-03-23_10_06_04/fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-04-07_10_19_12/fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-04-18_15_16_39/fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-04-20_11_25_18/fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-05-02_10_45_11/fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-05-17_10_54_47/fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-05-18_10_53_22/fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-05-25_09_48_32/fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-05-31_08_27_00/fr_wbgam_h264.mp4']
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,shuffle=1,save_as_csv=True)
dlc.create_labeled_video('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,draw_skeleton=True)

# Okay i made notes on the results of those tracks in this sheet:
# https://tuprd.sharepoint.com/:x:/r/sites/SpenceLab/_layouts/15/doc2.aspx?sourcedoc=%7BBD1B475F-A213-4FBE-8429-7EA586ABAA24%7D&file=AjayPilotVideosAnalysis.xlsx&action=default&mobileredirect=true
# And came up with a plan for the anlaysis here:
# https://tuprd.sharepoint.com/:w:/r/sites/SpenceLab/_layouts/15/Doc.aspx?sourcedoc=%7B0B59E929-DD53-48C1-9280-FBB3CB8B3228%7D&file=AjayPilot20220823KinematicsLog.docx&action=default&mobileredirect=true
# First need to rename the files to unique, and generate an excel sheet of them
# so Ajay/someone can copy the rat and speed over.
# Then, while they do that, I will refine the model and start training tonight...

# let's just copy the files, not rename them, and hope for best.
allvids=[]
allvidsfull=[]
import os, shutil
for dirpath, sub_directories, files in os.walk(os.getcwd()):
   for file in files:
     #study_name = os.path.split(path)[0].split("/")[-5]
     #study_name = os.path.split(path)[0].split("/")[-4]
     #week_num = os.path.split(path)[0].split("/")[-3]
     #cam_num = os.path.split(path)[0].split("/")[-2]
     #rat_num = os.path.split(path)[0].split("/")[-1]
     folder_name = os.path.split(dirpath)[1] # this folder contains the .mp4
     #print(folder_name)
     ##  create what you want the file to be renamed as
     #extension = os.path.splitext(file)[1] # extension of the file you want to change
         ## if you want to change all of the files in a folder, use:
             # extension = os.path.splitext(file)[1]
     source = os.path.join(dirpath, file)
     #print(source)
     if file == "fr_wbgam_h264.mp4" and folder_name.startswith("2023"):
       trg = os.path.join(dirpath, folder_name + "_" + file)
       print('  yes', source, " to ", trg)
       #shutil.copy(source,trg)
       allvidsfull.append(trg)

# Okay that worked. Wasteful, but worked. Now export the list of videos:
import pandas as pd
vdf=pd.DataFrame({'video':allvids})
vdf.to_csv('allvids2023.csv')
vdff=pd.DataFrame({'video':allvidsfull})
vdff.to_csv('allvidsfull2023.csv')

# Ok yeah wow there are 510 vids. awesome. that's 18gb. for a whole study!
# much more manageable.
# Okay following above, i need to re-analyze using the unique file names:
vidslist=['/zfsr01/storage/ajay20220823/cam2/2023-03-13_11_49_40/2023-03-13_11_49_40_fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-03-23_09_44_43/2023-03-23_09_44_43_fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-03-23_10_06_04/2023-03-23_10_06_04_fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-04-07_10_19_12/2023-04-07_10_19_12_fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-04-18_15_16_39/2023-04-18_15_16_39_fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-04-20_11_25_18/2023-04-20_11_25_18_fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-05-02_10_45_11/2023-05-02_10_45_11_fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-05-17_10_54_47/2023-05-17_10_54_47_fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-05-18_10_53_22/2023-05-18_10_53_22_fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-05-25_09_48_32/2023-05-25_09_48_32_fr_wbgam_h264.mp4',
'/zfsr01/storage/ajay20220823/cam2/2023-05-31_08_27_00/2023-05-31_08_27_00_fr_wbgam_h264.mp4']
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,shuffle=1,save_as_csv=True)
dlc.create_labeled_video('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,draw_skeleton=True)

# ok did this work with new filenames?
# yep i see videos there. ok now i need to extract outliers... do i hope this will give me
# enough examples of eyes flickering? let's do it by bandwidth... how much time do i have.
# I added 11 videos. 3 markers per frame. 30 per vid, 11 vid, 3 per = 990 clicks. 1 click per second
# 16.5 min... triple it. 1hr. try it...
# config has numframes to pick at 10... start there? lets' try leaving numframes at 10.  so 11*10*3=330 markers to fix.
# Ok yeah i think it's good... it grabbed random assortment with some eye jumps! it's using jump method.
# found 212 frames in first vid, then took 10, and then 87, then 53
dlc.extract_outlier_frames('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',vidslist,automatic=True)
# this is puttig stuff in labelled_videos which is great. it does seem a good outlier sample.
# hmm the vids don't look that dark in the pngs... i think it is the movie player!
# Trade off between time investment in labeling and training. How long did the retraining take last time?
# Once above is done will do: PS I kept the config open in sublime on accident and you can see the vids
# added as you go... also links to vids? What does the config look like after you extract but before you refine?
# Just has them added without the question marks. Hmm.
dlc.refine_labels('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml')
# Okay that went fine. Took about 45 minutes... for 330 markers...
# So if I wanted to add more I could add analyze more novel videos, extract, and refine them.
# I'm not sure what happens to my refined labels if I simply increase num2extract in config and rerun with current vids.
# In any case, now i'll start the model training hoping that 330 is enough to fix the eye and handle the dark videos.
# Let's measure training time too.
dlc.merge_datasets('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml')
'''
In [41]: dlc.merge_datasets('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml')
    ...: 
Merged data sets and updated refinement iteration to 2.
Now you can create a new training set for the expanded annotated images (use create_training_dataset).
'''
dlc.create_training_dataset('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',num_shuffles=1)
'''
The training dataset is successfully created. Use the function 'train_network' to start training. Happy training!
'''
# Hmm now do i want to copy past weights?
# Hmm so my iteration-0 started with resnet defaults:
# /zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/dlc-models/iteration-0/forelimbAug24-trainset95shuffle1/train/pose_cfg.yaml
# has: init_weights: /home/spencelab/anaconda3/envs/DLC-GPU/lib/python3.7/site-packages/deeplabcut/pose_estimation_tensorflow/models/pretrained/resnet_v1_50.ckpt
# But i started my iteration 1 with
# init_weights: /zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/dlc-models/iteration-0/forelimbAug24-trainset95shuffle1/train/snapshot-200000
# And now my iteration 2 comes fresh with:
# init_weights: /home/spencelab/anaconda3/envs/DLC-GPU/lib/python3.7/site-packages/deeplabcut/pose_estimation_tensorflow/models/pretrained/resnet_v1_50.ckpt
# I don't know whether to start it over from scratch or from iteration1... could drop into local minima? could also just be faster...
# HERES YOUR ANSWER FROM MACKENZIE:
# https://forum.image.sc/t/re-training-strategy-init-weights-from-resnet50-or-last-snapshot/22793?u=aspence
# YOU CAN RESTART FROM WEIGHTS OF LAST ITERATION NOT RESNET AFTER REFINING.
# let's try from iter1. i'm pasting into this file:
# /zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/dlc-models/iteration-2/forelimbAug24-trainset95shuffle1/train/pose_cfg.yaml
# this weights: /zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/dlc-models/iteration-1/forelimbAug24-trainset95shuffle1/train/snapshot-200000
# Starting at 2023-06-06 at 1611pm
dlc.train_network('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',maxiters=200000)
# ok looked up how to restart training from snapshots and then killed train at 117000 with ctrl-c.
# ok this killed ipython. pressing q didn't work. so did ctrl-c. had to restart ipython.
# want to see if good enough now. if not restart train, if so start analyzing vids:
# from 1611pm to 2121pm did 117000 iters. 5 hrs. So total train from last iteration would be 9 hours or so.
# let's evaluate and look at pixel error:
dlc.evaluate_network('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',Shuffles=[1],plotting=True)
# ok seems working used parameters from iteration-2 snapshot 100000.
'''
Analyzing data...
920it [01:28, 10.40it/s]
Done and results stored for snapshot:  snapshot-100000
Results for 100000  training iterations: 95 1 train error: 3.47 pixels. Test error: 3.82  pixels.
With pcutoff of 0.1  train error: 3.47 pixels. Test error: 3.82 pixels
Thereby, the errors are given by the average distances between the labels by DLC and the scorer.
'''
# IS this good or bad?
# https://forum.image.sc/t/re-training-strategy-init-weights-from-resnet50-or-last-snapshot/22793?u=aspence
# She think 2.41 test set is good, so 3.82 not bad... especially for our high res. but does it track?
# ARgh it's plotting 237/920...
# Ok so need to be careful int he evalution results folder. 95% are training images...
# Up the top are the 5% test images. So far none are from my new trained images...
# Ooh yay there are some and they are good.
'''
The network is evaluated and the results are stored in the subdirectory 'evaluation_results'.
If it generalizes well, choose the best model for prediction and update the config file with the appropriate index for the 'snapshotindex'.
Use the function 'analyze_video' to make predictions on new videos.
Otherwise consider retraining the network (see DeepLabCut workflow Fig 2)
'''
# Ok let's get it to start analyzing all the videos. It might take 18 hours so I shouold randomize the order.
# 1. Regenerate allvids after restarting python:
# 2. Analyze and plot the first 10 random, take a look
# 3. If ok analyze and plot them all... will generate another 10gb of sanity check movies lol
# ok made allvidsrel. first 7 is a bit of spread.
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',allvidsrel[0:7],shuffle=1,save_as_csv=True)
# takes about 1:17 to analyze one. 77*510/3600 = 10.9 hours to analyze. making vids faster...
# have about 12 hours. would like to analyze and make vids for as many as possible.
dlc.create_labeled_video('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',allvidsrel[0:7],draw_skeleton=True)
# Got error hopefuly because using relative paths. redoing.
# OK IF YOU ACCIDENTALLY ANALYZE YOUR VIDEOS WITH RELATIVE PATHS AND IT WONT LET YOU MAKE VIDEOS
# YOU CAN SIMPLY CREATE LABELLED VIDEOS WITH FULL PATHS AND RESCuE THIngS I HOPE.
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',allvidsfull[0:1],shuffle=1,save_as_csv=True)
# crap is says already analyzed... try vids with full path?
dlc.create_labeled_video('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',allvidsfull[1:7],draw_skeleton=True)
# HOLY COW THE FIRST THREE LOOK AMAAZING
# the fourth struggle but markers aren't there! /zfsr01/storage/ajay20220823/cam2/2023-05-31_09_16_51/2023-05-31_09_16_51_fr_wbgam_h264DLC_resnet50_forelimbAug24shuffle1_100000_labeled.mp4
# fifth also godo when markers there
# sixth great
# 7th was dark and wow it's nigh on perfect /zfsr01/storage/ajay20220823/cam2/2023-04-18_15_30_01/2023-04-18_15_30_01_fr_wbgam_h264DLC_resnet50_forelimbAug24shuffle1_100000_labeled.mp4
# but animal at front of treadmill reared up... this could confound...
# Ok it takes 9 seconds to make videos!
# so 77+9+fudge = 90 seconds to analyze and make video per video.
# start at 1012 pm, end at 10am. call it 11 hours.
# 11*60/1.5=440 videos.
# Ok let's analyze the first 440 videos...
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',allvidsfull[7:(7+440)],shuffle=1,save_as_csv=True)
dlc.create_labeled_video('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',allvidsfull[7:(7+440)],draw_skeleton=True)

# GAH! Bad video! Crashed is. Need try/catch.
# 275 ./2023-04-20_12_28_46/2023-04-20_12_28_46_fr_wbgam_h264.mp4
# 200 bytes or something. bad. dump.
# I'll make vids for what we have 
# In [46]: allvidsfull[275]
# Out[46]: '/zfsr01/storage/ajay20220823/cam2/2023-04-20_12_28_46/2023-04-20_12_28_46_fr_wbgam_h264.mp4
# Actaully nah keep analyzing... going to analyze without looking first anyways.
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',allvidsfull[276:(276+80)],shuffle=1,save_as_csv=True)
# started and stopped...
# SKIPPED OVER ./2023-05-02_10_44_34/2023-05-02_10_44_34_fr_wbgam_h264.mp4
# Need to go back and do.
dlc.create_labeled_video('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',allvidsfull[7:(7+440)],draw_skeleton=True)
# Shuold be able to mung all h5 data into one file <80mb.
# Make multindex with file before frame.
# Strategy: big list of dataframes and then do pandas vertcat.
# Find all the h5 files...
import os, pandas as pd
alldat=[]
for dirpath, sub_directories, files in os.walk(os.getcwd()):
   for file in files:
     folder_name = os.path.split(dirpath)[1] # this folder contains the .mp4
     source = os.path.join(dirpath, file)
     if file.endswith("DLC_resnet50_forelimbAug24shuffle1_100000.h5") and folder_name.startswith("2023"):
       alldat.append(source)
adf=[]
for f in alldat:
   d0=pd.read_hdf(f)
   # Convert index to dataframe
   old_idx = d0.index.to_frame()
   # Insert new level at specified location
   old_idx.insert(0, 'video', f.split('/')[-2])
   # Convert back to MultiIndex
   d0.index = pd.MultiIndex.from_frame(old_idx)
   adf.append(d0)
adf=pd.concat(adf)
adf.to_hdf('alldata.h5',key='df')

# THe analyzis as of 2023-06-06 945am has gone up to 
# 384   ./2023-04-20_11_38_51/2023-04-20_11_38_51_fr_wbgam_h264.mp4
# with the one file above that has an empyt movie to be removed.
# The above alldata.h5 has fewer was created while more were analyzed.
# Ok restarting at 2023-0607 2037pm
dlc.analyze_videos('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',allvidsfull[384:],shuffle=1,save_as_csv=True)

# now make labelled vids for all..
# wait remove the bad one
allvidsfull.remove('/zfsr01/storage/ajay20220823/cam2/2023-04-20_12_28_46/2023-04-20_12_28_46_fr_wbgam_h264.mp4')
dlc.create_labeled_video('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',allvidsfull,draw_skeleton=True)

'''
Step 3: Fixing Errors
After extracting the outlier frames, your actual work can begin. The function below starts a graphical interface to refine labels manually:

deeplabcut.refine_labels(path_config_file)
First, you need to load the directory with frames you want to refine, and then load the corresponding .h5 file with the outlier predictions from the previous model. You are asked to define a likelihood threshold, but don’t worry too much about it - this is only to show you which labels have an especially low prediction. Labels with a likelihood higher than your threshold will appear as opaque colored circles, while labels below the threshold will appear as transparent colored circles. As I am going to refine all labels, and I recommend you do the same, I like setting the threshold to 1 to display all markers transparent. This makes it somewhat easier to place the center of the marker when you zoom in.

The refining process is overall very similar to labeling, except that the labels are already placed somewhere in the frame. You drag them holding the left mouse key and drop them in place. Delete labels that are not supposed to be in the frame by clicking the mouse wheel. Make sure to delete all labels that are not visible and suppress your ‘knowing’ where the eyebrow is behind that strand of hair: if you don’t see it, don’t label it. A minimal difference from the original labeling process is the fact that instead of saving and quitting to go on labeling other files, you will be prompted to refine other files directly after clicking save. The Quit button will close the GUI without redirecting you to new files… and that may cause your notebook to crash. In that case try restarting the kernel from your jupyter notebook.
'''

'''
In [17]: dlc.train_network('/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/config.yaml',maxiters
    ...: =200000)
Config:
{'all_joints': [[0], [1], [2], [3]],
 'all_joints_names': ['Collarbone', 'Shoulder', 'Elbow', 'Wrist'],
 'batch_size': 1,
 'bottomheight': 400,
 'crop': True,
 'crop_pad': 0,
 'cropratio': 0.4,
 'dataset': 'training-datasets/iteration-1/UnaugmentedDataSet_forelimbAug24/forelimb_BR95shuffle1.mat',
 'dataset_type': 'default',
 'deconvolutionstride': 2,
 'deterministic': False,
 'display_iters': 1000,
 'fg_fraction': 0.25,
 'global_scale': 0.8,
 'init_weights': '/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/dlc-models/iteration-0/forelimbAug24-trainset95shuffle1/train/snapshot-200000',
 'intermediate_supervision': False,
 'intermediate_supervision_layer': 12,
 'leftwidth': 400,
 'location_refinement': True,
 'locref_huber_loss': True,
 'locref_loss_weight': 0.05,
 'locref_stdev': 7.2801,
 'log_dir': 'log',
 'max_input_size': 1500,
 'mean_pixel': [123.68, 116.779, 103.939],
 'metadataset': 'training-datasets/iteration-1/UnaugmentedDataSet_forelimbAug24/Documentation_data-forelimb_95shuffle1.pickle',
 'min_input_size': 64,
 'minsize': 100,
 'mirror': False,
 'multi_step': [[0.005, 10000],
                [0.02, 430000],
                [0.002, 730000],
                [0.001, 1030000]],
 'net_type': 'resnet_50',
 'num_joints': 4,
 'num_outputs': 1,
 'optimizer': 'sgd',
 'output_stride': 16,
 'pos_dist_thresh': 17,
 'project_path': '/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24',
 'regularize': False,
 'rightwidth': 400,
 'save_iters': 50000,
 'scale_jitter_lo': 0.5,
 'scale_jitter_up': 1.25,
 'scoremap_dir': 'test',
 'shuffle': True,
 'snapshot_prefix': '/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/dlc-models/iteration-1/forelimbAug24-trainset95shuffle1/train/snapshot',
 'stride': 8.0,
 'topheight': 400,
 'weigh_negatives': False,
 'weigh_only_present_joints': False,
 'weigh_part_predictions': False,
 'weight_decay': 0.0001}
Switching batchsize to 1, as default/tensorpack/deterministic loaders do not support batches >1. Use imgaug loader.
Starting with standard pose-dataset loader.
Initializing ResNet
WARNING:tensorflow:From /home/spencelab/anaconda3/envs/DLC-GPU/lib/python3.7/site-packages/tensorflow/python/ops/losses/losses_impl.py:209: to_float (from tensorflow.python.ops.math_ops) is deprecated and will be removed in a future version.
Instructions for updating:
Use tf.cast instead.
WARNING:tensorflow:From /home/spencelab/anaconda3/envs/DLC-GPU/lib/python3.7/site-packages/tensorflow/python/ops/losses/losses_impl.py:209: to_float (from tensorflow.python.ops.math_ops) is deprecated and will be removed in a future version.
Instructions for updating:
Use tf.cast instead.
Loading already trained DLC with backbone: resnet_50
2022-10-03 17:36:44.456199: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1512] Adding visible gpu devices: 0
2022-10-03 17:36:44.456233: I tensorflow/core/common_runtime/gpu/gpu_device.cc:984] Device interconnect StreamExecutor with strength 1 edge matrix:
2022-10-03 17:36:44.456239: I tensorflow/core/common_runtime/gpu/gpu_device.cc:990]      0 
2022-10-03 17:36:44.456244: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1003] 0:   N 
2022-10-03 17:36:44.456299: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1115] Created TensorFlow device (/job:localhost/replica:0/task:0/device:GPU:0 with 5585 MB memory) -> physical GPU (device: 0, name: NVIDIA GeForce RTX 2080, pci bus id: 0000:01:00.0, compute capability: 7.5)
INFO:tensorflow:Restoring parameters from /zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/dlc-models/iteration-0/forelimbAug24-trainset95shuffle1/train/snapshot-200000
INFO:tensorflow:Restoring parameters from /zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/dlc-models/iteration-0/forelimbAug24-trainset95shuffle1/train/snapshot-200000
Max_iters overwritten as 200000
Training parameter:
{'stride': 8.0, 'weigh_part_predictions': False, 'weigh_negatives': False, 'fg_fraction': 0.25, 'weigh_only_present_joints': False, 'mean_pixel': [123.68, 116.779, 103.939], 'shuffle': True, 'snapshot_prefix': '/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/dlc-models/iteration-1/forelimbAug24-trainset95shuffle1/train/snapshot', 'log_dir': 'log', 'global_scale': 0.8, 'location_refinement': True, 'locref_stdev': 7.2801, 'locref_loss_weight': 0.05, 'locref_huber_loss': True, 'optimizer': 'sgd', 'intermediate_supervision': False, 'intermediate_supervision_layer': 12, 'regularize': False, 'weight_decay': 0.0001, 'mirror': False, 'crop_pad': 0, 'scoremap_dir': 'test', 'batch_size': 1, 'dataset_type': 'default', 'deterministic': False, 'crop': True, 'cropratio': 0.4, 'minsize': 100, 'leftwidth': 400, 'rightwidth': 400, 'topheight': 400, 'bottomheight': 400, 'all_joints': [[0], [1], [2], [3]], 'all_joints_names': ['Collarbone', 'Shoulder', 'Elbow', 'Wrist'], 'dataset': 'training-datasets/iteration-1/UnaugmentedDataSet_forelimbAug24/forelimb_BR95shuffle1.mat', 'init_weights': '/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24/dlc-models/iteration-0/forelimbAug24-trainset95shuffle1/train/snapshot-200000', 'net_type': 'resnet_50', 'num_joints': 4, 'num_outputs': 1, 'output_stride': 16, 'deconvolutionstride': 2, 'display_iters': 1000, 'max_input_size': 1500, 'metadataset': 'training-datasets/iteration-1/UnaugmentedDataSet_forelimbAug24/Documentation_data-forelimb_95shuffle1.pickle', 'min_input_size': 64, 'multi_step': [[0.005, 10000], [0.02, 430000], [0.002, 730000], [0.001, 1030000]], 'pos_dist_thresh': 17, 'project_path': '/zfsr01/storage/ajay20220823/forelimb-BR-2022-08-24', 'save_iters': 50000, 'scale_jitter_lo': 0.5, 'scale_jitter_up': 1.25}
Starting training....
iteration: 1000 loss: 0.0039 lr: 0.005
iteration: 2000 loss: 0.0037 lr: 0.005
iteration: 3000 loss: 0.0035 lr: 0.005

Starting training....
iteration: 1000 loss: 0.0039 lr: 0.005
iteration: 2000 loss: 0.0037 lr: 0.005
iteration: 3000 loss: 0.0035 lr: 0.005
iteration: 4000 loss: 0.0037 lr: 0.005
iteration: 5000 loss: 0.0035 lr: 0.005
iteration: 6000 loss: 0.0036 lr: 0.005
iteration: 7000 loss: 0.0035 lr: 0.005
iteration: 8000 loss: 0.0036 lr: 0.005
iteration: 9000 loss: 0.0036 lr: 0.005
iteration: 10000 loss: 0.0035 lr: 0.005
iteration: 11000 loss: 0.0037 lr: 0.02
iteration: 12000 loss: 0.0038 lr: 0.02
iteration: 13000 loss: 0.0037 lr: 0.02
iteration: 14000 loss: 0.0037 lr: 0.02
iteration: 15000 loss: 0.0037 lr: 0.02
iteration: 16000 loss: 0.0036 lr: 0.02
iteration: 17000 loss: 0.0036 lr: 0.02
iteration: 18000 loss: 0.0036 lr: 0.02
iteration: 19000 loss: 0.0038 lr: 0.02
iteration: 20000 loss: 0.0036 lr: 0.02
iteration: 21000 loss: 0.0036 lr: 0.02
iteration: 22000 loss: 0.0037 lr: 0.02
iteration: 23000 loss: 0.0036 lr: 0.02
iteration: 24000 loss: 0.0035 lr: 0.02
iteration: 25000 loss: 0.0035 lr: 0.02
iteration: 26000 loss: 0.0035 lr: 0.02
iteration: 27000 loss: 0.0035 lr: 0.02
iteration: 28000 loss: 0.0036 lr: 0.02
iteration: 29000 loss: 0.0036 lr: 0.02
iteration: 30000 loss: 0.0036 lr: 0.02
iteration: 31000 loss: 0.0036 lr: 0.02
iteration: 32000 loss: 0.0035 lr: 0.02
iteration: 33000 loss: 0.0037 lr: 0.02
iteration: 34000 loss: 0.0035 lr: 0.02
iteration: 35000 loss: 0.0036 lr: 0.02
iteration: 36000 loss: 0.0035 lr: 0.02
iteration: 37000 loss: 0.0034 lr: 0.02
iteration: 38000 loss: 0.0034 lr: 0.02
iteration: 39000 loss: 0.0035 lr: 0.02
iteration: 40000 loss: 0.0036 lr: 0.02
iteration: 41000 loss: 0.0034 lr: 0.02
iteration: 42000 loss: 0.0034 lr: 0.02
iteration: 43000 loss: 0.0035 lr: 0.02
iteration: 44000 loss: 0.0036 lr: 0.02
iteration: 45000 loss: 0.0035 lr: 0.02
iteration: 46000 loss: 0.0034 lr: 0.02
iteration: 47000 loss: 0.0036 lr: 0.02
iteration: 48000 loss: 0.0035 lr: 0.02
iteration: 49000 loss: 0.0034 lr: 0.02
iteration: 50000 loss: 0.0036 lr: 0.02
iteration: 51000 loss: 0.0035 lr: 0.02
iteration: 52000 loss: 0.0035 lr: 0.02
iteration: 53000 loss: 0.0035 lr: 0.02
iteration: 54000 loss: 0.0035 lr: 0.02
iteration: 55000 loss: 0.0036 lr: 0.02
iteration: 56000 loss: 0.0035 lr: 0.02
iteration: 57000 loss: 0.0035 lr: 0.02
iteration: 58000 loss: 0.0036 lr: 0.02
iteration: 59000 loss: 0.0035 lr: 0.02

'''

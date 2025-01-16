#alright need to mix and match our subdirectories so stuff works
#going to create a small folder on my laptop to mimic the current issue 

#probably need two loops? one to iterate through the folders and look at them and then another
#method to compare the datetimes to see which csv is the more recent of the two 
import os, datetime
import pandas as pd

#important note: /zfsr01/storage/contusions/baseline/cam#/rat/date/date
time_points=[
	'baseline/',
	'week2/',
	'week3/',
	'week4/',
	'week6/',
	'week7/',
	'week8/']

root_path='/zfsr01/storage/contusions/'

#make dictionary for later
data = {"date": [], "csv_path": []}

#join for needed paths, ignore extra folders in "contusions'
for date in time_points:
	folder_path = os.path.join(root_path,date)

	#safety check to see if the paths exist or not 
	if not os.path.exists(folder_path):
		print(f"skipping {folder_path}, does not exist.")
		continue

	#iterate through all subdirectories and if the folder starts with 20, then its a dated
	#folder for the analysis (none were completed 2100 bc thats a century)
	#(and i pray i will be dead by then)
	for root, dirs, _ in os.walk(folder_path):
		date_folders = [os.path.join(root, d) for d in dirs if d.startswith("20")] #works bc years

		#iterate through folders and see if it has "analyze" in it for analysis from dlc
		for date_folder in date_folders:
			analysis_dirs = [
				os.path.join(date_folder,d)
				for d in os.listdir(date_folder)
				if os.path.isdir(os.path.join(date_folder,d)) and "analyze" in d.lower()
			]

			#commented out bc a lot of output happening here
			if not analysis_dirs:
				#print(f"no analysis folder found in {date_folder}")
				continue

			#check to see which folders have multiple analysis
			if len(analysis_dirs) > 1:
				print(f"multiple analysis folders found in {date_folder}:{analysis_dirs}")


			'''
			---> getmtime <---
			Return the time of last modification of path. The return value is a number giving 
			the number of seconds since the epoch (see the time module). 
			Raise os.error if the file does not exist or is inaccessible.

			---> getctime <---
			Return the system’s ctime which, on some systems (like Unix) is the time of 
			the last change, and, on others (like Windows), is the creation time for path. 
			The return value is a number giving the number of seconds since the epoch (see 
			the time module). Raise os.error if the file does not exist or is inaccessible.
			'''

			most_recent_analysis = max(analysis_dirs, key=os.path.getctime)

			#compared with output from multiple analysis folder, yes this is 
			#choosing the most recent one every time. 
			print(f"most recent analysis folder in {date_folder}:{most_recent_analysis}")

			#join the most recent analysis file path and choose the file that ends
			#with ".csv" to be saved for our merge attempts
			csv_files =[
				os.path.join(most_recent_analysis,f)
				for f in os.listdir(most_recent_analysis)
				if f.endswith(".csv")
			]

			#append the csv files and pull the dates
			if csv_files:
				most_recent_csv = max(csv_files,key=os.path.getctime)
				data['date'].append(os.path.basename(date_folder))
				data['csv_path'].append(most_recent_csv)

#dataframe outside of loop
df = pd.DataFrame(data)

#okay now i need to make the paths paired properly
#so in column 1:cam3, need entries to most recent analysis of cam3
#in column2:cam4, need entries to most recent analysis of cam4.

#load dataframe again bc i dont like just passing
df["camera"] = df["csv_path"].apply(lambda x: "cam3" if "/cam3/" in x else "cam4")

#split into two and remove the paths
df_cam3 = df[df["camera"] == "cam3"].drop(columns=["camera"]).rename(columns={"csv_path": "cam3_path"})
df_cam4 = df[df["camera"] == "cam4"].drop(columns=["camera"]).rename(columns={"csv_path": "cam4_path"})

#merge on date column to match the dates
df_merged = pd.merge(df_cam3, df_cam4, on="date", how="outer")
print(df_merged)

#i dont like how many NaNs there are..... 
df_merged.to_csv("merged_analysis_files.csv", index=False)

#check which columns dont have a match pls
count_all_entries = df_merged.dropna().shape[0]
print(f"Number of rows with entries in all three columns: {count_all_entries}")
#answer:1639
#there are 16 videos that do not match on date or maybe are off by a second 
#or maybe just arent taken, im not sure, but 16 is not a lot, so.





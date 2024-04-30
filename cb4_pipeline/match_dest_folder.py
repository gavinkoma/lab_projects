import os
import re

def get_directory():
	return str(os.popen("pwd").read()).replace('\n','')

def list_csv_files(directory):
    csv_files = []
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            csv_files.append(file)
    return csv_files

def match_cam1_cam2(csv_files):
	pattern1 = re.compile(r'[Cc]am1')
	cam1_files = []
	cam2_files = []
	for filename in csv_files:
		#print(filename)
		if pattern1.search(filename):
			cam1_files.append(filename)
		else:
			cam2_files.append(filename)

	all_video_dic = {'camera1':cam1_files,
					'camera2':[]
					}
	for filename in cam1_files:
		#print(filename)
		pattern2 = r'\d{4}-\d{2}-\d{2}_\d{2}_\d{2}_\d{2}'
		match1 = re.search(pattern2,filename)
		#print(match1)
		print(filename)
		if match1:
			timestamp = match1.group()
			print("timestamp:",timestamp)
		else:
			print("No timestamp found")
			#break

		file_match = [x for x in cam2_files if timestamp in x]
		print(file_match)
		#all_video_list = all_video_list+file_match
		#all_video_list['camera1'] = all_video_list.get('camera1') + filename
		all_video_dic['camera2'] = all_video_dic.get('camera2') + file_match


	
	return all_video_dic

if __name__ == "__main__":
#def match_files():
	path = get_directory()
	csv_files = list_csv_files(path)
	all_video_dic = match_cam1_cam2(csv_files)
	#print(len(csv_files))
	#return csv_files

#match_files()







import os

#define the videos path and the labeled data path
videos_dir = ""
labeled_data_dir = ""

#just paste from config file the added videos
'''
Youll have to first find and replace the crop input with ", 
and then youll have to find and replace the front spacing with "
doing so will just create one big long list for you to copy and paste

'''
config_videos = [
    "/full/path/to/video1.mp4",
    "/full/path/to/video2.mp4",
    # ...
]

#get base names (no .mp4) from config
config_names = {os.path.splitext(os.path.basename(p))[0] for p in config_videos}

#get actual .mp4 files from videos/ (no extension)
actual_videos = {
    os.path.splitext(f)[0]
    for f in os.listdir(videos_dir)
    if f.endswith(".mp4")
}

#get folder names from labeled-data/
labeled_folders = {
    f for f in os.listdir(labeled_data_dir)
    if os.path.isdir(os.path.join(labeled_data_dir, f))
}

# ---- 5 CHECKS ----
#config names missing in videos/
missing_in_videos = config_names - actual_videos
#config names missing in labeled-data/
missing_in_labeled = config_names - labeled_folders
#extra video files not in config
extra_in_videos = actual_videos - config_names
#extra folders not in config
extra_in_labeled = labeled_folders - config_names
#videos in videos/ with no matching folder in labeled-data
videos_missing_labeled = actual_videos - labeled_folders


if missing_in_videos:
    print("in config but missing in 'videos/':")
    for name in sorted(missing_in_videos):
        print(f"  - {name}.mp4")

if missing_in_labeled:
    print("\nin config but missing in 'labeled-data/':")
    for name in sorted(missing_in_labeled):
        print(f"  - {name}/")

if extra_in_videos:
    print("\nextra .mp4s in 'videos/' not listed in config:")
    for name in sorted(extra_in_videos):
        print(f"  - {name}.mp4")

if extra_in_labeled:
    print("\nextra folders in 'labeled-data/' not listed in config:")
    for name in sorted(extra_in_labeled):
        print(f"  - {name}/")

if videos_missing_labeled:
    print("\nfiles in 'videos/' with no corresponding folder in 'labeled-data/':")
    for name in sorted(videos_missing_labeled):
        print(f"  - {name}.mp4")

if not (
    missing_in_videos
    or missing_in_labeled
    or extra_in_videos
    or extra_in_labeled
    or videos_missing_labeled
):
    print("all entries match across config, videos/, and labeled-data/")

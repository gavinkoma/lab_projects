import pandas as pd
import h5py
import numpy as np
import os



def find_datafiles(thedir='.',pattern='*.h5'):
    x = os.popen(f"find '{thedir}' -type f -iname '{pattern}'").read()
    return(x.split('\n')[:-1])

# read master sheet w calibs
# pain_annot_filled.xlsx
df = pd.read_excel("pain_annot_filled.xlsx")

# take video column, remove .mp4, match with that + * + _filtered.h5
# 10.21.2020_B21_DB_C001H001S0001DLC_resnet50_painaaJul25shuffle1_200000_filtered.h5

# get al lthe ctner paw perfect trials
# get appropriat paw marker x y
# calibrate
# write to h5
out=list()
for row in df.itertuples():
    if row.center_paw_marker_good=='perfect':
        f=find_datafiles('.',f'{row.video[0:-4]}*_filtered.h5')
        if f and (len(f)==1):
            print(f'Found single perfect center paw file {f}')
            hd=pd.read_hdf(f[0])
            hd.columns=hd.columns.droplevel('scorer')
            if row.paw_to_use == 'left':
                kin=hd.loc[:,('left_center_paw',['x','y'])]
            else:   
                kin=hd.loc[:,('right_center_paw',['x','y'])]
            # baseline it by subtracting first point:
            kin=kin-kin.iloc[0,:]
            # flip the y so up is positive:
            kin.iloc[:,1]=-kin.iloc[:,1]
            # calibrate to mm
            mmperpix=row.distance_mm/np.abs(row._4-row._5)
            kin=kin*mmperpix
            out.append({
                "id": row.video,
                "strain": "SD",
                "stimulus": ["VF100"],
                "time.series": np.array(kin).T,
                "startframe": row.startframe,
                "stopframe": row.stopframe
            })

# Create and write to an HDF5 file
with h5py.File("cpperfect.h5", "w") as h5file:
    for i, element in enumerate(out):
        group = h5file.create_group(f"element_{i}")
        group.create_dataset("id", data=element["id"])
        group.create_dataset("strain", data=np.string_(element["strain"]))
        group.create_dataset("stimulus", data=np.array(element["stimulus"], dtype='S'))
        group.create_dataset("time_series", data=element["time.series"])
        group.create_dataset("startframe", data=element["startframe"])
        group.create_dataset("stopframe", data=element["stopframe"])







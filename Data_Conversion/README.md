# Data conversion

After data capture from NYU X,  we will get 3 kind of data. They are XXXX.h5, XXXXX.pkl (correspond with kinect) and XXXX.csv(correspond with motion camera)

## For XXXX.csv

#### Mcam_raw2unified.py

change: the *src_path*, *dst_path*, *uni_src_path( = dst_path )*, *uni_dst_path30* and *uni_dst_path30*; in the *src_psth* there are several users' sub-folders

output : unified Rotated Mocam data (dtype:dict)


#### Mcam_raw2rawarray.py

output : kinect-like not unified array

## For XXXX.h5

#### Kh52avi.py   

 change: the *src_path* and *dst_path*, in the main data path there are several users' sub-folders

 output : avi files for color image, depth image and bodyindex.


## For XXXX.pkl

#### Kinect_raw2unified.py:

change: the *src_path* and *dst_path*, in the main data path there are several users' sub-folders

output : unified Kinect data (dtype:dict)


#### Rel_raw2array.py : (modified reliability)

change: *exeno*, *src_path* and *dst_path*
output: Rel array

#### raw2reliability.py (original reliability)

#### (other) Kinect_raw2unified_ary.py

for files all in the same folder and directly convert it to array type


#### raw2raw3D.py

create raw kinect data


## unified data 2 array data type

data_dict2ary.py


# Data corruption checking

#### animation.py

change: *src_path_M*, *src_path_K*, *m_data_path*, and *k_data_path*

input: unified Kinect & Mocap data -> synchronized data or not (if not: discard related data)

# -*- coding: utf-8 -*-
"""
Created on Sun Oct 08 23:02:31 2017

@author: medialab
"""

# === resize ===
# original size (798,438)
import cv2
import os, glob
impath   = 'C:/Users/medialab/Desktop/New folder/exercise 4/399x219/1/'
dst_path = 'C:/Users/medialab/Desktop/New folder/exercise 4/399x219/2/'

for idx,infile in enumerate(glob.glob( os.path.join(impath, '*.jpg') )[::-1]):

  img = cv2.imread(infile)
  simg = cv2.resize(img, (0,0), fx=1, fy=1) 
  fname =dst_path + str(idx).zfill(3)+'.jpg' 
  cv2.imwrite(fname,simg)


# build exercise animation dataset
import glob,os,cv2
import numpy as np
import h5py


f = h5py.File("399x219_ex4_comp.h5", "w")


for i in [0,1,2,3,4]:
    print i
    name = 'M'+str(i)
    
    src_path = 'C:/Users/medialab/Desktop/New folder/exercise 4/399x219/'+str(i)+'/'
    flist    = glob.glob( os.path.join(src_path, '*.jpg'))
    if (i == 1) | (i ==2):
        nframe   = len(flist)
        IMG      = np.zeros([nframe,219,399,3])
        for idx,infile in enumerate(flist):
            img = cv2.imread(infile)
            IMG[idx,:,:,:] = img
    else:
        nframe   = len(flist)/2
        IMG      = np.zeros([nframe,219,399,3])
        for idx,infile in enumerate(flist[::2]):
            img = cv2.imread(infile)
            IMG[idx,:,:,:] = img
    f.create_dataset(name, data = IMG, compression="gzip", compression_opts=9)
f.close()

# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 17:43:27 2017

@author: medialab

Mcam_raw2rawarray (kinect-like)
"""
import cPickle,glob,os,pdb
from Mocam2Kinect import *
import numpy as np

src_path = 'F:/AllData_0327/Motion and Kinect raw data/raw_MData/'
dst_path = 'F:/AllData_0327/Motion and Kinect raw data/Not_unified_Mdata/'



jidx = [0,1,2,3,4,5,6,8,9,10,20]



for subfolder in os.listdir(src_path):  
    filelist = glob.glob(os.path.join(src_path+subfolder, '*.pkl') ) # find all pkl files
    for infile in filelist:
        print infile
        data  = cPickle.load(file(infile,'rb'))
        J     = Mocam2Kinect(data)
        for i in jidx:
            if i == 0:
                Joints = J[i]
            else:
                Joints = np.vstack([Joints,J[i]])
                
        fname = dst_path + subfolder + '/'+infile.split('\\')[-1]
        cPickle.dump(Joints,file(fname,'wb'))
        
        
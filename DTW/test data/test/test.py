# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 18:22:08 2017

@author: medialab
"""

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from Kfunc.IO     import *
from Kfunc.finger import *
from Kfunc.skel   import skel
from Kfunc.model  import Human_mod   as Hmod
from Kfunc.Rel    import reliability as REL
from Kfunc.GPR    import GPR
from Kfunc.DTW    import DTW_matching
import ctypes,os
import pygame,h5py,datetime
import pdb,time,cv2,cPickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.externals import joblib
from collections import defaultdict

# DTW


#data       = h5py.File('GT_kinect_EX4_40_40_40.h5','r')
#gt_data    = {}
#gt_data[1] = data['GT_kinect_1'][:]
#gt_data[2] = data['GT_kinect_2'][:]
#gt_data[3] = data['GT_kinect_3'][:]
#gt_data[4] = data['GT_kinect_4'][:]
#data.close()


data       = h5py.File('GT_V_data_mod_EX4.h5','r')
gt_data    = {}
gt_data[1] = data['GT_1'][:]
gt_data[2] = data['GT_2'][:]
gt_data[3] = data['GT_3'][:]
gt_data[4] = data['GT_4'][:]
data.close()


#infile = 'C:/exercisetest/output/Qi_data20171016172808_ex4.pkl'
infile = 'D:/Project/K_project/output/Yao_data201710131636.pkl'


data  = cPickle.load(file(infile,'rb'))


# dtw parameter initialize
Dtw = {}
Dtw['decTh']       = 2000
Dtw['cnt']         = 0
Dtw['distp_prev']  = 0         
Dtw['distp_cmp']   = np.inf             
Dtw['oidx']        = 0      # initail
Dtw['gt_idx']      = 0 
Dtw['presv_size']  = 0
Dtw['idxlist']     = []   
Dtw['idx_cmp']     = 0
Dtw['fcnt']        = 0
### test###
Dtw['seglist']     = []
Dtw['seginidx']    = 0
###
#        
Dtw['dpfirst']     = {}
Dtw['dist_p']      = {}
Dtw['deflag_mul']  = defaultdict(lambda:(bool(False)))  
Dtw['seqlist']     = np.array([])                
Dtw['dcnt']        = 0 
Dtw['chk_flag']    = False
Dtw['exechk']      = True
Dtw['deflag']      = False   # decreasing flag
Dtw['onedeflag']   = False
Dtw['segini']      = True  
Dtw['evalstr']     = ''


cnt = 0

    
while ( Dtw['exechk'] & (cnt < (len(data)-1) )):
    
    joints     = data[cnt]['joints']    
    _, modJary = Hmod.human_mod_pts(joints,True) #modJary is 7*3 array 
    modJary    = modJary.flatten().reshape(-1,21)   #change shape to 1*21 array
    reconJ     = modJary
    Dtw.update(DTW_matching(Dtw,reconJ,gt_data))
    cnt += 1
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


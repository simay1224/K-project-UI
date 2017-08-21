# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 14:21:52 2017

@author: medialab
"""

import cPickle
import numpy as np
from scipy.spatial.distance import euclidean
import scipy.signal as signal
from fastdtw import fastdtw
import matplotlib.pyplot as plt

gt_src   = 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'
test_src = 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'

#gt_data      = cPickle.load(open(gt_src ,'rb') ,encoding = 'latin1')[18:,30:].T
#test_data    = cPickle.load(open(test_src,'rb') ,encoding = 'latin1')[18:,30:].T

gt_data      = cPickle.load(file(gt_src,'rb'))[12:,:].T
test_data    = cPickle.load(file(test_src,'rb'))[12:,:].T

# === initialization ===
e                   = 20
delta               = 6
distance_global     = []
distance_global_P   = []
distant_list        = []
count_global        = 0
distance_count      = 0
count_IO            = False
break_IO            = False
distance_previous   = np.inf
test_idx            = 0

# === data segment ===

th                  = 3


grad  = gt_data[:,6]-np.roll(gt_data[:,6],-1)
gidx  = np.arange(gt_data.shape[0])[np.abs(grad)<th]
#gidx  = np.append(np.append([0],gidx),[gt_data.shape[0]-1])
sidx  = gidx[np.abs(gidx-np.roll(gidx,1))>th]
eidx  = gidx[np.abs(gidx-np.roll(gidx,-1))>th]
idx   = list((sidx+eidx)//2)


# === main function ===

id_list=[]
for j in range (len(idx)-1): 
    test_data_p  = test_data + np.atleast_2d((gt_data[idx[j]]-test_data[test_idx]))
    print(test_data_p.shape)
    print(str(test_idx)+'   '+str(idx[j])+'    '+str(idx[j+1]))
    for i in range (itest_idx+50,test_data.shape[0]):















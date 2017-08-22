# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 14:21:52 2017

@author: medialab
"""

import cPickle,pdb
import numpy as np
from scipy.spatial.distance import euclidean
import scipy.signal as signal
from fastdtw import fastdtw
import matplotlib.pyplot as plt

gt_src   = 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'
test_src = 'Angela_2017-03-06 09.09.00 AM_ex4_FPS30_motion_unified.pkl'

#gt_data      = cPickle.load(open(gt_src ,'rb') ,encoding = 'latin1')[18:,30:].T
#test_data    = cPickle.load(open(test_src,'rb') ,encoding = 'latin1')[18:,30:].T

gt_data      = cPickle.load(file(gt_src,'rb'))[12:,:].T
test_data    = cPickle.load(file(test_src,'rb'))[12:,:].T

# === initialization ===
e                   = 20
delta               = 6
distance_global     = []
distance_global_P   = []
distlist            = []
distplist           = []
count_global        = 0
dist_cnt            = 0
count_IO            = False
break_IO            = False
#dist_prev           = np.inf
seglist             =[]
gtseglist           =[]
# === data segment ===

th                  = 3


grad  = gt_data[:,6]-np.roll(gt_data[:,6],-1)
gidx  = np.arange(gt_data.shape[0])[np.abs(grad)<th]
#gidx  = np.append(np.append([0],gidx),[gt_data.shape[0]-1])
sidx  = gidx[np.abs(gidx-np.roll(gidx,1))>th]
eidx  = gidx[np.abs(gidx-np.roll(gidx,-1))>th]
idx   = list((sidx+eidx)//2) + [len(gt_data)]
 

# === main function ===


cnt = 0
test_idx   = 0
chk_flag   = False
err        = []
dist_prev  = 0
distp_prev = 0 


for gt_idx in range(len(idx)-1):
    test_data_p  = test_data + np.atleast_2d((gt_data[idx[gt_idx],6]-test_data[test_idx,6]))
    distlist = []
    distplist = []
    for j in  range(test_idx+1,test_data.shape[0]-1):
        dist  , path   = fastdtw(gt_data[idx[gt_idx]:idx[gt_idx+1],6], test_data[test_idx:j,6]  , dist=euclidean)
        dist_p, path_p = fastdtw(gt_data[idx[gt_idx]:idx[gt_idx+1],6], test_data_p[test_idx:j,6], dist=euclidean)


        print j
        print dist
        print dist_p
        print np.abs(dist_p-dist)/dist
        
        distlist.append(dist)
        distplist.append(dist_p) 
        
        if j != (test_idx+1): 
            print dist_p-distp_prev
            if chk_flag:  # in check global min status
                cnt +=1
                err.append(np.abs(dist_p-dist)/dist) 
                if cnt == 20:
                    Err_mean = np.mean(err)
#                    pdb.set_trace()
                    print('err mean')
                    print(Err_mean)
                    if Err_mean <0.6:
                        chk_flag = False
                        seglist.append([test_idx,j-20])
                        gtseglist.append([idx[gt_idx],idx[gt_idx+1]])
                        test_idx = j-20+1
                        
                        break
                        
                    else:
                        print('Ooops!!')
                    
            else:    
                if (dist_p-distp_prev)>50:   # turning point
                    print (' ==============  turning ====================')

                    chk_flag = True
                    err      = []
                    cnt      = 0
                    
        dist_prev  = dist
        distp_prev = dist_p 
        print ('===========\n')
    






# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 16:27:57 2017

@author: medialab
"""

import h5py,cPickle,pdb,glob,os
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw,dtw
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf


src_path = 'D:/Project/K_project/data/unified data array/Unified_MData/'
name     = 'Andy_2017-03-06 02.19.08'
path     = 'C:/Users/medialab/Desktop/0919/0919/7 joints/'+name+'/DTW_path.pkl'
test_src = src_path + name +' PM_ex4_FPS30_motion_unified.pkl'



data       = h5py.File('GT_V_data_mod_EX4.h5','r')
gt_data    = {}
gt_data[1] = data['GT_1'][:]
gt_data[2] = data['GT_2'][:]
gt_data[3] = data['GT_3'][:]
gt_data[4] = data['GT_4'][:]

ii = 3
seg = 2
sidx = 210
eidx = 284
jidx = 6 

path_21  = np.array(cPickle.load(file(path,'rb'))[ii][seg-1]).T

test_data    = cPickle.load(file(test_src,'rb'))[12:,:][jidx,:].T



test_p = test_data + np.atleast_2d((gt_data[ii][0,jidx]-test_data[sidx]))
dist_p, path_p = fastdtw(gt_data[ii][:,jidx], test_p[0,sidx:eidx], dist=euclidean) 


path_p = np.array(path_p).T
plt.figure(1)
plt.plot(gt_data[ii][:,jidx],color = 'blue')
plt.plot(test_p[0,sidx:eidx],color = 'red')
plt.plot([path_21[0],path_21[1]],[gt_data[ii][path_21[0],jidx],test_p[0,sidx+path_21[1]]],'-k')
plt.title('DTW path from 21 coordinates')




plt.figure(2)
plt.plot(gt_data[ii][:,jidx],color = 'blue')
plt.plot(test_p[0,sidx:eidx],color = 'red')
plt.plot([path_p[0],path_p[1]],[gt_data[ii][path_p[0],jidx],test_p[0,sidx+path_p[1]]],'-k')
plt.title('DTW path from current coordinate')


plt.figure(3)
plt.plot(gt_data[ii][:,jidx],color = 'blue')
plt.plot(test_p[0,sidx:eidx],color = 'red')
plt.plot([path_21[0],path_21[1]],[gt_data[ii][path_21[0],jidx],test_p[0,sidx+path_21[1]]],'-k',color = 'green')
plt.plot([path_p[0],path_p[1]],[gt_data[ii][path_p[0],jidx],test_p[0,sidx+path_p[1]]],'-k',color ='black')

plt.show()










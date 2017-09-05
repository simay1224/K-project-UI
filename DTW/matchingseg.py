# -*- coding: utf-8 -*-
"""
Created on Tue Sep 05 14:48:06 2017

@author: medialab
"""

import h5py,cPickle
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy.signal import argrelextrema

src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'
#src_path  = 'D:/Project/K_project/data/unified data array/Unified_MData/'
gt_src   = 'GT_V_data.h5'

test_src = src_path + 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'

gt_data      = h5py.File('GT_V_data.h5','r')
gt1          = gt_data['GT_1'][:]
gt2          = gt_data['GT_2'][:]
gt3          = gt_data['GT_3'][:]
gt4          = gt_data['GT_4'][:]

test_data    = cPickle.load(file(test_src,'rb'))[12:,:].T

# === initialization ===
distlist            = []
distplist           = []

seglist             =[]
gtseglist           =[]

cnt         = 0
dcnt        = 0      # decreasing cnt
test_idx    = 0
offset      = test_idx 
chk_flag    = False
deflag      = False  # decreasing flag
err         = []
dist_prev   = 0
distp_prev  = 0 
distp_cmp  = np.inf




    test_data_p1  = test_data[:,:] + np.atleast_2d((gt1[]-test_data[test_idx,:]))
    
    distlist  = []
    distplist = []




















# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 14:54:00 2017

@author: medialab
"""

import cPickle
import numpy as np
import matplotlib.pyplot as plt


#src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'
src_path  = 'D:/Project/K_project/data/unified data array/Unified_MData/'

test_src = src_path + 'Danny_2017-02-24 03.22.19 PM_ex4_FPS30_motion_unified.pkl'
test_data    = cPickle.load(file(test_src,'rb'))[12:,:].T


plt.plot(test_data[:,6])
plt.show()
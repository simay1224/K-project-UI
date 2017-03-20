# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 15:05:46 2017

@author: medialab
"""

import h5py
import cPickle as pkl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np


src_path = 'F:/Kinect Project/20170306/Sophia/'
f = h5py.File(src_path + 'Sophia_data0306104952_ex4.h5','r')
kdata=pkl.load(file(src_path + 'Sophia_data0306104952_ex4.pkl','r'))

depth_data = f['imgs']['dimgs']

L =  int(kdata[5]['depth_jointspts'][4].x)
R =  int(kdata[5]['depth_jointspts'][8].x)
U =  int(kdata[5]['depth_jointspts'][20].y)
D =  int(kdata[5]['depth_jointspts'][1].y)

depth = []

for i in depth_data.keys():
    print i
    depth.append(depth_data[i][U:D,L+10:R-10,0].mean())
    
plt.plot(range(528),depth)
plt.show()
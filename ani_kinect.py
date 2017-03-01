# -*- coding: utf-8 -*-
"""
Created on Tue Dec 06 17:18:35 2016

@author: Dawnknight
"""

import cPickle,cv2 
import matplotlib.pyplot as plt

from Kfunc import *
from Kfunc.model import *
from mpl_toolkits.mplot3d import Axes3D


data = cPickle.load(file('./output/pkl/mocapdata1128_array.pkl','r'))





Kbody = Mocam2Kinect(data)

keys = Kbody.keys()
NUM_LABELS = len(keys)  # total number of the labels
NUM_FRAMES = Kbody[keys[0]].shape[1]   #total number of the frames
print 'The total frames: ', NUM_FRAMES

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for frame_no in range(50,400):
    plt.cla()
    
    xs = []
    ys = []
    zs = []
    kxs = []
    kys = []
    kzs = []
    
    
    for i in  xrange( NUM_LABELS ):
        kxs.append(Kbody[keys[i]][0][frame_no])
        kys.append(Kbody[keys[i]][1][frame_no])
        kzs.append(-1*Kbody[keys[i]][2][frame_no])
        
    for i in xrange(33):    
        xs.append(data['rcpos'][i*3][frame_no])
        ys.append(data['rcpos'][i*3+1][frame_no])
        zs.append(-1*data['rcpos'][i*3+2][frame_no])        
        
        
    ax.scatter(kxs, kzs, kys, c = 'red', s = 100,label='Kinect Joints')
    ax.scatter(xs, zs, ys, c = 'green',s = 50,alpha=.4,label='MoCam Joints')
    ax.set_xlim(-0.5,1.5)
    ax.set_ylim(-0.2,1.9)
    ax.set_zlim(1,2)
    ax.set_title(frame_no)
    plt.legend( loc=1)
    plt.draw()
    name = './data/'+repr(frame_no).zfill(3)+'.jpg'
    fig.savefig(name)
    plt.pause(1.0/120)


# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 13:19:13 2017

@author: medialab
"""

JointType_SpineBase = 0
JointType_SpineMid = 1
JointType_Neck = 2
JointType_Head = 3
JointType_ShoulderLeft = 4
JointType_ElbowLeft = 5
JointType_WristLeft = 6
JointType_HandLeft = 7
JointType_ShoulderRight = 8
JointType_ElbowRight = 9
JointType_WristRight = 10
JointType_HandRight = 11
JointType_HipLeft = 12
JointType_KneeLeft = 13
JointType_AnkleLeft = 14
JointType_FootLeft = 15
JointType_HipRight = 16
JointType_KneeRight = 17
JointType_AnkleRight = 18
JointType_FootRight = 19
JointType_SpineShoulder = 20
JointType_HandTipLeft = 21
JointType_ThumbLeft = 22
JointType_HandTipRight = 23
JointType_ThumbRight = 24

import h5py
import cPickle as pkl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np

f = h5py.File('F:/Kinect Project/20170306/Angela/Angela_data0306091154_ex4.h5','r')
kdata=pkl.load(file('F:/Kinect Project/20170306/Angela/Angela_data0306091154_ex4.pkl','r'))

depth_data = f['imgs']['dimgs']

# allt the bounding information was pick up from 6th frame
depth_base = kdata[5]['joints'][JointType_SpineBase].Position.z * 1000
base_level = kdata[5]['depth_jointspts'][JointType_SpineBase].y
head_level = kdata[5]['depth_jointspts'][JointType_Head].y
depth_xcenter = kdata[5]['depth_jointspts'][JointType_SpineBase].x

chest_depth = kdata[5]['joints'][20].Position.z * 1000



height = 424
width  = 512

fig = plt.figure()
ax = fig.gca(projection='3d')

Zpts = np.arange(2200,2400)
kernel = np.ones(200)

for frame_idx in range(120,200):
    
    depth_frame = depth_data['d_'+repr(frame_idx).zfill(4)][:,:,0]
    Rwx = kdata[frame_idx]['depth_jointspts'][JointType_WristRight].x
    Rwy = kdata[frame_idx]['depth_jointspts'][JointType_WristRight].y
    Rwz = kdata[frame_idx]['joints'][JointType_WristRight].Position.z * 1000
    Rwrel = kdata[frame_idx]['Rel'][JointType_WristRight]
    RTs = kdata[frame_idx]['joints'][JointType_WristRight].TrackingState

    Lwx = kdata[frame_idx]['depth_jointspts'][JointType_WristLeft].x
    Lwy = kdata[frame_idx]['depth_jointspts'][JointType_WristLeft].y    
    Lwz = kdata[frame_idx]['joints'][JointType_WristLeft].Position.z * 1000  
    Lwrel = kdata[frame_idx]['Rel'][JointType_WristLeft]
    LTs = kdata[frame_idx]['joints'][JointType_WristLeft].TrackingState                   
    plt.cla()
    
#     upper bound of height is head_loc+50, lower bound is Spinebase_loc

    ROI_y = np.zeros([height,width])                                     # setup boundry in y axis
    ROI_y[max(0,int(head_level)-50) :int(base_level),:] = 1              # setup boundry in y axis
    ROI = (((depth_base-500)<depth_frame) & (depth_frame<depth_base+500) )*ROI_y
    ROI_flat = np.where(ROI.flatten()!=0)[0]  
    
         
    xs  = ROI_flat% width
    ys  = (ROI_flat//width )*-1
    zs  = depth_frame.flatten()[ROI_flat]    
              
                
    ax.scatter(zs, xs, ys, marker = '.') # marker as point
    
    idx = np.where(zs<(chest_depth-150))     
    
    
    
    ax.scatter(zs[idx], xs[idx], ys[idx],color = 'r', marker = ',') # marker as point
    ax.scatter(Zpts,Rwx*kernel,-Rwy*kernel,color='g',s = 100)
    ax.scatter(Zpts,Lwx*kernel,-Lwy*kernel,color='y',s = 100)

    
    title = 'frame_'+repr(frame_idx)+'\n Lw :' + repr(round(Lwrel,2))+' value:('+repr(int(Rwx))+','+repr(int(Rwy))+') '+repr(RTs)\
                                    +'\n Rw :' + repr(round(Rwrel,2))+' value:('+repr(int(Lwx))+','+repr(int(Lwy))+') '+repr(LTs)
    
    ax.set_xlim(depth_base-500, depth_base+500)
    ax.set_ylim(depth_xcenter-150, depth_xcenter+150)
    ax.set_zlim(-260, -50)
    ax.set_title(title)
    ax.set_xlabel('Z axis')
    ax.set_ylabel('X axis')
    ax.set_zlabel('Y axis')
    plt.draw()
    plt.pause(1.0/120)


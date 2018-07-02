# -*- coding: utf-8 -*-
"""
Created on Fri Dec 02 13:04:16 2016

@author: liuqi
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

import cPickle as pk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

############################
# Motion capture
###########################
src_path_M = 'E:/Kinect_gaussian_5to7/Unified_M_data/ex6/'
src_path_K = 'E:/Kinect_gaussian_5to7/Unified_K_data/ex6/'
m_data_path = 'Qingyuan_2017-03-06 01.43.26 PM_ex6_FPS30_motion_unified'+'.pkl'
k_data_path = 'Qingyuan_data20170306134320_unified_ex6'+'.pkl'
data_all = pk.load(file(src_path_M+m_data_path))
kdata_all = pk.load(file(src_path_K+k_data_path))

NUM_LABELS = len(data_all)  # total number of the joints
NUM_FRAMES = len(data_all[0][1])   # total number of the frames
kNUM_FRAMES = len(kdata_all[0][1]) 

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim(-500,300)
ax.set_ylim(-1000,400)
ax.set_zlim(50,600)
ax.set_xlabel('Z axis')
ax.set_ylabel('X axis')
ax.set_zlabel('Y axis')

xs = []
ys = []
zs = []
kxs = []
kys = []
kzs = []

for joint_idx in  data_all.keys() :
    xs.append(0)
    ys.append(0)
    zs.append(0)     
    
    kxs.append(0)
    kys.append(0)
    kzs.append(0)


l_M, = ax.plot(xs,ys,zs, marker='o', linestyle='None', color='r',label='MoCam Joints')
l_K, = ax.plot(kxs,kys,kzs, marker='o', linestyle='None', color='b',label='Kinect Joints')
ax.legend( loc=1)
plt.draw()
for frame_no in xrange(min(kNUM_FRAMES,NUM_FRAMES)):
    xs = []
    ys = []
    zs = []
    kxs = []
    kys = []
    kzs = []

    for joint_idx in  data_all.keys() :
        xs.append(data_all[joint_idx][0][frame_no])
        ys.append(data_all[joint_idx][1][frame_no])
        zs.append(data_all[joint_idx][2][frame_no])     
        
        kxs.append(kdata_all[joint_idx][0][frame_no]-500)
        kys.append(kdata_all[joint_idx][1][frame_no])
        kzs.append(kdata_all[joint_idx][2][frame_no])

    l_M.set_data(xs,zs)
    l_M.set_3d_properties(ys)
    l_K.set_data(kxs,kzs)
    l_K.set_3d_properties(kys)

    plt.pause(0.0001)
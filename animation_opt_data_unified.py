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

import cPickle,h5py
import numpy as np
import glob,os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

############################
# Motion capture
###########################



#mpdata_all  = h5py.File('./data/GSP/opt_cor_0_gam_0.5_adj_0_relb_F/Andy_data201612151615_unified_ex4.h5')['data'][:]
#data_all    = h5py.File('./data/GSP/opt_cor_0_gam_0.005_adj_0_relb_F/Andy_data201612151615_unified_ex4.h5')['data'][:]
#data_all    = h5py.File('test123.h5')['data'][:]

#kdata_all  = h5py.File('D:/Project/K_project/data/unified GPR_K2M/Andy_data201612151615_unified_ex4.h5')['data'][:]
#mpdata_all  = h5py.File('D:/Project/K_project/data/unified Kprime smooth/Andy_data201612151615_unified_ex4.h5')['data'][:]

#mpdata_all = cPickle.load(file('D:/Project/K_project/data/unified GPR/Andy_data201612151615_unified_ex4.pkl'))
#data_all = cPickle.load(file('D:/Project/K_project/data/Motion and Kinect unified/Unified_MData/Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'))

kdata_all = cPickle.load(file('./data/unified data array/Unified_KData/Andy_data201612151615_unified_ex4.pkl'))
data_all  = cPickle.load(file('D:/Project/K_project/data/unified data array/Unified_MData/Andy_2017-03-06 02.19.08 PM_ex4_FPS30_motion_unified.pkl'))


#Rfile  = glob.glob(os.path.join('D:/Project/K_project/data/unified data array/reliability/','*ex4.pkl'))[0]
#rdata   = cPickle.load(file(Rfile,'rb'))
#Rel_th    =  0.7
#R  = rdata[4:10 ,:954]
#relidx = np.where(np.sum((R<Rel_th)*1,0)==0)[0] 

#NUM_LABELS = len(data_all)  # total number of the joints
#NUM_FRAMES = len(data_all[0][1])   # total number of the frames
#kNUM_FRAMES = len(kdata_all[0][1]) 
#print 'The total frames: ', NUM_FRAMES

fig = plt.figure(1)
ax = fig.add_subplot(111, projection='3d')


ax.set_xlabel('Z axis')
ax.set_ylabel('X axis')
ax.set_zlabel('Y axis')
    
for frame_no in xrange(1,10):#min(kNUM_FRAMES,NUM_FRAMES)):
    plt.cla()
    
#    mpxs = mpdata_all[0::3,frame_no]
#    mpys = mpdata_all[1::3,frame_no]
#    mpzs = mpdata_all[2::3,frame_no]

    kxs = kdata_all[0::3,frame_no]
    kys = kdata_all[1::3,frame_no]
    kzs = kdata_all[2::3,frame_no] 

    xs = data_all[0::3,frame_no]
    ys = data_all[1::3,frame_no]
    zs = data_all[2::3,frame_no] 

   
#    xs = []
#    ys = []
#    zs = []

#    kxs = []
#    kys = []
#    kzs = []


#    for joint_idx in  kdata_all.keys() :
#        xs.append(data_all[joint_idx][0][frame_no])
#        ys.append(data_all[joint_idx][1][frame_no])
#        zs.append(data_all[joint_idx][2][frame_no])
##        mxs.append(mdata[joint_idx][0][frame_no])
##        mys.append(mdata[joint_idx][1][frame_no])
##        mzs.append(mdata[joint_idx][2][frame_no])        
#        
#        kxs.append(kdata_all[joint_idx][0][frame_no])
#        kys.append(kdata_all[joint_idx][1][frame_no])
#        kzs.append(kdata_all[joint_idx][2][frame_no])
        


#    ax.scatter(kzs, kxs, kys, c = 'red', s = 30,label='Kinect Joints')    
    ax.scatter(zs, xs, ys,c = 'green',s = 100,alpha=.4,label='M')
#    ax.scatter(mpzs, mpxs, mpys,c = 'blue',s =50,alpha=.4,label='MP ')
    ax.set_xlim(-300,300)
    ax.set_ylim(-200,400)
    ax.set_zlim(50,600)

#    ax.set_xlim(2.4,2.6)
#    ax.set_ylim(-0.3,0.7)
#    ax.set_zlim(-0.3,-0.5)
    ax.set_title(frame_no)
    ax.set_xlabel('Z axis')
    ax.set_ylabel('X axis')
    ax.set_zlabel('Y axis')
    plt.legend( loc=1)
    plt.draw()
    plt.pause(1.0/40)


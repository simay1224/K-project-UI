# -*- coding: utf-8 -*-
"""
Created on Sun Jun 04 21:43:57 2017

@author: Dawnknight
"""

import cv2
import cPickle
import ctypes
from Mocam2Kinect import *
from Human_mod import *
from rawK2array import *
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime


#vid_src = 'Andy_data12151615.avi'
dst_path = './data/frame/'
#vid     = cv2.VideoCapture(vid_src)
#
#Width     = vid.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
#Height    = vid.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
#FPS       = vid.get(cv2.cv.CV_CAP_PROP_FPS) 
#Nframe    = vid.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)

#  Joints  initialize
kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)      
joints = ctypes.POINTER(PyKinectV2._Joint)
joints_capacity = ctypes.c_uint(PyKinectV2.JointType_Count)
joints_data_type = PyKinectV2._Joint * joints_capacity.value
joints = ctypes.cast(joints_data_type(), ctypes.POINTER(PyKinectV2._Joint))


Kinfile = 'D:/Project/K_project/data/Motion and Kinect raw data/20161216/pkl/Andy/Andy_data12151615_ex4.pkl'
Minfile = 'D:/Project/K_project/data/1216/Andy_2016-12-15 04.15.27 PM_FPS30_motion.pkl'
jidx = [0,1,2,3,4,5,6,8,9,10,20]


mdata = cPickle.load(file(Minfile,'r'))
kdata = rawK2ary(cPickle.load(file(Kinfile,'r')),jidx)
Len   = min(mdata['recon'].shape[1],kdata[0].shape[1])
pos_Kinect = Mocam2Kinect(mdata)
Pos_Unified = human_mod_Mocam(pos_Kinect,kdata[20])

Ccord = {}
for i in jidx:
    Ccord[i] = np.zeros((2,Len))


for frame_idx in range(Len):
    for j in jidx:
        joints[j].Position.x = Pos_Unified[j][0,frame_idx] 
        joints[j].Position.y = Pos_Unified[j][1,frame_idx]
        joints[j].Position.z = Pos_Unified[j][2,frame_idx]
    Jps = kinect.body_joints_to_color_space(joints)
    for jj in jidx:
        Ccord[jj][0,frame_idx] = Jps[jj].x
        Ccord[jj][0,frame_idx] = Jps[jj].y

count = 0

while count<len:
    
    ret, frame = vid.read()
    fname = dst_path+'frame'+repr(count).zfill(4)+'.jpg'
    
    cv2.imwrite(fname,frame)
    count += 1



    
    
vid.release()
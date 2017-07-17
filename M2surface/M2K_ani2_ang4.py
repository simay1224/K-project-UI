# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 15:59:06 2017

@author: medialab
"""

import cv2
import cPickle,h5py
import ctypes
import glob,os
from Mocam2Kinect import *
from Human_mod import *
from rawK2array import *
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import numpy as np

vid_src  = 'F:/avi/Angela_data20170306090752_ex4.avi'
name    = 'Angela_data0306090752_ex4'
dst_path = 'F:/frame/'+name+'/'

#src_path = 'D:/Project/K_project/data/'
src_path = 'F:/AllData_0327/' 

#raw kinect data
Kinfile   =  src_path + 'Motion and Kinect raw data/20170306/pkl/Angela/Angela_data0306090752_ex4.pkl'
#not unified Motion camera data
Minfile   = src_path + 'Motion and Kinect raw data/raw_MData/ex4/Angela_2017-03-06 09.09.00 AM_ex4_FPS30_motion.pkl' 
#raw data
Mraw      = src_path + 'Motion and Kinect raw data/Not_unified_Mdata/ex4/Angela_2017-03-06 09.09.00 AM_ex4_FPS30_motion.pkl'
Kraw      = src_path + 'Motion and Kinect raw data/3D_kinect_joint/ex4/Angela_data20170306090752_raw3D_ex4.pkl' 
# filtered data
Mpinfile  = src_path +'GPRresult/K2M_800/Angela_data20170306090752_unified_ex4.h5'


if not os.path.exists(dst_path):
    os.makedirs(dst_path)

def uni_vec(Body):
    
#    pdb.set_trace()
    j0  = Body[0:3 ,:]        
    j1  = Body[3:6 ,:]       
    j20 = Body[30: ,:]      
    j2  = Body[6:9 ,:]
    j3  = Body[9:12 ,:]
    
    vec01  = (j1 - j0 ) / np.sum((j1 - j0 )**2,axis = 0)**0.5
    vec201 = (j1 - j20 ) / np.sum((j1- j20)**2,axis = 0)**0.5
    vec202 = (j2 - j20) / np.sum((j2 - j20)**2,axis = 0)**0.5
    vec23  = (j3 - j2 ) / np.sum((j3 - j2 )**2,axis = 0)**0.5
    
    Len01  = np.mean(np.sum((j1 - j0 )**2,axis = 0)**0.5)
    Len201 = np.mean(np.sum((j1 - j20 )**2,axis = 0)**0.5)
    Len202 = np.mean(np.sum((j2 - j20)**2,axis = 0)**0.5)
    Len23  = np.mean(np.sum((j3 - j2 )**2,axis = 0)**0.5)

    return [vec01,vec201,vec202,vec23],[Len01,Len201,Len202,Len23]

def data2real(data,refK,joints,L):

    univec, Len  = uni_vec(data)

    Ccord = {}
    for i in jidx:
        Ccord[i] = np.zeros((2,L))

    for i in range(L):
        joints[20].Position.x = refK[0,i] 
        joints[20].Position.y = refK[1,i]            
        joints[20].Position.z = refK[2,i]
        joints[1].Position.x  = refK[0,i] + univec[1][0,i]*Len[1]
        joints[1].Position.y  = refK[1,i] + univec[1][1,i]*Len[1]
        joints[1].Position.z  = refK[2,i] + univec[1][2,i]*Len[1]
        joints[2].Position.x  = refK[0,i] + univec[2][0,i]*Len[2]
        joints[2].Position.y  = refK[1,i] + univec[2][1,i]*Len[2]
        joints[2].Position.z  = refK[2,i] + univec[2][2,i]*Len[2]
        joints[3].Position.x  = joints[2].Position.x + univec[3][0,i]*Len[3]
        joints[3].Position.y  = joints[2].Position.y + univec[3][1,i]*Len[3]
        joints[3].Position.z  = joints[2].Position.z + univec[3][2,i]*Len[3]   
        joints[0].Position.x  = joints[1].Position.x - univec[0][0,i]*Len[0]
        joints[0].Position.y  = joints[1].Position.y - univec[0][1,i]*Len[0]
        joints[0].Position.z  = joints[1].Position.z - univec[0][2,i]*Len[0] 

        Jps = kinect.body_joints_to_color_space(joints) 

        for jj in [0,1,2,3,20]:
            Ccord[jj][0,i] = Jps[jj].x
            Ccord[jj][1,i] = Jps[jj].y

    return Ccord

#  Joints  initialize
kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body|PyKinectV2.FrameSourceTypes_Depth|PyKinectV2.FrameSourceTypes_BodyIndex)       
joints = ctypes.POINTER(PyKinectV2._Joint)
joints_capacity = ctypes.c_uint(PyKinectV2.JointType_Count)
joints_data_type = PyKinectV2._Joint * joints_capacity.value
joints = ctypes.cast(joints_data_type(), ctypes.POINTER(PyKinectV2._Joint))


Mjoints = ctypes.POINTER(PyKinectV2._Joint)
Mjoints_capacity = ctypes.c_uint(PyKinectV2.JointType_Count)
Mjoints_data_type = PyKinectV2._Joint * Mjoints_capacity.value
Mjoints = ctypes.cast(Mjoints_data_type(), ctypes.POINTER(PyKinectV2._Joint))


jidx = [0,1,2,3,4,5,6,8,9,10,20]
jidx_draw = [4,5,6,8,9,10]

color = {}
color[4 ]     =(255,0,0)
color[5 ]     =(255,255,0)
color[6 ]     =(0,0,255)
color[8 ]     =(255,0,255)
color[9 ]     =(0,255,255)
color[10]     =(0,255,0)
color['bone'] = (50,200,50)



kdata   = rawK2ary(cPickle.load(file(Kinfile,'r')),jidx)
kdata2D = rawK2ary2D(cPickle.load(file(Kinfile,'r')),jidx)
mdata   = cPickle.load(file(Minfile,'r'))
rM      = cPickle.load(file(Mraw,'r'))
rK      = cPickle.load(file(Kraw,'r'))



if Mpinfile.split('/')[-1][-1] == 'l' :
    mpdata = cPickle.load(file(Mpinfile,'r'))
    Len   = min(mpdata['rcpos'].shape[1],kdata[0].shape[1])    
else:    
    mpdata = h5py.File(Mpinfile)['data'][:]
    Len   = min(mpdata.shape[1],kdata[0].shape[1])

# =================================


Mcord = data2real(rM,rK[30:,:],Mjoints,Len)
# =================================



Ccord = {}
for i in jidx:
    Ccord[i] = np.zeros((2,Len))
    
cv2.waitKey(50000) 

pos_Kinect = Mocam2Kinect(mdata) 


data = mpdata.reshape(-1,3,mpdata.shape[1])
Pos_Unified = human_mod_unified_Mocam(pos_Kinect,data,kdata[4],kdata[8],Len)


for frame_idx in range(Len):
    for j in jidx_draw:

        joints[j].Position.x = Pos_Unified[j][0,frame_idx] 
        joints[j].Position.y = Pos_Unified[j][1,frame_idx] 
        joints[j].Position.z = Pos_Unified[j][2,frame_idx] 

    Jps = kinect.body_joints_to_color_space(joints)    
    for jj in jidx_draw:
        Ccord[jj][0,frame_idx] = Jps[jj].x
        Ccord[jj][1,frame_idx] = Jps[jj].y


print Ccord[4]

vid      = cv2.VideoCapture(vid_src)
idx = 681

for i in range(idx+1):
    ret, img = vid.read()

    
for i in [4,6,8,9,10]:
    cv2.circle(img ,(int(Ccord[i][0,idx]),int(Ccord[i][1,idx])), 5, (0,0,255), -1)
    
cv2.circle(img ,(int(kdata2D[5][0,idx]),int(kdata2D[5][1,idx])+5), 5, (0,0,255), -1)   

for i in [0,1,2,3,20]:
    cv2.circle(img ,(int(Mcord[i][0,idx]),int(Mcord[i][1,idx])), 5, (0,0,255), -1)

 
for i in [0,1,2,3,4,5,6,8,9,10,20]:
    cv2.circle(img ,(int(kdata2D[i][0,idx]),int(kdata2D[i][1,idx])), 5, (0,255,0), -1)




cv2.line(img,(int(kdata2D[4][0,idx]),int(kdata2D[4][1,idx])),(int(kdata2D[5][0,idx]) ,int(kdata2D[5][1,idx])) ,(0,255,0),3) 
cv2.line(img,(int(kdata2D[5][0,idx]),int(kdata2D[5][1,idx])),(int(kdata2D[6][0,idx]) ,int(kdata2D[6][1,idx])) ,(0,255,0),3)
cv2.line(img,(int(kdata2D[9][0,idx]),int(kdata2D[9][1,idx])),(int(kdata2D[8][0,idx]) ,int(kdata2D[8][1,idx])) ,(0,255,0),3)
cv2.line(img,(int(kdata2D[9][0,idx]),int(kdata2D[9][1,idx])),(int(kdata2D[10][0,idx]),int(kdata2D[10][1,idx])),(0,255,0),3)

cv2.line(img,(int(Ccord[4][0,idx]),int(Ccord[4][1,idx])),(int(kdata2D[5][0,idx]) ,int(kdata2D[5][1,idx])+5) ,(0,0,255),3) 
cv2.line(img,(int(kdata2D[5][0,idx]),int(kdata2D[5][1,idx])+5),(int(Ccord[6][0,idx]) ,int(Ccord[6][1,idx])) ,(0,0,255),3)

cv2.line(img,(int(Ccord[9][0,idx]),int(Ccord[9][1,idx])),(int(Ccord[8][0,idx]) ,int(Ccord[8][1,idx])) ,(0,0,255),3)
cv2.line(img,(int(Ccord[9][0,idx]),int(Ccord[9][1,idx])),(int(Ccord[10][0,idx]),int(Ccord[10][1,idx])),(0,0,255),3)


#kinect taro:
    
cv2.line(img,(int(kdata2D[4][0,idx]),int(kdata2D[4][1,idx])),(int(kdata2D[20][0,idx]) ,int(kdata2D[20][1,idx])) ,(0,255,0),3) 
cv2.line(img,(int(kdata2D[8][0,idx]),int(kdata2D[8][1,idx])),(int(kdata2D[20][0,idx]) ,int(kdata2D[20][1,idx])) ,(0,255,0),3) 
cv2.line(img,(int(kdata2D[1][0,idx]),int(kdata2D[1][1,idx])),(int(kdata2D[20][0,idx]) ,int(kdata2D[20][1,idx])) ,(0,255,0),3) 
cv2.line(img,(int(kdata2D[2][0,idx]),int(kdata2D[2][1,idx])),(int(kdata2D[20][0,idx]) ,int(kdata2D[20][1,idx])) ,(0,255,0),3) 
cv2.line(img,(int(kdata2D[2][0,idx]),int(kdata2D[2][1,idx])),(int(kdata2D[3][0,idx])  ,int(kdata2D[3][1,idx])) ,(0,255,0),3) 
cv2.line(img,(int(kdata2D[1][0,idx]),int(kdata2D[1][1,idx])),(int(kdata2D[0][0,idx])  ,int(kdata2D[0][1,idx])) ,(0,255,0),3) 

#MoCAP taro:

cv2.line(img,(int(Ccord[4][0,idx]),int(Ccord[4][1,idx])),(int(Mcord[20][0,idx]) ,int(Mcord[20][1,idx])) ,(0,0,255),3) 
cv2.line(img,(int(Ccord[8][0,idx]),int(Ccord[8][1,idx])),(int(Mcord[20][0,idx]) ,int(Mcord[20][1,idx])) ,(0,0,255),3) 
cv2.line(img,(int(Mcord[1][0,idx]),int(Mcord[1][1,idx])),(int(Mcord[20][0,idx]) ,int(Mcord[20][1,idx])) ,(0,0,255),3) 
cv2.line(img,(int(Mcord[2][0,idx]),int(Mcord[2][1,idx])),(int(Mcord[20][0,idx]) ,int(Mcord[20][1,idx])) ,(0,0,255),3) 
cv2.line(img,(int(Mcord[2][0,idx]),int(Mcord[2][1,idx])),(int(Mcord[3][0,idx])  ,int(Mcord[3][1,idx]))  ,(0,0,255),3) 
cv2.line(img,(int(Mcord[1][0,idx]),int(Mcord[1][1,idx])),(int(Mcord[0][0,idx])  ,int(Mcord[0][1,idx]))  ,(0,0,255),3)     


  
img = cv2.resize(img, (0,0), fx=0.75, fy=0.75)
cv2.imshow('123',img)    
vid.release()
    
fname =dst_path + name+'_'+repr(idx).zfill(4)+'.jpg'

cv2.imwrite(fname,img)  

#FPS = 30
#Fsize = (960,540) #frame size
#fourcc = cv2.cv.FOURCC('X','V','I','D')
#video = cv2.VideoWriter(dst_path +name+'.avi', fourcc, FPS, Fsize)
#
#vid      = cv2.VideoCapture(vid_src)
#
#idx = 0
#
#while idx<Len:
#    print idx
#    ret, img = vid.read()
#    
#    for i in jidx_draw:
#        cv2.circle(img ,(int(Ccord[i][0,idx]),int(Ccord[i][1,idx])), 5, (0,0,255), -1)
#        cv2.circle(img ,(int(kdata2D[i][0,idx]),int(kdata2D[i][1,idx])), 5, (0,255,0), -1)
#
#
#
#    cv2.line(img,(int(kdata2D[4][0,idx]),int(kdata2D[4][1,idx])),(int(kdata2D[5][0,idx]) ,int(kdata2D[5][1,idx])) ,(0,255,0),3) 
#    cv2.line(img,(int(kdata2D[5][0,idx]),int(kdata2D[5][1,idx])),(int(kdata2D[6][0,idx]) ,int(kdata2D[6][1,idx])) ,(0,255,0),3)
#    cv2.line(img,(int(kdata2D[9][0,idx]),int(kdata2D[9][1,idx])),(int(kdata2D[8][0,idx]) ,int(kdata2D[8][1,idx])) ,(0,255,0),3)
#    cv2.line(img,(int(kdata2D[9][0,idx]),int(kdata2D[9][1,idx])),(int(kdata2D[10][0,idx]),int(kdata2D[10][1,idx])),(0,255,0),3)
#
#    cv2.line(img,(int(Ccord[4][0,idx]),int(Ccord[4][1,idx])),(int(Ccord[5][0,idx]) ,int(Ccord[5][1,idx])) ,(0,0,255),3) 
#    cv2.line(img,(int(Ccord[5][0,idx]),int(Ccord[5][1,idx])),(int(Ccord[6][0,idx]) ,int(Ccord[6][1,idx])) ,(0,0,255),3)
#    cv2.line(img,(int(Ccord[9][0,idx]),int(Ccord[9][1,idx])),(int(Ccord[8][0,idx]) ,int(Ccord[8][1,idx])) ,(0,0,255),3)
#    cv2.line(img,(int(Ccord[9][0,idx]),int(Ccord[9][1,idx])),(int(Ccord[10][0,idx]),int(Ccord[10][1,idx])),(0,0,255),3)
#  
#    fname =dst_path + name+'_'+repr(idx).zfill(4)+'.jpg'
#
#    img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
#    cv2.imwrite(fname,img)
#    
#    video.write(img)
#    idx +=1
#    
#vid.release()
#del video    
#
#
#data = {}
#data['K'] = kdata2D
#data['G'] = Ccord





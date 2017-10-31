# -*- coding: utf-8 -*-
"""
Created on Wed Dec 07 13:59:40 2016

@author: medialab
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pdb


# joint in kinect
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



factor = 5
Jlen = {}
Jlen['0203'] = 13.4  #head2neck
Jlen['2002'] = 8.3   #neck2spinshoulder
Jlen['0120'] = 15.4  #spinshoulder2spinmiddle
Jlen['0001'] = 32.5  #spinmiddle2spinbase
Jlen['2008'] = 16.65 #spinshoulder2Rshoulder
Jlen['0809'] = 33.2  #Rshoulder2Relbow
Jlen['0910'] = 27.1  #Relbow2Rwrist
Jlen['2004'] = 16.65 #spinshoulder2Lshoulder
Jlen['0405'] = 33.2  #Lshoulder2Lelbow
Jlen['0506'] = 27.1  #Lelbow2Lwrist

J = {}
oripos = np.array([80,100,0])

def uni_vec(Body,start,end):
    tmp = Body[start]-Body[end]
    vlen = sum(tmp**2)**.5
    vlen[vlen==0] = 10**-6
    return tmp/vlen

def uni_vec_pts(Body,start,end):
    tmp = np.array([Body[start].Position.x-Body[end].Position.x,\
                    Body[start].Position.y-Body[end].Position.y,\
                    Body[start].Position.z-Body[end].Position.z])
    
    vlen = sum(tmp**2)**.5
    if vlen == 0:
        vlen = 10**-6
    return tmp/vlen
    
def human_mod(Body): # for offline
    # Body : include all joints 3D position
    #pdb.set_trace()
    Vec0001 = uni_vec(Body, JointType_SpineBase    , JointType_SpineMid)
    Vec0120 = uni_vec(Body, JointType_SpineMid     , JointType_SpineShoulder)
    Vec2002 = uni_vec(Body, JointType_SpineShoulder, JointType_Neck)
    Vec0203 = uni_vec(Body, JointType_Neck         , JointType_Head)
    Vec2004 = uni_vec(Body, JointType_SpineShoulder, JointType_ShoulderLeft)
    Vec0405 = uni_vec(Body, JointType_ShoulderLeft , JointType_ElbowLeft)
    Vec0506 = uni_vec(Body, JointType_ElbowLeft    , JointType_WristLeft)
    Vec2008 = uni_vec(Body, JointType_SpineShoulder, JointType_ShoulderRight)
    Vec0809 = uni_vec(Body, JointType_ShoulderRight, JointType_ElbowRight)
    Vec0910 = uni_vec(Body, JointType_ElbowRight   , JointType_WristRight)
    
    
    J[JointType_SpineBase]     = np.tile(oripos,(Body[0].shape[1],1)).T
    J[JointType_SpineMid]      = J[JointType_SpineBase]    - Vec0001*Jlen['0001']*factor
    J[JointType_SpineShoulder] = J[JointType_SpineMid]     - Vec0120*Jlen['0120']*factor
    J[JointType_Neck]          = J[JointType_SpineShoulder]- Vec2002*Jlen['2002']*factor
    J[JointType_Head]          = J[JointType_Neck]         - Vec0203*Jlen['0203']*factor
    J[JointType_ShoulderLeft]  = J[JointType_SpineShoulder]- Vec2004*Jlen['2004']*factor
    J[JointType_ElbowLeft]     = J[JointType_ShoulderLeft] - Vec0405*Jlen['0405']*factor
    J[JointType_WristLeft]     = J[JointType_ElbowLeft]    - Vec0506*Jlen['0506']*factor
    J[JointType_ShoulderRight] = J[JointType_SpineShoulder]- Vec2008*Jlen['2008']*factor
    J[JointType_ElbowRight]    = J[JointType_ShoulderRight]- Vec0809*Jlen['0809']*factor
    J[JointType_WristRight]    = J[JointType_ElbowRight]   - Vec0910*Jlen['0910']*factor

    return J


def draw_human_mod(Joints):
    
    keys = Joints.keys()
    #nframe = Joints[keys[0]].shape[1]   #total number of the frames
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    for fno in range(50,726):
        plt.cla()
        x = []
        y = []
        z = []
    
        for i in  xrange(len(keys)):
            x.append(Joints[keys[i]][0][fno])
            y.append(Joints[keys[i]][1][fno])
            z.append(-1*Joints[keys[i]][2][fno])
    
        ax.scatter(z, x, y, c = 'red', s = 100)
        
        ax.set_xlim(-200,200)
        ax.set_ylim(-400,400)
        ax.set_zlim(100,500)
        ax.set_title(fno)
        
        plt.draw()
        plt.pause(1.0/120)
    

def human_mod_pts(Body):
    # Body : include all joints 3D position
    #pdb.set_trace()
    Vec0001 = uni_vec_pts(Body, JointType_SpineBase    , JointType_SpineMid)
    Vec0120 = uni_vec_pts(Body, JointType_SpineMid     , JointType_SpineShoulder)
    Vec2002 = uni_vec_pts(Body, JointType_SpineShoulder, JointType_Neck)
    Vec0203 = uni_vec_pts(Body, JointType_Neck         , JointType_Head)
    Vec2004 = uni_vec_pts(Body, JointType_SpineShoulder, JointType_ShoulderLeft)
    Vec0405 = uni_vec_pts(Body, JointType_ShoulderLeft , JointType_ElbowLeft)
    Vec0506 = uni_vec_pts(Body, JointType_ElbowLeft    , JointType_WristLeft)
    Vec2008 = uni_vec_pts(Body, JointType_SpineShoulder, JointType_ShoulderRight)
    Vec0809 = uni_vec_pts(Body, JointType_ShoulderRight, JointType_ElbowRight)
    Vec0910 = uni_vec_pts(Body, JointType_ElbowRight   , JointType_WristRight)
    
    
    J[JointType_SpineBase]     = oripos
    J[JointType_SpineMid]      = J[JointType_SpineBase]    - Vec0001*Jlen['0001']*factor
    J[JointType_SpineShoulder] = J[JointType_SpineMid]     - Vec0120*Jlen['0120']*factor
    J[JointType_Neck]          = J[JointType_SpineShoulder]- Vec2002*Jlen['2002']*factor
    J[JointType_Head]          = J[JointType_Neck]         - Vec0203*Jlen['0203']*factor
    J[JointType_ShoulderLeft]  = J[JointType_SpineShoulder]- Vec2004*Jlen['2004']*factor
    J[JointType_ElbowLeft]     = J[JointType_ShoulderLeft] - Vec0405*Jlen['0405']*factor
    J[JointType_WristLeft]     = J[JointType_ElbowLeft]    - Vec0506*Jlen['0506']*factor
    J[JointType_ShoulderRight] = J[JointType_SpineShoulder]- Vec2008*Jlen['2008']*factor
    J[JointType_ElbowRight]    = J[JointType_ShoulderRight]- Vec0809*Jlen['0809']*factor
    J[JointType_WristRight]    = J[JointType_ElbowRight]   - Vec0910*Jlen['0910']*factor

    return J


def draw_human_mod_pts(Joints,surface,keys):
    x=[]
    y=[]
    z=[]
    for i in  keys:
        x.append(Joints[i][0])
        y.append(Joints[i][1])
        z.append(Joints[i][2])
        
    surface.scatter(z, x, y, c = 'red', s = 100)    
    surface.set_xlim(-200,200)
    surface.set_ylim(-400,400)
    surface.set_zlim(100,500)
    plt.draw()
    plt.pause(1.0/120)

def human_mod_Mocam(Body,Kpos):
    # Body : include all joints 3D position
    #pdb.set_trace()
    #Kpos : kinect spinshoulder position
    
    oripos = Body[JointType_SpineShoulder]

    Vec00 = Body[JointType_SpineBase]     - oripos  
    Vec01 = Body[JointType_SpineMid]      - oripos
    Vec02 = Body[JointType_Neck]          - oripos
    Vec03 = Body[JointType_Head]          - oripos
    Vec04 = Body[JointType_ShoulderLeft]  - oripos
    Vec05 = Body[JointType_ElbowLeft]     - oripos
    Vec06 = Body[JointType_WristLeft]     - oripos   
    Vec08 = Body[JointType_ShoulderRight] - oripos
    Vec09 = Body[JointType_ElbowRight]    - oripos
    Vec10 = Body[JointType_WristRight]    - oripos
    Vec20 = Body[JointType_SpineShoulder] - oripos    
    
    Len = min(Vec00.shape[1],Kpos.shape[1])
    J[JointType_SpineBase]     = Vec00[:,:Len]  + Kpos[:,:Len]
    J[JointType_SpineMid]      = Vec01[:,:Len]  + Kpos[:,:Len]
    J[JointType_SpineShoulder] = Vec20[:,:Len]  + Kpos[:,:Len]
    J[JointType_Neck]          = Vec02[:,:Len]  + Kpos[:,:Len]
    J[JointType_Head]          = Vec03[:,:Len]  + Kpos[:,:Len]
    J[JointType_ShoulderLeft]  = Vec04[:,:Len]  + Kpos[:,:Len]
    J[JointType_ElbowLeft]     = Vec05[:,:Len]  + Kpos[:,:Len]
    J[JointType_WristLeft]     = Vec06[:,:Len]  + Kpos[:,:Len]
    J[JointType_ShoulderRight] = Vec08[:,:Len]  + Kpos[:,:Len]
    J[JointType_ElbowRight]    = Vec09[:,:Len]  + Kpos[:,:Len]
    J[JointType_WristRight]    = Vec10[:,:Len]  + Kpos[:,:Len]

    return J
       
    
#import cPickle 
#from Mocam2Kinect import *
#
#
#
#data = cPickle.load(file('../../output/pkl/mocapdata1128_array.pkl','r'))
#
#
#
#
#
#Kbody = Mocam2Kinect(data)
#
#J = human_mod(Kbody)
#draw_human_mod(J)    
    
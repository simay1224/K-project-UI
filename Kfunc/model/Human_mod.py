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
    
def human_mod(Body):
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
    

def human_mod_pts(Body,array= False, limb = True): #for online
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
    
#    if array :
#        for i in [0,1,2,3,4,5,6,8,9,10,20]:
#            if i == 0 :            
#                Jary = J[0]
#            else:
#                Jary = np.hstack([Jary, J[i]])
#        if limb:
#            return J,Jary[12:]
#        else:
#            return J,Jary
#                
#    else:       
#        return J
    if array :
        for iidx,i in enumerate([4,5,6,8,9,10,20]):
            if iidx == 0 :            
                Jary = J[i]
            else:
                Jary = np.vstack([Jary, J[i]])
        return J,Jary                
    else:       
        return J


def human_mod_pts2(Body,array= False, limb = True):
    # Body : include all joints 3D position
    pdb.set_trace()
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
    pdb.set_trace()
#    if array :
#        for i in [0,1,2,3,4,5,6,8,9,10,20]:
#            if i == 0 :            
#                Jary = J[0]
#            else:
#                Jary = np.hstack([Jary, J[i]])
#        if limb:
#            return J,Jary[12:]
#        else:
#            return J,Jary
#                
#    else:       
#        return J
    if array :
        for iidx,i in enumerate([4,5,6,8,9,10,20]):
            if iidx == 0 :            
                Jary = J[i]
            else:
                Jary = np.vstack([Jary, J[i]])
        return J,Jary                
    else:       
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

def reconJ2joints(joint, recon_body):
    #LSpos : ShoulderLeft position


    ori_body = {}
    for i in [4,5,6,8,9,10]:
        ori_body[i] = np.array([joint[i].Position.x,joint[i].Position.y,joint[i].Position.z])

    Vec45 = (recon_body[1,:]  - recon_body[0,:])/np.sum((recon_body[1,:]-recon_body[0,:])**2,0)**0.5
    Vec56 = (recon_body[2,:]  - recon_body[1,:])/np.sum((recon_body[2,:]-recon_body[1,:])**2,0)**0.5 
#    Vec48 = (recon_body[3,:]  - recon_body[0,:])/np.sum((recon_body[3,:]-recon_body[0,:])**2,0)**0.5 
    Vec89 = (recon_body[4,:]  - recon_body[3,:])/np.sum((recon_body[4,:]-recon_body[3,:])**2,0)**0.5 
    Vec90 = (recon_body[5,:]  - recon_body[4,:])/np.sum((recon_body[5,:]-recon_body[4,:])**2,0)**0.5  
    
    
    Len45 = np.mean(np.sum((ori_body[5 ]  - ori_body[4])**2,axis = 0)**0.5)  
    Len56 = np.mean(np.sum((ori_body[6 ]  - ori_body[5])**2,axis = 0)**0.5)
#    Len48 = np.mean(np.sum((ori_body[8 ]  - ori_body[4])**2,axis = 0)**0.5) 
    Len89 = np.mean(np.sum((ori_body[9 ]  - ori_body[8])**2,axis = 0)**0.5)
    Len90 = np.mean(np.sum((ori_body[10]  - ori_body[9])**2,axis = 0)**0.5)  
    

    J = {}
#    LSpos = ori_body[4]
#    RSpos = ori_body[8]
    
    J[JointType_ShoulderLeft] = ori_body[4]
    J[JointType_ElbowLeft]    = Vec45*Len45 + ori_body[4]
    J[JointType_WristLeft]    = Vec56*Len56 + J[JointType_ElbowLeft]
    
    J[JointType_ShoulderRight] = ori_body[8]
#    J[JointType_ShoulderRight] = Vec48*Len48 + J[JointType_ShoulderLeft]
    J[JointType_ElbowRight]    = Vec89*Len89 + ori_body[8]
    J[JointType_WristRight]    = Vec90*Len90 + J[JointType_ElbowRight]

    return J

#    joint[JointType_ElbowLeft].Position.x     = (Vec45*Len45 + ori_body[4])[0]
#    joint[JointType_ElbowLeft].Position.y     = (Vec45*Len45 + ori_body[4])[1]
#    joint[JointType_ElbowLeft].Position.z     = (Vec45*Len45 + ori_body[4])[2]
#    
#    joint[JointType_WristLeft].Position.x     = (Vec56*Len56 + joint[JointType_ElbowLeft])[0]
#    joint[JointType_WristLeft].Position.y     = (Vec56*Len56 + joint[JointType_ElbowLeft])[1]
#    joint[JointType_WristLeft].Position.z     = (Vec56*Len56 + joint[JointType_ElbowLeft])[2]
#    joint[JointType_ElbowRight].Position.x    = (Vec89*Len89 + ori_body[8])[0]
#    joint[JointType_ElbowRight].Position.y    = (Vec89*Len89 + ori_body[8])[1]
#    joint[JointType_ElbowRight].Position.z    = (Vec89*Len89 + ori_body[8])[2]
#    joint[JointType_WristRight] .Position.x   = (Vec90*Len90 + joint[JointType_ElbowRight])[0]
#    joint[JointType_WristRight] .Position.y   = (Vec90*Len90 + joint[JointType_ElbowRight])[1]
#    joint[JointType_WristRight] .Position.z   = (Vec90*Len90 + joint[JointType_ElbowRight])[2]
#    
#    
#    return joint
  
     
    
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
    
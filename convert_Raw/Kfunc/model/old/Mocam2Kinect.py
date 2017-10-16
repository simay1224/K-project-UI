# -*- coding: utf-8 -*-
"""
Created on Tue Dec 06 15:50:02 2016

@author: Dawnknight
"""
import numpy as np

Qing_LFArm_2  = 0
Qing_LFArm_1  = 1
Qing_LThumb1_1= 2 
Qing_RUArm_1  = 3
Qing_RUArm_2  = 4
Qing_LHand_2  = 5
Qing_RFArm_1  = 6
Qing_Hip_4    = 7
Qing_RFArm_2  = 8 
Qing_Hip_2    = 9
Qing_Hip_3    = 10
Qing_RThumb1_1= 11 
Qing_LPinky1_1= 12
Qing_LHand_1  = 13
Qing_Hip_1    = 14
Qing_Head_2   = 15
Qing_Head_3   = 16
Qing_Head_1   = 17
Qing_RHand_2  = 18
Qing_RHand_1  = 19
Qing_Chest_4  = 20
Qing_Chest_1  = 21
Qing_Chest_2  = 22
Qing_Chest_3  = 23
Qing_LShoulder_2= 24 
Qing_LShoulder_1= 25
Qing_RIndex1_1  = 26
Qing_LUArm_2    = 27
Qing_LUArm_1    = 28
Qing_RShoulder_1= 29 
Qing_RShoulder_2= 30
Qing_RPinky1_1  = 31
Qing_LIndex1_1  = 32
x=0
y=1
z=2

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


def Mocam2Kinect(pts):
     
     body = pts['rcpos']
     result = {}
     
     head_x = body[Qing_Head_1*3+x]
     head_y = (body[Qing_Head_1*3+y]-body[Qing_Chest_1*3+y])*0.585+body[Qing_Chest_1*3+y]
     head_z = (body[Qing_Chest_1*3+z]+body[Qing_Chest_4*3+z])/2
     head = np.vstack([head_x,head_y,head_z])
        
     neck_x = body[Qing_Chest_1*3+x]
     neck_y = (body[Qing_Head_1*3+y]-body[Qing_Chest_1*3+y])*0.255+body[Qing_Chest_1*3+y]
     neck_z = (body[Qing_Chest_1*3+z]+body[Qing_Chest_4*3+z])/2
     neck = np.vstack([neck_x,neck_y,neck_z])
     
     spinshoulder_x = (body[Qing_LShoulder_2*3+x]+body[Qing_RShoulder_2*3+x])/2
     spinshoulder_y = (body[Qing_LShoulder_2*3+y]+body[Qing_RShoulder_2*3+y])/2
     spinshoulder_z = (body[Qing_Chest_1*3+z]+body[Qing_Chest_4*3+z])/2
     spinshoulder = np.vstack([spinshoulder_x,spinshoulder_y,spinshoulder_z])
     
     spinmid_x = body[Qing_Chest_4*3+x]
     spinmid_y = body[Qing_Chest_4*3+y]
     spinmid_z = (body[Qing_Chest_1*3+z]+body[Qing_Chest_4*3+z])/2
     spinmid = np.vstack([spinmid_x,spinmid_y,spinmid_z])
     
     spinbase_x = (body[Qing_Hip_1*3+x]+body[Qing_Hip_2*3+x])/2
     spinbase_y = (body[Qing_Hip_1*3+y]+body[Qing_Hip_2*3+y])/2
     spinbase_z = (body[Qing_Chest_1*3+z]+body[Qing_Chest_4*3+z])/2
     spinbase = np.vstack([spinbase_x,spinbase_y,spinbase_z])
     
     Lshoulder_x = body[Qing_LShoulder_2*3+x]
     Lshoulder_y = body[Qing_LShoulder_2*3+y]
     Lshoulder_z = (body[Qing_Chest_1*3+z]+body[Qing_Chest_4*3+z])/2
     Lshoulder = np.vstack([Lshoulder_x,Lshoulder_y,Lshoulder_z])
     
     Rshoulder_x = body[Qing_RShoulder_2*3+x]
     Rshoulder_y = body[Qing_RShoulder_2*3+y]
     Rshoulder_z = (body[Qing_Chest_1*3+z]+body[Qing_Chest_4*3+z])/2     
     Rshoulder = np.vstack([Rshoulder_x,Rshoulder_y,Rshoulder_z])
     
     Lelbow_x = body[Qing_LUArm_1*3+x]
     Lelbow_y = body[Qing_LUArm_2*3+y]
     Lelbow_z = body[Qing_LUArm_1*3+z]
     Lelbow = np.vstack([Lelbow_x,Lelbow_y,Lelbow_z])
     
     Relbow_x = body[Qing_RUArm_1*3+x]
     Relbow_y = body[Qing_RUArm_2*3+y]
     Relbow_z = body[Qing_RUArm_1*3+z]
     Relbow = np.vstack([Relbow_x,Relbow_y,Relbow_z])
     
     Lwrist_x = body[Qing_LFArm_1*3+x]
     Lwrist_y = body[Qing_LFArm_1*3+y]
     Lwrist_z = body[Qing_LFArm_1*3+z]
     Lwrist = np.vstack([Lwrist_x,Lwrist_y,Lwrist_z])
     
     Rwrist_x = body[Qing_RFArm_1*3+x]
     Rwrist_y = body[Qing_RFArm_1*3+y]
     Rwrist_z = body[Qing_RFArm_1*3+z]     
     Rwrist = np.vstack([Rwrist_x,Rwrist_y,Rwrist_z])
     
     
     result[JointType_Head]          = head
     result[JointType_Neck]          = neck
     result[JointType_SpineShoulder] = spinshoulder
     result[JointType_SpineMid]      = spinmid
     result[JointType_SpineBase]     = spinbase
     result[JointType_ShoulderLeft]  = Lshoulder
     result[JointType_ShoulderRight] = Rshoulder
     result[JointType_ElbowLeft]     = Lelbow
     result[JointType_ElbowRight]    = Relbow
     result[JointType_WristLeft]     = Lwrist
     result[JointType_WristRight]    = Rwrist

     return result
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
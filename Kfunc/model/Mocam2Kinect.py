# -*- coding: utf-8 -*-
"""
Created on Tue Dec 06 15:50:02 2016

@author: Dawnknight
"""
import numpy as np

#LFArm_2  = 0
#LFArm_1  = 1
#LThumb1_1= 2 
#RUArm_1  = 3
#RUArm_2  = 4
#LHand_2  = 5
#RFArm_1  = 6
#Hip_4    = 7
#RFArm_2  = 8 
#Hip_2    = 9
#Hip_3    = 10
#RThumb1_1= 11 
#LPinky1_1= 12
#LHand_1  = 13
#Hip_1    = 14
#Head_2   = 15
#Head_3   = 16
#Head_1   = 17
#RHand_2  = 18
#RHand_1  = 19
#Chest_4  = 20
#Chest_1  = 21
#Chest_2  = 22
#Chest_3  = 23
#LShoulder_2= 24 
#LShoulder_1= 25
#RIndex1_1  = 26
#LUArm_2    = 27
#LUArm_1    = 28
#RShoulder_1= 29 
#RShoulder_2= 30
#RPinky1_1  = 31
#LIndex1_1  = 32

LShoulder_1   = 0
RUArm_2       = 1
LShoulder_2   = 2
LUArm_1       = 3
RUArm_1       = 4
LUArm_2       = 5
Head_3        = 6
Head_2        = 7
Head_1        = 8
RShoulder_2   = 9
Chest_4       = 10
Chest_3       = 11
Chest_2       = 12
Chest_1       = 13
Hip_1         = 14
Hip_3         = 15
Hip_2         = 16
Hip_4         = 17
RShoulder_1   = 18
LHand_3       = 19
LHand_2       = 20
LHand_1       = 21
RHand_1       = 22
RHand_3       = 23
RHand_2       = 24

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


def Mocam2Kinect25(pts):
     
     body = pts['rcpos']
     result = {}
     
     head_x = body[Head_1*3+x]
     head_y = (body[Head_1*3+y]-body[Chest_1*3+y])*0.585+body[Chest_1*3+y]
     head_z = (body[Chest_1*3+z]+body[Chest_4*3+z])/2
     head = np.vstack([head_x,head_y,head_z])
        
     neck_x = body[Chest_1*3+x]
     neck_y = (body[Head_1*3+y]-body[Chest_1*3+y])*0.255+body[Chest_1*3+y]
     neck_z = (body[Chest_1*3+z]+body[Chest_4*3+z])/2
     neck = np.vstack([neck_x,neck_y,neck_z])
     
     spinshoulder_x = (body[LShoulder_2*3+x]+body[RShoulder_2*3+x])/2
     spinshoulder_y = (body[LShoulder_2*3+y]+body[RShoulder_2*3+y])/2
     spinshoulder_z = (body[Chest_1*3+z]+body[Chest_4*3+z])/2
     spinshoulder = np.vstack([spinshoulder_x,spinshoulder_y,spinshoulder_z])
     
     spinmid_x = body[Chest_4*3+x]
     spinmid_y = body[Chest_4*3+y]
     spinmid_z = (body[Chest_1*3+z]+body[Chest_4*3+z])/2
     spinmid = np.vstack([spinmid_x,spinmid_y,spinmid_z])
     
     spinbase_x = (body[Hip_1*3+x]+body[Hip_2*3+x])/2
     spinbase_y = (body[Hip_1*3+y]+body[Hip_2*3+y])/2
     spinbase_z = (body[Chest_1*3+z]+body[Chest_4*3+z])/2
     spinbase = np.vstack([spinbase_x,spinbase_y,spinbase_z])
     
     Lshoulder_x = body[LShoulder_2*3+x]
     Lshoulder_y = body[LShoulder_2*3+y]
     Lshoulder_z = (body[Chest_1*3+z]+body[Chest_4*3+z])/2
     Lshoulder = np.vstack([Lshoulder_x,Lshoulder_y,Lshoulder_z])
     
     Rshoulder_x = body[RShoulder_2*3+x]
     Rshoulder_y = body[RShoulder_2*3+y]
     Rshoulder_z = (body[Chest_1*3+z]+body[Chest_4*3+z])/2     
     Rshoulder = np.vstack([Rshoulder_x,Rshoulder_y,Rshoulder_z])
     
     Lelbow_x = body[LUArm_1*3+x]*2-body[LUArm_2*3+x]
     Lelbow_y = body[LUArm_2*3+y]
     Lelbow_z = body[LUArm_1*3+z]*2-body[LUArm_2*3+z]
     Lelbow = np.vstack([Lelbow_x,Lelbow_y,Lelbow_z])
     
     Relbow_x = body[RUArm_1*3+x]*2-body[RUArm_2*3+x]
     Relbow_y = body[RUArm_2*3+y]
     Relbow_z = body[RUArm_1*3+z]*2-body[RUArm_2*3+z]
     Relbow = np.vstack([Relbow_x,Relbow_y,Relbow_z])
     
     
     
     
     
#     Lwrist_x = body[LHand_2*3+x]
#     Lwrist_y = body[LHand_2*3+y]
#     Lwrist_z = body[LHand_2*3+z]
     Lwrist_x = (body[LHand_3*3+x]+body[LHand_2*3+x])/2
     Lwrist_y = (body[LHand_3*3+y]+body[LHand_2*3+y])/2
     Lwrist_z = (body[LHand_3*3+z]+body[LHand_2*3+z])/2
     Lwrist = np.vstack([Lwrist_x,Lwrist_y,Lwrist_z])
     
     Rwrist_x = (body[RHand_3*3+x]+body[RHand_2*3+x])/2
     Rwrist_y = (body[RHand_3*3+y]+body[RHand_2*3+y])/2
     Rwrist_z = (body[RHand_3*3+z]+body[RHand_2*3+z])/2
#     Rwrist_x = body[RHand_2*3+x]
#     Rwrist_y = body[RHand_2*3+y]
#     Rwrist_z = body[RHand_2*3+z]
#    
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
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
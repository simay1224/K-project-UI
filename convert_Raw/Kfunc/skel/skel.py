# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 09:50:08 2016

@author: medialab
"""
import pygame
import numpy as np

# values for enumeration '_JointType'
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
JointType_Count = 25

# values for enumeration '_TrackingState'
TrackingState_NotTracked = 0
TrackingState_Inferred = 1
TrackingState_Tracked = 2

def draw_body_bone(joints, jointPoints, color, joint0, joint1,surface,linewidth=8):
    joint0State = joints[joint0].TrackingState;
    joint1State = joints[joint1].TrackingState;

    # both joints are not tracked
    if (joint0State ==  TrackingState_NotTracked) or (joint1State ==  TrackingState_NotTracked): 
        return

    # both joints are not *really* tracked
    if (joint0State ==  TrackingState_Inferred) and (joint1State ==  TrackingState_Inferred):
        return

    # ok, at least one is good 
    start = (jointPoints[joint0].x, jointPoints[joint0].y)
    end = (jointPoints[joint1].x, jointPoints[joint1].y)

    try:
        pygame.draw.line(surface, color, start, end ,linewidth)
        #lines(Surface, color, closed, pointlist, width=1)
    except: # need to catch it due to possible invalid positions (with inf)
        pass

def draw_body( joints, jointPoints, color , surface,linewidth = 8):
    # Torso
    #pdb.set_trace()
    
    draw_body_bone(joints, jointPoints, color,  JointType_Head,  JointType_Neck,surface,linewidth);
    draw_body_bone(joints, jointPoints, color,  JointType_Neck,  JointType_SpineShoulder,surface,linewidth);
    draw_body_bone(joints, jointPoints, color,  JointType_SpineShoulder,  JointType_SpineMid,surface,linewidth);
    draw_body_bone(joints, jointPoints, color,  JointType_SpineMid,  JointType_SpineBase,surface,linewidth);
    draw_body_bone(joints, jointPoints, color,  JointType_SpineShoulder,  JointType_ShoulderRight,surface,linewidth);
    draw_body_bone(joints, jointPoints, color,  JointType_SpineShoulder,  JointType_ShoulderLeft,surface,linewidth);
    draw_body_bone(joints, jointPoints, color,  JointType_SpineBase,  JointType_HipRight,surface,linewidth);
    draw_body_bone(joints, jointPoints, color,  JointType_SpineBase,  JointType_HipLeft,surface,linewidth);
    
    # Right Arm    
    draw_body_bone(joints, jointPoints, color,  JointType_ShoulderRight,  JointType_ElbowRight,surface,linewidth);
    draw_body_bone(joints, jointPoints, color,  JointType_ElbowRight,  JointType_WristRight,surface,linewidth);
    #draw_body_bone(joints, jointPoints, color,  JointType_WristRight,  JointType_HandRight,surface,linewidth);


    # Left Arm
    draw_body_bone(joints, jointPoints, color,  JointType_ShoulderLeft,  JointType_ElbowLeft,surface,linewidth);
    draw_body_bone(joints, jointPoints, color,  JointType_ElbowLeft,  JointType_WristLeft,surface,linewidth);
    #draw_body_bone(joints, jointPoints, color,  JointType_WristLeft,  JointType_HandLeft,surface,linewidth);

def draw_Rel_joints(jointPoints,Rel,surface):
    for i in Rel.keys():
        try:
            pygame.draw.circle(surface, (255,0,0), (int(jointPoints[i].x), int(jointPoints[i].y)), np.int((1-Rel[i])*30))    
        except:
            pass
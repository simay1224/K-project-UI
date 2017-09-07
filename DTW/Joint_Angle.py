# -*- coding: utf-8 -*-
"""
Created on Thu Sep 07 14:34:19 2017

@author: medialab
"""

import numpy as np
import pdb

def Joint_Angle(Joints,Type = 'All'):
    if len(Joints) == 33: # Raw data
        Joints = Joints[12:]
    elif len(Joints) != 21: 
        print('Error !! Please check the data ... ')
        return 'Err'
    
    
    #  === assign each joint ===   
    SL = Joints[ 0: 3]
    EL = Joints[ 3: 6]
    WL = Joints[ 6: 9]
    SR = Joints[ 9:12]
    ER = Joints[12:15]
    WR = Joints[15:18]
    SP = Joints[18:21] 
    
    # === get the vectors ===
    
    SL_vec = SL - SP
    EL_vec = EL - SL
    WL_vec = WL - EL
    SR_vec = SR - SP
    ER_vec = ER - SR
    WR_vec = WR - ER
    Y_vec  = np.array([0,-1,0])
    
    SL_r   = np.sqrt(SL_vec[0]**2+SL_vec[1]**2+SL_vec[2]**2)
    EL_r   = np.sqrt(EL_vec[0]**2+EL_vec[1]**2+EL_vec[2]**2)
    WL_r   = np.sqrt(WL_vec[0]**2+WL_vec[1]**2+WL_vec[2]**2)
    SR_r   = np.sqrt(SR_vec[0]**2+SR_vec[1]**2+SR_vec[2]**2)
    ER_r   = np.sqrt(ER_vec[0]**2+ER_vec[1]**2+ER_vec[2]**2)
    WR_r   = np.sqrt(WR_vec[0]**2+WR_vec[1]**2+WR_vec[2]**2)
    Y_r    = np.sqrt( Y_vec[0]**2+ Y_vec[1]**2+ Y_vec[2]**2)
    
    # === get the angle ===
    Angle = {}
    if (Type == 'All') | (Type =='S') | (Type == 'LS'):
#        pdb.set_trace()
        SL_angle_XZ = np.pi- np.arccos(np.sum(SL_vec * EL_vec)/(SL_r*EL_r))
        SL_angle_Y  = np.arccos(np.sum(EL_vec * Y_vec)/(Y_r*EL_r))
        Angle['LS'] = [np.rad2deg(SL_angle_XZ),np.rad2deg(SL_angle_Y)]
    if (Type == 'All') | (Type == 'S') | (Type == 'RS'):
        SR_angle_XZ = np.pi- np.arccos(np.sum(SR_vec * ER_vec)/(SR_r*ER_r))
        SR_angle_Y  = np.arccos(np.sum(ER_vec * Y_vec)/(Y_r*ER_r)) 
        Angle['RS'] = [np.rad2deg(SR_angle_XZ),np.rad2deg(SR_angle_Y)]
    if (Type == 'All') | (Type == 'E') | (Type == 'LE'):           
        EL_angle_XZ = np.pi- np.arccos(np.sum(EL_vec * WL_vec)/(EL_r*WL_r))
        EL_angle_Y  = np.arccos(np.sum(WL_vec * Y_vec)/(WL_r*Y_r))
        Angle['LE'] = [np.rad2deg(EL_angle_XZ),np.rad2deg(EL_angle_Y)]
    if (Type == 'All') | (Type == 'E') | (Type == 'RE'):        
        ER_angle_XZ = np.pi- np.arccos(np.sum(ER_vec * WR_vec)/(ER_r*WR_r))
        ER_angle_Y  = np.arccos(np.sum(WR_vec * Y_vec)/(WR_r*Y_r))
        Angle['RE'] = [np.rad2deg(ER_angle_XZ),np.rad2deg(ER_angle_Y)]
    
    return Angle
    
    
    
    
    
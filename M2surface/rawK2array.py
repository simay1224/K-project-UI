# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 15:49:36 2017

@author: medialab
"""
import numpy as np

def rawK2ary(rawK,jidx): #kinect raw data 2 np array
    #rawK : original kinect data
    #jidx : joints index which are interested
   
    joints = {}
    for i in jidx:
        joints[i] = np.zeros([3,len(rawK)])
    
    for i in xrange(len(rawK)):
        for idx,j in enumerate(jidx):
            joints[j][0,i] = rawK[i]['joints'][j].Position.x
            joints[j][1,i] = rawK[i]['joints'][j].Position.y
            joints[j][2,i] = rawK[i]['joints'][j].Position.z  

    return joints  


def rawK2ary2D(rawK,jidx): #kinect raw data 2 np array
    #rawK : original kinect data
    #jidx : joints index which are interested
   
    joints = {}
    for i in jidx:
        joints[i] = np.zeros([2,len(rawK)])
    
    for i in xrange(len(rawK)):
        for idx,j in enumerate(jidx):
            joints[j][0,i] = rawK[i]['jointspts'][j].x
            joints[j][1,i] = rawK[i]['jointspts'][j].y
              
    return joints      

 


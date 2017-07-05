# -*- coding: utf-8 -*-
"""
Created on Wed Jul 05 01:14:40 2017

@author: Dawnknight
"""

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import numpy as np
import cPickle
import glob,os

#Alldata = cPickle.load(file('I:/AllData_0327/raw data/20161216/pkl/Andy/Andy_data12151615_ex4.pkl','rb'))

Alldata = cPickle.load(file('D:/Project/K_project/data/Motion and Kinect raw data/20161216/pkl/Andy/Andy_data12151615_ex4.pkl','rb'))
jidx = [0,1,2,3,4,5,6,8,9,10,20]



#for idx,data in enumerate(Alldata):
#    tmp = []
#    for i in jidx:
##        tmp.append(data['joints'][i].Position.x) 
##        tmp.append(data['joints'][i].Position.y) 
##        tmp.append(data['joints'][i].Position.z) 
#        tmp.append(np.array([data['joints'][i].Position.x,data['joints'][i].Position.y,data['joints'][i].Position.z])) 
#    if idx == 0:
#        Joints = np.array(tmp) 
#    else:
#        Joints = np.vstack([Joints,np.array(tmp)])
#        
#Joints = Joints.T 

        


       
#th = 0.03
#fsize = 1
#
#Rel = {}
#for i in jidx:
#    Rel[i] = []
#    
#for fidx in range(125,130):#Joints.shape[1]):#
#        for idx,j in enumerate(jidx):
#            J = Joints[3*idx:3*idx+3,:].T.flatten()[:3*fidx+3]
#            if len(J)>fsize*3:
#                for k in xrange(fsize):
#                    dj   = np.array([J[-(3*k+1)],J[-(3*k+2)],J[-(3*k+3)]])- np.array([J[-(3*k+4)],J[-(3*k+5)],J[-(3*k+6)]])
#                    dj_1 = np.array([J[-(3*k+4)],J[-(3*k+5)],J[-(3*k+6)]])- np.array([J[-(3*k+7)],J[-(3*k+8)],J[-(3*k+9)]])
#                    dj_2 = np.array([J[-(3*k+1)],J[-(3*k+2)],J[-(3*k+3)]])- np.array([J[-(3*k+7)],J[-(3*k+8)],J[-(3*k+9)]])
#                    n_dj = np.linalg.norm(dj)
#                    n_dj_1 = np.linalg.norm(dj_1)
#                    n_dj_2 = np.linalg.norm(dj_2)
#            
#    #                r = -99
#                    if (n_dj_2 < th):
#                        r = 1
#                    else:
#                        if (n_dj > th):
#                            r = max(1-4*(n_dj-th)/th,0)
#                        else:
#                            r = 1
#    
#                Rel[j].append(r)
#                            
#            else:
#                Rel[j].append(1)
    



i=6
Joints = []
for idx,data in enumerate(Alldata):
    Joints.append(np.array([data['joints'][i].Position.x,data['joints'][i].Position.y,data['joints'][i].Position.z])) 

th = 0.03
fsize = 3

Rel = []
#for i in jidx:
#    Rel[i] = []


for fidx in range(127,128):
#        for idx,j in enumerate(jidx):
    J = Joints[:fidx+1]
    r=1
    if len(J)>=fsize:
        for k in xrange(1):
            dj   = J[-(k+1)]-J[-(k+2)]            
            dj_1 = J[-(k+2)]-J[-(k+3)]
            dj_2 = J[-(k+1)]-J[-(k+3)]
            n_dj = np.linalg.norm(dj)
            n_dj_1 = np.linalg.norm(dj_1)
            n_dj_2 = np.linalg.norm(dj_2)
    
#                r = -99
            if (n_dj_2 < th):
                r = 1
            else:
                if (n_dj > th):
                    r = max(1-4*(n_dj-th)/th,0)
                else:
                    r = 1

        Rel.append(r)
                    
    else:
        Rel.append(1)


    print Rel
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 04 15:45:19 2017

@author: user
"""

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import numpy as np
import cPickle

#def rel_behav(J,th = 0.03,theta_r=135,theta_f = 90): #behavior term
#    #J : 3D joint position in [...,f-4,f-3,f-2,f-1,f]
#    #th   : threshold (uint: m)
#
#    theta = 0
#    if len(J)>5:
#        for k in xrange(3):
#            dj   = J[-(k+1)]-J[-(k+2)]
#            dj_1 = J[-(k+2)]-J[-(k+3)]
#            n_dj = np.linalg.norm(dj)
#            n_dj_1 = np.linalg.norm(dj_1)
#            if (n_dj > th) & (n_dj_1 > th):
#                theta += np.arccos(sum([dj[i]*dj_1[i] for i in xrange(3)])/n_dj/n_dj_1)/np.pi*180
#    return 1-max(min(theta/3,theta_r)-theta_f,0)/(theta_r-theta_f)


Alldata = cPickle.load(file('I:/AllData_0327/raw data/20161216/pkl/Andy/Andy_data12151615_ex4.pkl','rb'))
jidx = [0,1,2,3,4,5,6,8,9,10,20]

#Joints = np.array([])

for idx,data in enumerate(Alldata):
    tmp = []
    for i in jidx:
        tmp.append(data['joints'][i].Position.x) 
        tmp.append(data['joints'][i].Position.y) 
        tmp.append(data['joints'][i].Position.z) 
    if idx == 0:
        Joints = np.array(tmp) 
    else:
        Joints = np.vstack([Joints,np.array(tmp)])
        
Joints = Joints.T        

cPickle.dump(Joints,file('dic.pkl','wb'))


J = Joints[12:15,:].T.flatten()[:9]
th = 0.03
theta_r=135
theta_f = 90
    #J : 3D joint position in [...,f-4,f-3,f-2,f-1,f]
                                
    #th   : threshold (uint: m)

theta = 0
if len(J)>3*3:
    for k in xrange(1):
        dj   = np.array([J[-(3*k+1)],J[-(3*k+2)],J[-(3*k+3)]])- np.array([J[-(3*k+4)],J[-(3*k+5)],J[-(3*k+6)]])
        dj_1 = np.array([J[-(3*k+4)],J[-(3*k+5)],J[-(3*k+6)]])- np.array([J[-(3*k+7)],J[-(3*k+8)],J[-(3*k+9)]])
        n_dj = np.linalg.norm(dj)
        n_dj_1 = np.linalg.norm(dj_1)
        if (n_dj > th) & (n_dj_1 > th):
            theta += np.arccos(sum([dj[i]*dj_1[i] for i in xrange(3)])/n_dj/n_dj_1)/np.pi*180
                
            
#    return 1-max(min(theta/3,theta_r)-theta_f,0)/(theta_r-theta_f)








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


#Alldata = cPickle.load(file('I:/AllData_0327/raw data/20161216/pkl/Andy/Andy_data12151615_ex4.pkl','rb'))
#jidx = [0,1,2,3,4,5,6,8,9,10,20]
#
##Joints = np.array([])
#
#for idx,data in enumerate(Alldata):
#    tmp = []
#    for i in jidx:
#        tmp.append(data['joints'][i].Position.x) 
#        tmp.append(data['joints'][i].Position.y) 
#        tmp.append(data['joints'][i].Position.z) 
#    if idx == 0:
#        Joints = np.array(tmp) 
#    else:
#        Joints = np.vstack([Joints,np.array(tmp)])
#        
#Joints = Joints.T        
#
#cPickle.dump(Joints,file('dic.pkl','wb'))

Joints = cPickle.load(file('dic.pkl','rb'))

for idx in range(140,145):
    J = Joints[18:21,:].T.flatten()[:3*idx+3]
    th = 0.03
    theta_r=135
    theta_f = 90
        #J : 3D joint position in [...,f-4,f-3,f-2,f-1,f]
                                    
        #th   : threshold (uint: m)
    
    theta = 0
#    if len(J)>3*3:
    for k in xrange(1):
        dj   = np.array([J[-(3*k+1)],J[-(3*k+2)],J[-(3*k+3)]])- np.array([J[-(3*k+4)],J[-(3*k+5)],J[-(3*k+6)]])
        dj_1 = np.array([J[-(3*k+4)],J[-(3*k+5)],J[-(3*k+6)]])- np.array([J[-(3*k+7)],J[-(3*k+8)],J[-(3*k+9)]])
        dj_2 = np.array([J[-(3*k+1)],J[-(3*k+2)],J[-(3*k+3)]])- np.array([J[-(3*k+7)],J[-(3*k+8)],J[-(3*k+9)]])
        n_dj = np.linalg.norm(dj)
        n_dj_1 = np.linalg.norm(dj_1)
        n_dj_2 = np.linalg.norm(dj_2)
        print '\n==============\n'
        print idx
        print '\n'
#        print(repr(idx)+'-'+repr(idx-1)+': '+repr(dj))
#        print(repr(idx-1)+'-'+repr(idx-2)+': '+repr(dj_1))
#        print(repr(idx)+'-'+repr(idx-2)+': '+repr(dj_2))
        print '\nlen btw '+repr(idx)+' and '+repr(idx-1)+' is :'+ repr(n_dj)
#        print 'len btw '+repr(idx-1)+' and '+repr(idx-2)+' is :'+ repr(n_dj_1)      
        print 'len btw '+repr(idx)+' and '+repr(idx-2)+' is :'+ repr(n_dj_2)  
#        print '\nAngle btw '+repr(idx)+' and '+repr(idx-1)+' is :'+repr(np.arccos(sum(dj*dj_1)/n_dj/n_dj_1)/np.pi*180)
#        print 'Angle btw '+repr(idx)+' and '+repr(idx-2)+' is :'+repr(np.arccos(sum(dj*dj_2)/n_dj/n_dj_2)/np.pi*180)
#        
#

#        if (n_dj > th):
#            r = 1-4*(n_dj-th)/th
#            if (n_dj_1 > th):
#                if status == 1:
#                    if (n_dj_2 < th):
#                        r = 1
#                    
#                   status = 0 
#                else:
#                    status =1
#            else:
#                status=0            
#        else:
#            r = 1
#        r = -99
        if (n_dj_2 < th):
            r = 1
        else:
            if (n_dj > th):
                r = max(1-4*(n_dj-th)/th,0)
            else:
                r = 1
        print r

            

#            theta += np.arccos(sum(dj*dj_1)/n_dj/n_dj_1)/np.pi*180
                
                
                    
#    print  1-max(min(theta,theta_r)-theta_f,0)/(theta_r-theta_f)           









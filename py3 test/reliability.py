# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 14:41:16 2016

@author: medialab
"""

import numpy as np
import copy,pdb

#kinematic segment length (unit:cm)
kinseg = {}
kinseg[0] = 13.4  #head2neck
kinseg[1] = 8.3   #neck2spins
kinseg[2] = 15.4  #spins2spinm
kinseg[3] = 32.5  #spinm2spinb
kinseg[4] = 16.65 #spins2shlder
kinseg[5] = 33.2  #shlder2elbow
kinseg[6]  =27.1  #elbow2wrist

# target joint order
Tjo = [0,1,2,3,4,5,6,8,9,10,20]

# gaussian filter
a = np.arange(6)
sigma = 1
gw = 1/(2*np.pi)**2/sigma*np.exp(-0.5*a**2/sigma**2) 
gw = gw*(1/sum(gw))
#initail reliability 
rel = {}

jord = [0,1,2,3,4,5,6,8,9,10,20]
for i in jord:
    rel[i]=0

def rel_behav(J,th = 0.03,theta_r=135,theta_f = 90): #behavior term
    #J : 3D joint position in [...,f-4,f-3,f-2,f-1,f]
    #th   : threshold (uint: m)

    theta = 0
    if len(J)>5:
        for k in range(3):
            dj   = J[-(k+1)]-J[-(k+2)]
            dj_1 = J[-(k+2)]-J[-(k+3)]
            n_dj = np.linalg.norm(dj)
            n_dj_1 = np.linalg.norm(dj_1)
            if (n_dj > th) & (n_dj_1 > th):
                theta += np.arccos(sum([dj[i]*dj_1[i] for i in range(3)])/n_dj/n_dj_1)/np.pi*180
    return 1-max(min(theta/3,theta_r)-theta_f,0)/(theta_r-theta_f)

        
def rel_kin(joints): # kinematic term    
    order1 = [9,5,20,1,2]
    order2 = [8,6,4,20,3]     # joints' order   
    order3 = [10,4,8,0,20]
    refer1 = [5,6,4,2,0]      # kinseg's order
    refer2 = [6,5,4,3,1]  

    segrel = {}
    result = []
    cnts = np.zeros(21)
    for i in Tjo:
        segrel[i]=0

    for i in range(len(order1)):
        A = np.array([joints[order1[i]].Position.x,joints[order1[i]].Position.y,joints[order1[i]].Position.z])
        B = np.array([joints[order2[i]].Position.x,joints[order2[i]].Position.y,joints[order2[i]].Position.z])
        C = np.array([joints[order3[i]].Position.x,joints[order3[i]].Position.y,joints[order3[i]].Position.z])
          
        tmp = min(np.abs(np.linalg.norm(A-B)*100 - kinseg[refer1[i]])/kinseg[refer1[i]],1)
        segrel[order1[i]] += tmp
        segrel[order2[i]] += tmp
        

        tmp = min(np.abs(np.linalg.norm(A-C)*100 - kinseg[refer2[i]])/kinseg[refer2[i]],1)
        segrel[order1[i]] += tmp
        segrel[order3[i]] += tmp

        cnts[order1[i]]+=2
        cnts[order2[i]]+=1
        cnts[order3[i]]+=1

    for i in Tjo:
        result.append( 1-(segrel[i]/cnts[i]))

    return result

    
def rel_trk(joints): # tracking term
    trkrel = []
    for i in Tjo:
        if joints[i].TrackingState == 2:
            trkrel.append(1.0)
        else:
            trkrel.append(0.0)

    return trkrel
    
def rel_rate(Rb,Rk,Rt,order,flen = 6):
    Relary = np.zeros(21)
    if (len(Rb[0])>=flen) & (len(Rk[0])>=flen) & (len(Rt[0])>=flen) :
        Rel = copy.copy(rel)
        
        if order == jord :
            for j in order:
                for i in range(flen):
                    Rel[j] += gw[i]*min(Rb[j][-(i+1)],Rk[j][-(i+1)],Rt[j][-(i+1)])
                    Relary[j] += gw[i]*min(Rb[j][-(i+1)],Rk[j][-(i+1)],Rt[j][-(i+1)])
        else:
            print ('joints order not match !!')
    else:
        return rel,[]
    return Rel,Relary
#def rel_rate(Rb,Rk,Rt,order,flen = 6):
#    if (len(Rb[0])>=flen) &  (len(Rt[0])>=flen) :
#        Rel = copy.copy(rel)
#        
#        if order == jord :
#            for j in order:
#                for i in range(flen):
#                    Rel[j] += gw[i]*min(Rb[j][-(i+1)],Rt[j][-(i+1)])
#        else:
#            print 'joints order not match !!'
#    else:
#        return rel
#    return Rel
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 21:54:22 2017

@author: Dawnknight
"""

import cPickle
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.spatial.distance import euclidean

from fastdtw import fastdtw
def dist3D(Va,Vb):
    dist = []
    for i in xrange(Va.shape[1]):
        dist.append(np.linalg.norm(Va[:,i]-Vb[:,i]))
    return dist

def findplane(p1,p2,p3):
    V1 = p3-p1
    V2 = p2-p1
    cp = np.cross(V1, V2)
    a, b, c = cp
    d = np.dot(cp, p3)
    return [a,b,c,d]
    
    
    
data = cPickle.load(file('./data/Motion and Kinect/Unified_MData/Andy_2016-12-15 04.15.27 PM_FPS30_motion_unified_ex4.pkl'))
kdata = cPickle.load(file('./data/Motion and Kinect/Unified_KData/Andy_12151615_Kinect_unified_ex4.pkl'))
Rel = cPickle.load(file('./data/Rel.pkl'))
Relth = 0.5

LS = 4
LE = 5
LW = 6
RS = 8
RE = 9 
RW = 10


for i in [0,1,2,3,4,5,6,8,9,10,20]:
    if i == 0:
        joints = data[i]
        kjoints = kdata[i]
    else:
        joints = np.vstack([joints,data[i]])
        kjoints = np.vstack([kjoints,kdata[i]])


KLS = kjoints[12:15,:]
KRS = kjoints[21:24,:]           
KLE = kjoints[15:18,:]
KRE = kjoints[24:27,:]        
KLW = kjoints[18:21,:]
KRW = kjoints[27:30,:]
MLS = joints[12:15,:]
MRS = joints[21:24,:]           
MLE = joints[15:18,:]
MRE = joints[24:27,:]        
MLW = joints[18:21,:]
MRW = joints[27:30,:]


VLSE = KLS - KLE
VRSE = KRS - KRE
VLEW = KLE - KLW
VREW = KRE - KRW
#distance, path  = fastdtw(joints[15:18,:].T,kjoints[15:18,:].T,dist=euclidean)
#distance, path  = fastdtw(joints[18:21,:].T,kjoints[18:21,:].T,dist=euclidean)

dist = dist3D(KLS,KLE)
 
findplane(KLE[:,i],KLS[:,i],MLE[:,i])
      
for i in xrange(kjoints.shape[1]):
    if Rel[LE,i]>Relth:
       VLSE[:,i]/sum(VLSE[:,i]**2)**.5 
        









   
import cPickle
import matplotlib.pyplot as plt

kjts = cPickle.load(file('./data/kjts.pkl'))
Rel = cPickle.load(file('./data/Rel.pkl'))


fig = plt.figure()
ax1 = plt.subplot(2,1,1)
plt.plot(range(954),(kjts[17,:]-2)*100)

ax1 = plt.subplot(2,1,2)
plt.plot(range(954),Rel[5,:])

plt.show()    
    
    
         
            
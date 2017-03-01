# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 00:51:34 2017

@author: Dawnknight
"""

import cPickle,copy
import numpy as np
from sklearn import decomposition,linear_model
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import os, glob,pdb
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn import datasets
from sklearn.decomposition import PCA
import pdb

data = cPickle.load(file('./data/Motion and Kinect/Unified_MData/Andy_2016-12-15 04.15.27 PM_FPS30_motion_unified_ex4.pkl'))
kdata = cPickle.load(file('./data/Motion and Kinect/Unified_KData/Andy_12151615_Kinect_unified_ex4.pkl'))
rel = cPickle.load(file('./data/Rel.pkl'))
relth = 0.7


for i in [0,1,2,3,4,5,6,8,9,10,20]:
    if i == 0:
        joints = data[i]
        kjoints = kdata[i]
    else:
        joints = np.vstack([joints,data[i]])
        kjoints = np.vstack([kjoints,kdata[i]])
        
#normalized

Njoints = (joints*2-joints.max()-joints.min())/(joints.max()-joints.min())
mv = (np.roll(joints,-1,axis = 1)-joints)[:,:-1]
#    mvjoints = np.vstack([joints[:,1:],mv])
Nmv = (mv*2-mv.max()-mv.min())/(mv.max()-mv.min())
Nmvj = np.vstack([Njoints[:,1:],Nmv])
pca = PCA(n_components=3)
X_reduced = pca.fit_transform(Nmvj.T)    


Nkjoints = (kjoints*2-joints.max()-joints.min())/(joints.max()-joints.min())
kmv = (np.roll(kjoints,-1,axis = 1)-kjoints)[:,:-1]
#    mvjoints = np.vstack([joints[:,1:],mv])
Nkmv = (kmv*2-mv.max()-mv.min())/(mv.max()-mv.min())
Nkmvj = np.vstack([Nkjoints[:,1:],Nkmv])

repidx = np.tile(np.arange(rel.shape[0]).repeat(3),2)
Rel  =  rel[repidx][:,1:]  #increase the size of rel
newkdata = copy.copy(Nkmvj)

for i in xrange(1,Rel.shape[1]):
    idx = np.where(Rel[:,i]>relth)[0]
    if len(idx) != 66:
        #pdb.set_trace()
        kX_reduced = pca.transform(Nkmvj[:,i].reshape(1,-1))
        newkdata[:,i] = pca.inverse_transform(kX_reduced) 
        newkdata[idx,i] = Nkmvj[idx,i]


NewKJ = (newkdata[:33,:]*(joints.max()-joints.min())+(joints.max()+joints.min()))/2




fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


ax.set_xlabel('Z axis')
ax.set_ylabel('X axis')
ax.set_zlabel('Y axis')
    
for frame_no in xrange(953):
    plt.cla()
    
    xs = []
    ys = []
    zs = []
    kxs = []
    kys = []
    kzs = []
    nkxs = []
    nkys = []
    nkzs = []    

    for joint_idx in  data.keys() :
        xs.append(data[joint_idx][0][frame_no])
        ys.append(data[joint_idx][1][frame_no])
        zs.append(data[joint_idx][2][frame_no])
        kxs.append(kdata[joint_idx][0][frame_no])
        kys.append(kdata[joint_idx][1][frame_no])
        kzs.append(kdata[joint_idx][2][frame_no])
    
    nkxs = NewKJ[0::3,frame_no]
    nkys = NewKJ[1::3,frame_no]
    nkzs = NewKJ[2::3,frame_no]


    ax.scatter(nkzs, nkxs, nkys, c = 'blue', s = 100,label='Recover K Joints') 
    ax.scatter(kzs, kxs, kys, c = 'red', s = 100,label='Kinect Joints')    
    ax.scatter(zs, xs, ys,c = 'green',s = 50,alpha=.4,label='MoCam Joints')
    
    ax.set_xlim(-300,300)
    ax.set_ylim(-200,400)
    ax.set_zlim(50,600)
    ax.set_title(str(frame_no))
    plt.legend( loc=1)
    ax.set_xlabel('Z axis')
    ax.set_ylabel('X axis')
    ax.set_zlabel('Y axis')    
    plt.draw()
    plt.pause(1.0/120)

    
    
    
    
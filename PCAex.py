# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 13:33:31 2017

@author: medialab
"""


import cPickle 
import numpy as np
from sklearn import decomposition,linear_model
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import os, glob,pdb
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn import datasets
from sklearn.decomposition import PCA

infile  = './data/Motion and Kinect/Unified_MData/Andy_2016-12-15 04.15.27 PM_FPS30_motion_unified_ex4.pkl'
kinfile = './data/Motion and Kinect/Unified_KData/Andy_12151615_Kinect_unified_ex4.pkl'
#oinfile  = './data/Motion and Kinect/Unified_MData/qingyuan_2016-12-15 03.37.16 PM_FPS30_motion_unified_ex4.pkl'
#kinfile = './data/Motion and Kinect/Unified_KData/Qingyuan_12151536_Kinect_unified_ex4.pkl'


rel = cPickle.load(file('./data/Rel.pkl'))
relth = 0.7

color = ['b','g','r','c','m','y','k']
          

data = cPickle.load(file(infile,'rb'))
kdata = cPickle.load(file(kinfile,'rb'))
odata = cPickle.load(file(oinfile,'rb'))


for i in [0,1,2,3,4,5,6,8,9,10,20]:
    if i == 0:
        joints = data[i]
        kjoints = kdata[i]
        ojoints = odata[i]
    else:
        joints = np.vstack([joints,data[i]])
        kjoints = np.vstack([kjoints,kdata[i]])
        ojoints = np.vstack([ojoints,odata[i]])

Njoints = (joints*2-joints.max()-joints.min())/(joints.max()-joints.min())
Nkjoints = (kjoints*2-joints.max()-joints.min())/(joints.max()-joints.min())
mv = (np.roll(joints,-1,axis = 1)-joints)[:,:-1]
mvk = (np.roll(kjoints,-1,axis = 1)-kjoints)[:,:-1]
#    mvjoints = np.vstack([joints[:,1:],mv])
Nmv = (mv*2-mv.max()-mv.min())/(mv.max()-mv.min())
Nmvk = (mvk*2-mv.max()-mv.min())/(mv.max()-mv.min())
Nmvj = np.vstack([Njoints[:,1:],Nmv])
Nmvjk = np.vstack([Nkjoints[:,1:],Nmvk])         
  

#Nojoints = (ojoints*2-joints.max()-joints.min())/(joints.max()-joints.min())
#
#omv = (np.roll(ojoints,-1,axis = 1)-ojoints)[:,:-1]
#
#
#Nomv = (omv*2-mv.max()-mv.min())/(mv.max()-mv.min())
#
#Nomvj = np.vstack([Nojoints[:,1:],Nomv])



#      
#idx = []
#for i in xrange(rel.shape[1]):
#    if len(np.where(rel[:,i]<relth)[0])>0:
#        idx.append(i)

        
        
fig = plt.figure(2, figsize=(8, 6))
ax = Axes3D(fig, elev=-150, azim=110)
pca = PCA(n_components=3)
X_reduced = pca.fit_transform(Nmvj.T)
kX_reduced = pca.transform(Nmvjk.T)
oX_reduced = pca.transform(Nomvj.T)

ax.scatter(X_reduced[:, 0], X_reduced[:, 1], X_reduced[:, 2], color ='blue',label='motion cam' )
ax.scatter(kX_reduced[:, 0], kX_reduced[:, 1], kX_reduced[:, 2], color ='red',label='Kinect' )
#ax.scatter(oX_reduced[:, 0], oX_reduced[:, 1], oX_reduced[:, 2], color ='blue',label='Mo' )
#ax.scatter(kX_reduced[idx, 0], kX_reduced[idx, 1], kX_reduced[idx, 2], color ='green',label='Kinect' )


ax.set_title("First three PCA directions")
ax.set_xlabel("1st eigenvector")
ax.set_ylabel("2nd eigenvector")
ax.set_zlabel("3rd eigenvector")
plt.legend( loc=1)
plt.draw()
#    plt.show()
plt.pause(1.0/120)


'''



path = './data/Motion and Kinect/Unified_MData/'
dataname = ['Andy_2016-12-15 04.15.27 PM_FPS30_motion_unified_ex4.pkl',\
          #'Dawn_2016-12-16 02.26.38 PM_FPS30_motion_unified_ex4.pkl',\
          #'Dawn_2016-12-16 02.27.51 PM_FPS30_motion_unified_ex4.pkl',\
          #'Dawn_2016-12-16 02.48.46 PM_FPS30_motion_unified_ex4.pkl',\
          #'Nata_2016-12-16 03.08.50 PM_FPS30_motion_unified_ex4.pkl',\
          #'Nata_2016-12-16 03.09.35 PM_FPS30_motion_unified_ex4.pkl',\
          #'Nata_2016-12-16 03.18.15 PM_FPS30_motion_unified_ex4.pkl',\
          #'qingyuan_2016-12-15 03.37.16 PM_FPS30_motion_unified_ex4.pkl'\
          ]
color = ['b','g','r','c','m','y','k','b']

fig = plt.figure(1, figsize=(8, 6))
ax = Axes3D(fig, elev=-150, azim=110)    

      
for idx,infile in enumerate(dataname):
    data = cPickle.load(file(path+infile,'rb'))
    
    for i in [0,1,2,3,4,5,6,8,9,10,20]:
        if i == 0:
            joints = data[i]
    
        else:
            joints = np.vstack([joints,data[i]])
    
            
    #normalized
    
    Njoints = (joints*2-joints.max()-joints.min())/(joints.max()-joints.min())
    mv = (np.roll(joints,-1,axis = 1)-joints)[:,:-1]
#    mvjoints = np.vstack([joints[:,1:],mv])
    Nmv = (mv*2-mv.max()-mv.min())/(mv.max()-mv.min())
    Nmvj = np.vstack([Njoints[:,1:],Nmv])

    pca = PCA(n_components=3)        
    X_reduced = pca.fit_transform(Nmvj.T)
#    ax.scatter(X_reduced[:, 0], X_reduced[:, 1], X_reduced[:, 2], color ='red',label=infile[0:4]+'_pos' )


    
#    pca = PCA(n_components=3) 
#    X_reduced = pca.fit_transform(mvjoints.T)
#    b= pca.components_[0]
    
#
    
#    if idx ==0:
#        pca = PCA(n_components=3)
#        X_reduced = pca.fit_transform(joints.T)
#    else:
#        X_reduced = pca.transform(Nmvj.T)

        
        
      
    
    ax.scatter(X_reduced[:, 0], X_reduced[:, 1], X_reduced[:, 2], color =color[idx],label=infile[0:4] )

    plt.draw()

ax.set_title("First three PCA directions")
ax.set_xlabel("1st eigenvector")
ax.set_ylabel("2nd eigenvector")
ax.set_zlabel("3rd eigenvector")
plt.legend( loc=1)
plt.draw()
#    plt.show()
plt.pause(1.0/120)
'''

#for i in xrange(0,X_reduced.shape[0],5):
#
#    print i
#    ax.scatter(X_reduced[i, 0], X_reduced[i, 1], X_reduced[i, 2], cmap=plt.cm.Paired)
#    
#    ax.set_title("First three PCA directions")
#    ax.set_xlabel("1st eigenvector")
#    ax.w_xaxis.set_ticklabels([])
#    ax.set_ylabel("2nd eigenvector")
#    ax.w_yaxis.set_ticklabels([])
#    ax.set_zlabel("3rd eigenvector")
#    ax.w_zaxis.set_ticklabels([])
#    plt.draw()
##    plt.show()
#    plt.pause(1.0/120)
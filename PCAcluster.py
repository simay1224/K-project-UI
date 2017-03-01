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
from sklearn.cluster import KMeans
from hmmlearn import hmm


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

fig = plt.figure(2, figsize=(8, 6))
ax = Axes3D(fig, elev=-150, azim=110)    

      
for idx,infile in enumerate(dataname):
    data = cPickle.load(file(path+infile,'rb'))
    
    for i in [0,1,2,3,4,5,6,8,9,10,20]:
        if i == 0:
            joints = data[i]
    
        else:
            joints = np.vstack([joints,data[i]])
    
    mv = (np.roll(joints,-1,axis = 1)-joints)[:,:-1]          
     
    mvjts = np.vstack([joints[:,1:],mv])
       
    pca = PCA(n_components=3)        
    X_reduced = pca.fit_transform(joints.T)
    
    kmeans = KMeans(n_clusters=5, random_state=0).fit(mv.T)
    stablemv = np.where(kmeans.labels_ == kmeans.labels_[0])[0]
    skmeans = KMeans(n_clusters=3, random_state=0).fit(X_reduced[stablemv,:])
    #labels = kmeans.labels_
    
    
    index = [0,1,2]
    index.pop(skmeans.labels_[0])
    for cnt,i in enumerate(index):
        kmeans.labels_[stablemv[np.where(skmeans.labels_==i)[0]]] = max(kmeans.labels_)+1 
    
    
    model = hmm.GaussianHMM(n_components=5).fit(mv.T)
    Z =model.predict(mv.T)    

    #ax.scatter(X_reduced[:, 0], X_reduced[:, 1], X_reduced[:, 2], color ='red',label=infile[0:4]+'_pos' )
    
for i in xrange(1,961):
    ax.scatter(X_reduced[i, 0], X_reduced[i, 1], X_reduced[i, 2], color = color[kmeans.labels_[i]])#color[Z[i]])
    plt.draw()
    
ax.set_title("KM after PCA results (mv)")
ax.set_xlabel("1st eigenvector")
ax.set_ylabel("2nd eigenvector")
ax.set_zlabel("3rd eigenvector")
plt.legend( loc=1)
plt.draw()
#    plt.show()
plt.pause(1.0/120)


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

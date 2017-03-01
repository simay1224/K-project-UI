# -*- coding: utf-8 -*-
"""
Created on Fri Dec 02 10:10:04 2016

@author: liuqi
"""

import pickle as pk
import numpy as np
import cmath
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def rotate(x,y,theta):
    Rmtx = np.array(((np.cos(theta),-np.sin(theta)),(np.sin(theta),np.cos(theta))))
    return np.dot(Rmtx,np.array([x,y]))

def rotateary(x,y,theta):
    X = np.cos(theta)*x-np.sin(theta)*y
    Y = np.sin(theta)*x+np.cos(theta)*y

    return X,Y   
    
    

f = open('mocapdata1128_array.pkl','rb')
data_all = pk.load(f).values()

keys = data_all[0]
num_labels = len(keys)  # total number of the labels

#data_orig   = {}  # dictionary
#data_interp = {}   
# for one frame x,y,z of 33 markers
xs = []
ys = []
zs = []

frame_no = 200 # the no. of frame
for i in  xrange( num_labels ):
#    temp = []
#    temp = [data_all[2][i*3],data_all[2][i*3+1],data_all[2][i*3+2]]
#    data_interp.update({keys[i] : temp})
    xs.append(data_all[3][i*3][frame_no])
    ys.append(data_all[3][i*3+1][frame_no])
    zs.append(data_all[3][i*3+2][frame_no])


r,theta = cmath.polar(complex(data_all[3][20*3][frame_no]-data_all[2][21*3][frame_no],data_all[2][20*3+2][frame_no]-data_all[2][21*3+2][frame_no]))
    

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

labels = range(1,34)
X,Z = rotateary(np.array(xs),np.array(zs),-np.pi/2-theta)

#ax.scatter(Z, X, ys)
ax.scatter(zs, xs, ys)

#for i in xrange( num_labels ):
#    
#    #ax.text(zs[i],xs[i],ys[i],keys[i][5::])
#    
#    XX,ZZ = rotate(xs[i],zs[i],-np.pi/2-theta)
#    
#    
#    ax.text(ZZ,XX,ys[i],keys[i][5::])
#    #ax.text(xs[i],zs[i],ys[i],i
#    
#ax.set_xlim(-1,0.5)    
#ax.set_ylim(-0.5,1.5)
#
#ax.set_zlim(1,1.9)
#ax.set_xlabel('Z axis')
#ax.set_ylabel('X axis')
#ax.set_zlabel('Y axis')
plt.show()


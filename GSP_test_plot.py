# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 02:23:34 2017

@author: Dawnknight
"""

import h5py
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm

f = h5py.File('./data/GSP/diff/Err_opt_cor_0.5_adj_0_relb_F_mean.h5')

All_x   = f['all_x'][:]
All_y   = f['all_y'][:]
All_z   = f['all_z'][:]

unrel_x = f['unrel_x'][:]
unrel_y = f['unrel_y'][:]
unrel_z = f['unrel_z'][:]

N = 500
scale = 0.001

#case 1 :

plt.figure(1)
ax1 = plt.subplot(3,1,1)
ax1.set_title('x')
plt.plot(np.arange(1,N)*scale,unrel_x[1:],color = 'blue')
ax2 = plt.subplot(3,1,2)
ax2.set_title('y')
plt.plot(np.arange(1,N)*scale,unrel_y[1:],color = 'blue')
ax3 = plt.subplot(3,1,3)
ax3.set_title('z')
plt.plot(np.arange(1,N)*scale+1,unrel_z[1:],color = 'blue')
plt.show()



plt.figure(2)
ax1 = plt.subplot(3,1,1)
ax1.set_title('x')
plt.plot(np.arange(1,N)*scale,All_x[1:],color = 'blue')
ax2 = plt.subplot(3,1,2)
ax2.set_title('y')
plt.plot(np.arange(1,N)*scale,All_y[1:],color = 'blue')
ax3 = plt.subplot(3,1,3)
ax3.set_title('z')
plt.plot(np.arange(1,N)*scale+1,All_z[1:],color = 'blue')
plt.show()



#case 2 :
    
X =  np.tile(np.arange(1,N,10)*scale,[10,1])
Y =  np.tile(np.arange(1,N,10)*scale,[10,1]).T
for i in range(10):

#    Z_all = All[i,:,:] 
#    Z_unrel = unrel[:,:,i]   

    fig = plt.figure(i+1)
    ax1 = fig.add_subplot(111, projection='3d')
    
    ax1.plot_wireframe(X, Y, All[0,:,:], rstride=1, cstride=1,color = 'blue',label ='gamma_x : 0.01') 
#    ax1.plot_wireframe(X, Y, All[3,:,:], rstride=1, cstride=1,color = 'red' ,label ='gamma_x : 0.31') 
#    ax1.plot_wireframe(X, Y, All[6,:,:], rstride=1, cstride=1,color = 'green',label ='gamma_x : 0.61')
#    ax1.plot_wireframe(X, Y, All[9,:,:], rstride=1, cstride=1,color = 'black',label ='gamma_x : 0.91')
    
#    ax1.plot_surface(X, Y, Z_all ,rstride=1, cstride=1, alpha=0.3)
#    cset = ax1.contour(X, Y, Z_all, zdir='z', offset=46.2, cmap=cm.coolwarm)
#    cset = ax1.contour(X, Y, Z_all, zdir='x', offset=-0.1, cmap=cm.coolwarm)
#    cset = ax1.contour(X, Y, Z_all, zdir='y', offset=1.1, cmap=cm.coolwarm)
    ax1.set_title("gamma_x = "+repr(0.01+0.1*i)+' all joint error') 
    ax1.set_xlabel('gamma_y')
    ax1.set_ylabel('gamma_z')
    ax1.set_zlabel('err: pixel per joint')    
    plt.legend( loc=1)
    plt.show()

    fig = plt.figure(i+11)
    ax2 = fig.add_subplot(111, projection='3d')
    ax2.plot_wireframe(X, Y, unrel[:,:,i] , rstride=1, cstride=1)
    ax2.set_title("gamma_x = "+repr(0.01+0.1*i)+' unreliable joint error')
    plt.show()





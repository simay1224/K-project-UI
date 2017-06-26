# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 02:23:34 2017

@author: Dawnknight
"""

import h5py
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d

f = h5py.File('Err_opt_cor_0.5_adj_0_relb_T.h5')

All   = f['all'][:]
unrel = f['unrel'][:]
N = 200
scale = 0.01

#case 1 :

plt.figure(1)
plt.title('x,y,z share same gamma')

plt.plot(np.arange(N)*scale,unrel,color = 'blue',label = 'unrel joints')
plt.plot(np.arange(N)*scale,All  ,color = 'red',label = 'rall joints')

plt.legend( loc=1)

plt.show()


#case 2 :
    
X =  np.tile(np.arange(N-1)*scale,[N-1,1])
Y =  np.tile(np.arange(N-1)*scale,[N-1,1]).T
Z_all = All 
Z_unrel = unrel   

fig = plt.figure(1)
ax1 = fig.add_subplot(111, projection='3d')
ax1.plot_wireframe(X, Y, Z_all, rstride=10, cstride=10)


fig = plt.figure(2)
ax1 = fig.add_subplot(111, projection='3d')
ax1.plot_wireframe(X, Y, Z_unrel, rstride=10, cstride=10)






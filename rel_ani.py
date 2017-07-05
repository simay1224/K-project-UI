# -*- coding: utf-8 -*-
"""
Created on Wed Jul 05 17:02:28 2017

@author: medialab
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 04 22:51:01 2017

@author: Dawnknight
"""
import cPickle,h5py
import numpy as np
import glob,os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


mpdata_all = cPickle.load(file('dic.pkl'))

fig = plt.figure(1)
ax = fig.add_subplot(111, projection='3d')


ax.set_xlabel('Z axis')
ax.set_ylabel('X axis')
ax.set_zlabel('Y axis')
    
idx = 129


prx = mpdata_all[0::3,idx-1]
pry = mpdata_all[1::3,idx-1]
prz = mpdata_all[2::3,idx-1]

x   = mpdata_all[0::3,idx]
y   = mpdata_all[1::3,idx]
z   = mpdata_all[2::3,idx]

prx2 = mpdata_all[0::3,idx-2]
pry2 = mpdata_all[1::3,idx-2]
prz2 = mpdata_all[2::3,idx-2]

prx3 = mpdata_all[0::3,idx-3]
pry3 = mpdata_all[1::3,idx-3]
prz3 = mpdata_all[2::3,idx-3]

ax.scatter(prz3, prx3, pry3,c = 'black',s =50,alpha=.4,label=repr(idx-3))
ax.scatter(prz2, prx2, pry2,c = 'green',s =50,alpha=.4,label=repr(idx-2))
ax.scatter(prz, prx, pry,   c = 'blue' ,s =50,alpha=.4,label=repr(idx-1))
ax.scatter(z, x, y,         c = 'red'  ,s =50,alpha=.4,label=repr(idx))


plt.legend( loc=1)
plt.show()

    
    
    
    
    
    
    
    
    
    
    
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 07 13:46:44 2017

@author: medialab
"""

import cPickle,pdb
import numpy as np

import matplotlib.pyplot as plt
from Joint_Angle import *

#src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'
src_path  = 'D:/Project/K_project/data/unified data array/Unified_MData/'
gt_src   = 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'

data      = cPickle.load(file(gt_src,'rb'))[12:,:].T
AngleLS_XZ   = []
AngleLS_Y    = []
AngleLE_XZ   = []
AngleLE_Y    = []



for i in xrange(data.shape[0]):
    
    Angle = Joint_Angle(data[i,:],'All')
    AngleLS_XZ.append(Angle['RS'][0])
    AngleLS_Y.append(Angle['RS' ][1])
    AngleLE_XZ.append(Angle['RE'][0])
    AngleLE_Y.append(Angle['RE'] [1])




plt.figure(1)
plt.title('2')
plt.plot(AngleLS_XZ[730:],color = 'red')
plt.plot(AngleLS_Y[730:],color = 'blue')
plt.plot(AngleLE_XZ[730:],color = 'green')
plt.plot(AngleLE_Y[730:],color = 'black')

plt.figure(2)
plt.title('3')
plt.plot(AngleLS_XZ[89:179],color = 'red')
plt.plot(AngleLS_Y[89:179],color = 'blue')
plt.plot(AngleLE_XZ[89:179],color = 'green')
plt.plot(AngleLE_Y[89:179],color = 'black')

plt.figure(3)
plt.title('3')
plt.plot(AngleLS_XZ[282:381],color = 'red')
plt.plot(AngleLS_Y[282:381],color = 'blue')
plt.plot(AngleLE_XZ[282:381],color = 'green')
plt.plot(AngleLE_Y[282:381],color = 'black')


plt.show()







#Y   = data[:,1::3]
#
#plt.figure(1)
#plt.title('2')
#plt.plot(Y[730:,0],color = 'red')
#plt.plot(Y[730:,1],color = 'blue')
#plt.plot(Y[730:,2],color = 'green')
#
#plt.figure(2)
#plt.title('3')
#plt.plot(Y[89:179,0],color = 'red')
#plt.plot(Y[89:179,1],color = 'blue')
#plt.plot(Y[89:179,2],color = 'green')
#
#plt.figure(3)
#plt.title('3')
#plt.plot(Y[282:381,0],color = 'red')
#plt.plot(Y[282:381,1],color = 'blue')
#plt.plot(Y[282:381,2],color = 'green')
#
#
#plt.show()
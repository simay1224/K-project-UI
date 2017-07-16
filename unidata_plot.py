# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 03:22:43 2017

@author: medialab
"""
# Kinect joints
SpineBase = 0
SpineMid = 1
Neck = 2
Head = 3
ShoulderLeft = 4
ElbowLeft = 5
WristLeft = 6
ShoulderRight = 7
ElbowRight = 8
WristRight = 9
SpineShoulder = 10


import cPickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


mdata  = cPickle.load(file('F:/AllData_0327/unified data array/Unified_MData/ex4/Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'))
kdata  = cPickle.load(file('F:/AllData_0327/unified data array/Unified_KData/ex4/Andy_data201612151615_unified_ex4.pkl'))

frame_no = 20

Kx = kdata[0::3,frame_no]
Ky = kdata[1::3,frame_no]
Kz = kdata[2::3,frame_no] 

Mx = mdata[0::3,frame_no]
My = mdata[1::3,frame_no]
Mz = mdata[2::3,frame_no] 

fig = plt.figure(1)
ax = fig.add_subplot(111, projection='3d')


ax.set_xlabel('Z axis')
ax.set_ylabel('X axis')
ax.set_zlabel('Y axis')

ax.scatter(Kz, Kx, Ky, c = 'green', s = 30,label='normalized Kinect data') 
ax.scatter(Mz, Mx, My, c = 'red'  , s = 30,label='normalized MoCAP data') 


ax.plot([Kz[SpineBase]    ,Kz[SpineMid]]    ,[Kx[SpineBase]    ,Kx[SpineMid]]    ,[Ky[SpineBase]    ,Ky[SpineMid]]    , c = 'green')
ax.plot([Kz[SpineShoulder],Kz[SpineMid]]    ,[Kx[SpineShoulder],Kx[SpineMid]]    ,[Ky[SpineShoulder],Ky[SpineMid]]    , c = 'green')
ax.plot([Kz[SpineShoulder],Kz[ShoulderLeft]],[Kx[SpineShoulder],Kx[ShoulderLeft]],[Ky[SpineShoulder],Ky[ShoulderLeft]], c = 'green')
ax.plot([Kz[ElbowLeft]    ,Kz[ShoulderLeft]],[Kx[ElbowLeft]    ,Kx[ShoulderLeft]],[Ky[ElbowLeft]    ,Ky[ShoulderLeft]], c = 'green')
ax.plot([Kz[ElbowLeft]    ,Kz[WristLeft]]   ,[Kx[ElbowLeft]    ,Kx[WristLeft]]   ,[Ky[ElbowLeft]    ,Ky[WristLeft]]   , c = 'green')

ax.plot([Kz[SpineShoulder],Kz[ShoulderRight]],[Kx[SpineShoulder],Kx[ShoulderRight]],[Ky[SpineShoulder],Ky[ShoulderRight]], c = 'green')
ax.plot([Kz[ElbowRight]   ,Kz[ShoulderRight]],[Kx[ElbowRight]   ,Kx[ShoulderRight]],[Ky[ElbowRight]   ,Ky[ShoulderRight]], c = 'green')
ax.plot([Kz[ElbowRight]   ,Kz[WristRight]]   ,[Kx[ElbowRight]   ,Kx[WristRight]]   ,[Ky[ElbowRight]   ,Ky[WristRight]]   , c = 'green')

ax.plot([Kz[SpineShoulder],Kz[Neck]] ,[Kx[SpineShoulder],Kx[Neck]] ,[Ky[SpineShoulder],Ky[Neck]]    , c = 'green')
ax.plot([Kz[Head]         ,Kz[Neck]] ,[Kx[Head]         ,Kx[Neck]] ,[Ky[Head]         ,Ky[Neck]]    , c = 'green')


ax.plot([Mz[SpineBase]    ,Mz[SpineMid]]    ,[Mx[SpineBase]    ,Mx[SpineMid]]    ,[My[SpineBase]    ,My[SpineMid]]    , c = 'red')
ax.plot([Mz[SpineShoulder],Mz[SpineMid]]    ,[Mx[SpineShoulder],Mx[SpineMid]]    ,[My[SpineShoulder],My[SpineMid]]    , c = 'red')
ax.plot([Mz[SpineShoulder],Mz[ShoulderLeft]],[Mx[SpineShoulder],Mx[ShoulderLeft]],[My[SpineShoulder],My[ShoulderLeft]], c = 'red')
ax.plot([Mz[ElbowLeft]    ,Mz[ShoulderLeft]],[Mx[ElbowLeft]    ,Mx[ShoulderLeft]],[My[ElbowLeft]    ,My[ShoulderLeft]], c = 'red')
ax.plot([Mz[ElbowLeft]    ,Mz[WristLeft]]   ,[Mx[ElbowLeft]    ,Mx[WristLeft]]   ,[My[ElbowLeft]    ,My[WristLeft]]   , c = 'red')

ax.plot([Mz[SpineShoulder],Mz[ShoulderRight]],[Mx[SpineShoulder],Mx[ShoulderRight]],[My[SpineShoulder],My[ShoulderRight]], c = 'red')
ax.plot([Mz[ElbowRight]   ,Mz[ShoulderRight]],[Mx[ElbowRight]   ,Mx[ShoulderRight]],[My[ElbowRight]   ,My[ShoulderRight]], c = 'red')
ax.plot([Mz[ElbowRight]   ,Mz[WristRight]]   ,[Mx[ElbowRight]   ,Mx[WristRight]]   ,[My[ElbowRight]   ,My[WristRight]]   , c = 'red')

ax.plot([Mz[SpineShoulder],Mz[Neck]] ,[Mx[SpineShoulder],Mx[Neck]] ,[My[SpineShoulder],My[Neck]]    , c = 'red')
ax.plot([Mz[Head]         ,Mz[Neck]] ,[Mx[Head]         ,Mx[Neck]] ,[My[Head]         ,My[Neck]]    , c = 'red')



ax.set_xlim(-550,150)
ax.set_ylim(-200,400)
ax.set_zlim(0,600)

ax.set_xlabel('Z axis')
ax.set_ylabel('X axis')
ax.set_zlabel('Y axis')
plt.legend( loc=1)
plt.draw()
plt.pause(1.0/10)




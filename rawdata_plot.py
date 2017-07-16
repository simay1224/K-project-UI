# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 01:02:59 2017

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
# HandLeft = 7
ShoulderRight = 7
ElbowRight = 8
WristRight = 9
# HandRight = 11
HipLeft = 10
# KneeLeft = 13
# AnkleLeft = 14
# FootLeft = 15
HipRight = 11
# KneeRight = 17
# AnkleRight = 18
# FootRight = 19
SpineShoulder = 12
# HandTipLeft = 21
# ThumbLeft = 22
# HandTipRight = 23
# ThumbRight = 24

# Mocap joints

LShoulder_1  = 0
RUArm_2      = 1 
LShoulder_2  = 2 
LUArm_1      = 3
RUArm_1      = 4
LUArm_2      = 5
Head_3       = 6
Head_2       = 7
Head_1       = 8
RShoulder_2  = 9
Chest_4      = 10
Chest_3      = 11
Chest_2      = 12
Chest_1      = 13
Hip_1        = 14
Hip_3        = 15
Hip_2        = 16 
Hip_4        = 17 
RShoulder_1  = 18
LHand_3      = 19
LHand_2      = 20
LHand_1      = 21
RHand_1      = 22 
RHand_3      = 23
RHand_2      = 24











import cPickle
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


Mkeys = ['LShoulder_1','RUArm_2','LShoulder_2', 
         'LUArm_1', 'RUArm_1', 'LUArm_2', 'Head_3', 
         'Head_2', 'Head_1', 'RShoulder_2', 'Chest_4', 
         'Chest_3', 'Chest_2', 'Chest_1', 'Hip_1', 
         'Hip_3', 'Hip_2', 'Hip_4', 'RShoulder_1', 
         'LHand_3', 'LHand_2', 'LHand_1', 'RHand_1', 
         'RHand_3', 'RHand_2']


frame_no = 230
mdata_all  = cPickle.load(file('Andy_2016-12-15 04.15.27 PM_ex4_raw.pkl'))
kdata_all  = cPickle.load(file('F:/AllData_0327/Motion and Kinect raw data/20161216/pkl/Andy/Andy_data12151615_ex4.pkl'))[frame_no]['joints']

name = 'Andy_'


Mx = []
My = []
Mz = []

for kidx in Mkeys:
    Mx.append(mdata_all[name+kidx]['X'][frame_no])
    My.append(mdata_all[name+kidx]['Y'][frame_no])
    Mz.append(mdata_all[name+kidx]['Z'][frame_no])
    
    
    
    
    

Kx = []
Ky = []
Kz = []

for kidx in [0,1,2,3,4,5,6,8,9,10,12,16,20]:
    Kx.append(kdata_all[kidx].Position.x)
    Ky.append(kdata_all[kidx].Position.y)
    Kz.append(kdata_all[kidx].Position.z)

fig = plt.figure(1)
ax = fig.add_subplot(111, projection='3d')


ax.scatter(Kz, Kx, Ky, c = 'green', s = 30,label='Kinct raw data')    

ax.plot([Kz[SpineBase]    ,Kz[HipLeft]]     ,[Kx[SpineBase]    ,Kx[HipLeft]]     ,[Ky[SpineBase]    ,Ky[HipLeft]]     , c = 'green')
ax.plot([Kz[SpineBase]    ,Kz[HipRight]]    ,[Kx[SpineBase]    ,Kx[HipRight]]    ,[Ky[SpineBase]    ,Ky[HipRight]]    , c = 'green')
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

ax.scatter(Mz, Mx, My,c = 'red',s = 30,alpha=.4,label='MOCAP raw data')

ax.plot([Mz[LShoulder_1],Mz[RShoulder_1]],[Mx[LShoulder_1],Mx[RShoulder_1]],[My[LShoulder_1],My[RShoulder_1]], c = 'red')

ax.plot([Mz[RUArm_2],Mz[RShoulder_2]],[Mx[RUArm_2],Mx[RShoulder_2]],[My[RUArm_2],My[RShoulder_2]], c = 'red')
ax.plot([Mz[RUArm_2],Mz[RShoulder_1]],[Mx[RUArm_2],Mx[RShoulder_1]],[My[RUArm_2],My[RShoulder_1]], c = 'red')
ax.plot([Mz[RUArm_2],Mz[RUArm_1]]    ,[Mx[RUArm_2],Mx[RUArm_1]]    ,[My[RUArm_2],My[RUArm_1]]    , c = 'red')
ax.plot([Mz[RUArm_2],Mz[RUArm_1]]    ,[Mx[RUArm_2],Mx[RUArm_1]]    ,[My[RUArm_2],My[RUArm_1]]    , c = 'red')
ax.plot([Mz[RUArm_1],Mz[RHand_3]]    ,[Mx[RUArm_1],Mx[RHand_3]]    ,[My[RUArm_1],My[RHand_3]]    , c = 'red')
ax.plot([Mz[RHand_1],Mz[RHand_3]]    ,[Mx[RHand_1],Mx[RHand_3]]    ,[My[RHand_1],My[RHand_3]]    , c = 'red')
ax.plot([Mz[RHand_2],Mz[RHand_3]]    ,[Mx[RHand_2],Mx[RHand_3]]    ,[My[RHand_2],My[RHand_3]]    , c = 'red')

ax.plot([Mz[LUArm_2],Mz[LShoulder_2]],[Mx[LUArm_2],Mx[LShoulder_2]],[My[LUArm_2],My[LShoulder_2]], c = 'red')
ax.plot([Mz[LUArm_2],Mz[LShoulder_1]],[Mx[LUArm_2],Mx[LShoulder_1]],[My[LUArm_2],My[LShoulder_1]], c = 'red')
ax.plot([Mz[LUArm_2],Mz[LUArm_1]]    ,[Mx[LUArm_2],Mx[LUArm_1]]    ,[My[LUArm_2],My[LUArm_1]]    , c = 'red')
ax.plot([Mz[LUArm_2],Mz[LUArm_1]]    ,[Mx[LUArm_2],Mx[LUArm_1]]    ,[My[LUArm_2],My[LUArm_1]]    , c = 'red')
ax.plot([Mz[LUArm_1],Mz[LHand_3]]    ,[Mx[LUArm_1],Mx[LHand_3]]    ,[My[LUArm_1],My[LHand_3]]    , c = 'red')
ax.plot([Mz[LHand_1],Mz[LHand_3]]    ,[Mx[LHand_1],Mx[LHand_3]]    ,[My[LHand_1],My[LHand_3]]    , c = 'red')
ax.plot([Mz[LHand_2],Mz[LHand_3]]    ,[Mx[LHand_2],Mx[LHand_3]]    ,[My[LHand_2],My[LHand_3]]    , c = 'red')


ax.plot([Mz[Chest_1],Mz[RShoulder_2]],[Mx[Chest_1],Mx[RShoulder_2]],[My[Chest_1],My[RShoulder_2]], c = 'red')
ax.plot([Mz[Chest_1],Mz[LShoulder_2]],[Mx[Chest_1],Mx[LShoulder_2]],[My[Chest_1],My[LShoulder_2]], c = 'red')

ax.plot([Mz[Chest_3],Mz[RShoulder_2]],[Mx[Chest_3],Mx[RShoulder_2]],[My[Chest_3],My[RShoulder_2]], c = 'red')
ax.plot([Mz[Chest_2],Mz[LShoulder_2]],[Mx[Chest_2],Mx[LShoulder_2]],[My[Chest_2],My[LShoulder_2]], c = 'red')
ax.plot([Mz[Chest_3],Mz[Hip_4]]      ,[Mx[Chest_3],Mx[Hip_4]]      ,[My[Chest_3],My[Hip_4]]      , c = 'red')
ax.plot([Mz[Chest_2],Mz[Hip_3]]      ,[Mx[Chest_2],Mx[Hip_3]]      ,[My[Chest_2],My[Hip_3]]      , c = 'red')


ax.plot([Mz[Hip_3],Mz[Hip_4]]        ,[Mx[Hip_3],Mx[Hip_4]]        ,[My[Hip_3],My[Hip_4]]      , c = 'red')
ax.plot([Mz[Hip_3],Mz[Hip_1]]        ,[Mx[Hip_3],Mx[Hip_1]]        ,[My[Hip_3],My[Hip_1]]      , c = 'red')
ax.plot([Mz[Hip_2],Mz[Hip_4]]        ,[Mx[Hip_2],Mx[Hip_4]]        ,[My[Hip_2],My[Hip_4]]      , c = 'red')
ax.plot([Mz[Hip_2],Mz[Hip_1]]        ,[Mx[Hip_2],Mx[Hip_1]]        ,[My[Hip_2],My[Hip_1]]      , c = 'red')

ax.plot([Mz[Head_3],Mz[Head_1]]      ,[Mx[Head_3],Mx[Head_1]]    ,[My[Head_3],My[Head_1]]      , c = 'red')
ax.plot([Mz[Head_2],Mz[Head_1]]      ,[Mx[Head_2],Mx[Head_1]]    ,[My[Head_2],My[Head_1]]      , c = 'red')
ax.plot([Mz[Head_3],Mz[Head_2]]      ,[Mx[Head_3],Mx[Head_2]]    ,[My[Head_3],My[Head_2]]      , c = 'red')

ax.plot([Mz[Chest_4],Mz[RShoulder_1]],[Mx[Chest_4],Mx[RShoulder_1]],[My[Chest_4],My[RShoulder_1]], c = 'red')
ax.plot([Mz[Chest_4],Mz[LShoulder_1]],[Mx[Chest_4],Mx[LShoulder_1]],[My[Chest_4],My[LShoulder_1]], c = 'red')
ax.plot([Mz[Chest_4],Mz[Hip_1]]      ,[Mx[Chest_4],Mx[Hip_1]]      ,[My[Chest_4],My[Hip_1]]      , c = 'red')
ax.plot([Mz[Chest_4],Mz[Hip_2]]      ,[Mx[Chest_4],Mx[Hip_2]]      ,[My[Chest_4],My[Hip_2]]      , c = 'red')




#ax.set_xlim(-350,350)
ax.set_ylim(-1,1)
#ax.set_zlim(0,600)




ax.set_xlabel('Z axis')
ax.set_ylabel('X axis')
ax.set_zlabel('Y axis')
plt.legend( loc=1)
plt.draw()
plt.pause(1.0/10)


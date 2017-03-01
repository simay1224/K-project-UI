# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 14:17:04 2016

@author: user
"""

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import cv2,glob,pdb,h5py,cPickle,copy
import numpy as np
from matplotlib import pyplot as plt
import pylab as pl
'''
# values for enumeration '_JointType'
JointType_SpineBase = 0
JointType_SpineMid = 1
JointType_Neck = 2
JointType_Head = 3
JointType_ShoulderLeft = 4
JointType_ElbowLeft = 5
JointType_WristLeft = 6
JointType_HandLeft = 7
JointType_ShoulderRight = 8
JointType_ElbowRight = 9
JointType_WristRight = 10
JointType_HandRight = 11
JointType_HipLeft = 12
JointType_KneeLeft = 13
JointType_AnkleLeft = 14
JointType_FootLeft = 15
JointType_HipRight = 16
JointType_KneeRight = 17
JointType_AnkleRight = 18
JointType_FootRight = 19
JointType_SpineShoulder = 20
JointType_HandTipLeft = 21
JointType_ThumbLeft = 22
JointType_HandTipRight = 23
JointType_ThumbRight = 24


name = 'data09271342'
datapath = 'D:\\kinect project\\test data\\'+name+'.h5'
pkldata = 'D:\\kinect project\\test data\\backup\\dj_'+name+'.pkl'
colordata = 'D:\\kinect project\\test data\\'+name+'.pkl'

fig = plt.figure(1,figsize=[16,8])
axL1 = plt.subplot(2,2,1)
frame = np.zeros([424,512,3]).astype('uint8')
im1 = pl.imshow(frame)
plt.axis('off')
axL2 = plt.subplot(2,2,2)
im2 = pl.imshow(frame)
plt.axis('off')

axL3 = plt.subplot(2,2,3)
im3 = pl.imshow(frame)
plt.axis('off')

axL4 = plt.subplot(2,2,4)
im4 = pl.imshow(frame)
plt.axis('off')

def draw_body_bone(joints, color, joint0, joint1,status=[],judge = 0):
    if judge == 0:
        X = (joints[joint0].x, joints[joint1].x)
        Y = (joints[joint0].y, joints[joint1].y)
        axL1.plot(X,Y,color = color,linewidth=1)
    else:
        #pass
        joint0State = status[joint0].TrackingState;
        joint1State = status[joint1].TrackingState;

        # both joints are not tracked
        if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked): 
            return

        # both joints are not *really* tracked
        if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
            return    
        X = (joints[joint0].x, joints[joint1].x)
        Y = (joints[joint0].y, joints[joint1].y)
        axL3.plot(X,Y,color = color,linewidth=1)
    
def drawbone(i,status=[],judge = 0):
    joints = data[i]
    # Torso
    color = (1,0,0)    
    draw_body_bone(joints,color, JointType_Head, JointType_Neck,status,judge);
    draw_body_bone(joints,color, JointType_Neck, JointType_SpineShoulder,status,judge);
    draw_body_bone(joints,color, JointType_SpineShoulder, JointType_SpineMid,status,judge);
    draw_body_bone(joints,color, JointType_SpineMid, JointType_SpineBase,status,judge);
    draw_body_bone(joints,color, JointType_SpineShoulder, JointType_ShoulderRight,status,judge);
    draw_body_bone(joints,color, JointType_SpineShoulder,JointType_ShoulderLeft,status,judge);
    draw_body_bone(joints,color, JointType_SpineBase, JointType_HipRight,status,judge);
    draw_body_bone(joints,color, JointType_SpineBase, JointType_HipLeft,status,judge);
    
    # Right Arm    
    draw_body_bone(joints,color, JointType_ShoulderRight,JointType_ElbowRight,status,judge);
    draw_body_bone(joints,color, JointType_ElbowRight, JointType_WristRight,status,judge);
    draw_body_bone(joints,color, JointType_WristRight, JointType_HandRight,status,judge);


    # Left Arm
    draw_body_bone(joints,color, JointType_ShoulderLeft,JointType_ElbowLeft,status,judge);
    draw_body_bone(joints,color, JointType_ElbowLeft, JointType_WristLeft,status,judge);
    draw_body_bone(joints,color, JointType_WristLeft, JointType_HandLeft,status,judge);


init = 70
end  = 150
data = cPickle.load(file(pkldata,'rb'))[init:end]
cdata = cPickle.load(file(colordata,'rb'))[init:end]

f = h5py.File(datapath,'r')

bdimgs = f['imgs']['bdimgs'].keys()[init:end]
dimgs  = f['imgs']['dimgs'].keys()[init:end]
fnum = len(bdimgs)
idx = 0

J = {}
J[0] = {}
J[1] = {}
J[4] = {}
J[5] = {}
J[6] = {}
J[8] = {}
J[9] = {}
J[10] = {}
J[20] = {}


for i in J.keys():
    J[i]['x'] = []
    J[i]['y'] = []
    J[i]['d'] = []  # depth
    J[i]['rd'] = []
    J[i]['i'] = []  # inside body?
    J[i]['s'] = []  # status

for idx ,i in enumerate(data):
    for j in J.keys():    

        J[j]['x'].append(i[j].x)
        J[j]['y'].append(i[j].y)
        J[j]['d'].append(f['imgs']['dimgs'][dimgs[idx]][:][int(i[j].y)][int(i[j].x)])
        J[j]['rd'].append(cdata[idx]['joints'][j].Position.z*1000)        
        J[j]['s'].append(cdata[idx]['joints'][j].TrackingState)
        if f['imgs']['bdimgs'][bdimgs[idx]][:][int(i[j].y)][int(i[j].x)][0] ==255:
            J[j]['i'].append(0)
        else:
            J[j]['i'].append(1)
            
            
cPickle.dump(J,file('test1027.pkl','wb'))            

#while(idx<fnum-1):
#    print idx+init
#    
#    frame = f['imgs']['bdimgs'][bdimgs[idx]][:]
#    dframe = f['imgs']['dimgs'][dimgs[idx]][:]
#    comb = copy.copy(dframe)
#    comb[frame==255]=0
#    comb = comb/3000.0*255
#
#    im1.set_data(frame)
#    drawbone(idx)
#    plt.title(idx)
#    im3.set_data(frame)
#    drawbone(idx,cdata[idx]['joints'],1)
#    im4.set_data(np.uint8(comb))
#    
#    im2.set_data(dframe)
#    #fname = './img/'+name+'_'+repr(idx).zfill(3)+'.jpg'
#    #pl.savefig(fname)
#    pl.pause(.01)
#    pl.draw()
#    axL1.lines = []
#    axL3.lines = []
#    idx+=1



#=========================================================================
d = cPickle.load(file('test1011.pkl','rb'))


#fig = plt.figure(1,figsize=[16,8])

idx = 10

X = range(70,150)
Y1 = d[idx]['x']
Y2 = d[idx]['y']
Y3 = d[idx]['d']
Y4 = d[idx]['i']
Y5 = ((np.roll(Y1,1)-np.array(Y1))**2+(np.roll(Y2,1)-np.array(Y2))**2)**0.5
Y5[0] = 0
Y6 = d[idx]['s']
Y7 = d[idx]['rd']

plt.suptitle('right wrist',size = 20)

ax1 = plt.subplot(5,1,1)
plt.plot(X,Y1,color='red',label = 'X') 
plt.plot(X,Y2,color = 'green',label = 'Y')
ax1.set_title("X & Y coordinate")  
legend = ax1.legend(loc=1, shadow=True)


ax2=plt.subplot(5,1,2)
plt.plot(X,Y5)
ax2.set_title("point shift")  

#ax3=plt.subplot(5,1,3)
#plt.plot(X,Y3)
#ax3.set_title("depth")  

ax4=plt.subplot(5,1,4)
plt.plot(X,Y4)
ax4.set_title("inside body? ")  
pl.draw()


ax3=plt.subplot(5,1,3)
plt.plot(X,Y6)
ax3.set_title("state")  
pl.draw()

ax5=plt.subplot(5,1,5)
plt.plot(X,(np.array(Y3).T[0].T)-np.array(Y7))
ax5.set_title("depth  diff")  
pl.draw()



#=============================== morrior compare =========================
cidx = [4,5,6]
idx  = [8,9,10]
d = cPickle.load(file('test1011.pkl','rb'))

X = range(70,150)
figno = 1

name = ['shlder vs spinshlder (data09271342)','elbow vs spinshlder (data09271342)','wrist vs spinshlder (data09271342)']

for i,j in zip(cidx,idx):

    

    Y1 =  np.array(d[i]['x'])
    Yc1 = np.array(d[j]['x'])
    Y2 =  np.array(d[i]['y'])
    Yc2 = np.array(d[j]['y'])
    
    
    m1 =  np.array(d[20]['x'])
    m2 =  np.array(d[20]['y'])

    fig = plt.figure(figno,figsize=[16,8])
    plt.suptitle(name[figno-1],size = 20)
    ax1 = plt.subplot(4,1,1)
    plt.plot(X,Y1-m1,color=(1,0,0),label='left')
    plt.plot(X,-(Yc1-m1),color=(0,1,0),label='right')
    ax1.set_title("X coordinate")    
    legend = ax1.legend(loc=1, shadow=True)
    
    ax2 = plt.subplot(4,1,2)
    plt.plot(X,(Y1+Yc1)-2*m1,color=(0,0,1))
    ax2.set_title("X comb")  
    pl.draw()

    ax3 = plt.subplot(4,1,3)
    plt.plot(X,Y2-m2,color=(1,0,0),label= 'left')
    plt.plot(X,Yc2-m2,color=(0,1,0),label='right')
    ax3.set_title("Y coordinate")  
    legend = ax3.legend(loc=1, shadow=True)
    pl.draw()


    ax4 = plt.subplot(4,1,4)
    plt.plot(X,(Y2-Yc2),color=(0,0,1))
    ax4.set_title("Y comb")    
    legend = ax1.legend(loc=1, shadow=True)    



    figno+=1

'''

#============================================================
name = 'data09271342'
datapath = 'D:\\kinect project\\test data\\'+name+'.h5'
pkldata = 'D:\\kinect project\\test data\\backup\\dj_'+name+'.pkl'
colordata = 'D:\\kinect project\\test data\\'+name+'.pkl'

init = 70
end  = 150
data = cPickle.load(file(pkldata,'rb'))[init:end]
cdata = cPickle.load(file(colordata,'rb'))[init:end]

f = h5py.File(datapath,'r')

bdimgs = f['imgs']['bdimgs'].keys()[init:end]
dimgs  = f['imgs']['dimgs'].keys()[init:end]
fnum = len(bdimgs)


mtype ='mirror'  #move type
 
th = 16

d = cPickle.load(file('test1027.pkl','rb'))


#fig = plt.figure(1,figsize=[16,8])

idx = 6
X = d[idx]['x']
Y = d[idx]['y']
depth = d[idx]['d']
inside = d[idx]['i']
tacking = d[idx]['s']
jdepth = d[idx]['rd']

oldx= []
oldy= []

#====== compare pair ==============

cidx = 10
cX = d[cidx]['x']
cY = d[cidx]['y']
cdepth = d[cidx]['d']
cinside = d[cidx]['i']
ctacking = d[cidx]['s']
cjdepth = d[cidx]['rd']

coldx= []
coldy= []


oridepth = 2000
error = 0
sr    = 2# search region
from scipy.ndimage.morphology import distance_transform_edt as dte
dismtx = np.ones((sr*2+1,sr*2+1))
dismtx[sr,sr]=0
dismtx = dte(dismtx)


for i in xrange(len(X)):
    print i
    if i == 0:
        oldx.append(X[i])
        oldy.append(Y[i])
        coldx.append(cX[i])
        coldy.append(cY[i])        
        
        pass    
    else:
        dist = ((X[i]-oldx[-1])**2+(Y[i]-oldy[-1])**2)**0.5
        vx =  X[i] - oldx[-1] 
        vy =  Y[i] - oldy[-1]
        cvx =  (cX[i] - coldx[-1])*1 
        cvy =  (cY[i] - coldy[-1])*1
 
            
        if (tacking[i] !=2) or (inside[i] == 0):
            
            if dist > th :  # error happen
                error = 1
                #pdb.set_trace()
               
            if error: # refer compair joint
                
                # predict coordinate
                px = int(np.round(oldx[-1] - cvx)) 
                py = int(np.round(oldy[-1] + cvy))
                
                dmtx  = f['imgs']['dimgs'][dimgs[i]][:][py-sr:py+sr+1,px-sr:px+sr+1,0].astype(int) 
                bdmtx = f['imgs']['bdimgs'][bdimgs[i]][:][py-sr:py+sr+1,px-sr:px+sr+1,0].astype(int)          
                bdmtx[bdmtx==255] = 10**6
                dmtx[(dmtx-oridepth)>150]=10**8
                mtx = dmtx*0.01+bdmtx*0.6+dismtx*0.4
                if mtx[:].min() < 10**6:
                    mx = (mtx[:].argmin())/(sr*2+1)
                    my = np.mod(mtx[:].argmin(),(sr*2+1))
                    X[i] = oldx[-1]+(mx-sr)
                    Y[i] = oldy[-1]+(my-sr)
                else:
                    X[i] = oldx[-1]
                    Y[i] = oldy[-1]            
         
        else:
            error = 0
        
        oldx.append(X[i])
        oldy.append(Y[i])
        coldx.append(cX[i])
        coldy.append(cY[i]) 

coor = {}
coor['x'] = oldx
coor['y'] = oldy
cPickle.dump(coor,file('modcoor.pkl','wb'))




















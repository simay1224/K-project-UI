# -*- coding: utf-8 -*-
"""
Created on Wed May 17 13:10:57 2017

@author: medialab
"""
import h5py,pdb
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import _pickle as cPickle

gp = cPickle.load(open('model_G.pkl','rb'))

src_path = '../TF/Concatenate_Data/'
dst_path = '../TF/data/FC/'
date_ext = '_REL0504'
test_ext = ''

W1  = h5py.File(dst_path+'model'+date_ext+test_ext+'.h5','r')['W1' ][:]
W2  = h5py.File(dst_path+'model'+date_ext+test_ext+'.h5','r')['W2' ][:]
Wp1 = h5py.File(dst_path+'model'+date_ext+test_ext+'.h5','r')['Wp1'][:]
Wp2 = h5py.File(dst_path+'model'+date_ext+test_ext+'.h5','r')['Wp2'][:]
be1 = h5py.File(dst_path+'model'+date_ext+test_ext+'.h5','r')['b1' ][:]
be2 = h5py.File(dst_path+'model'+date_ext+test_ext+'.h5','r')['b2' ][:]
bd1 = h5py.File(dst_path+'model'+date_ext+test_ext+'.h5','r')['bp1'][:]
bd2 = h5py.File(dst_path+'model'+date_ext+test_ext+'.h5','r')['bp2'][:]
[Min,Max] =  h5py.File(dst_path+'model'+date_ext+test_ext+'.h5','r')['minmax'][:]

def sigmoid(x):
    return 1/(1+np.exp(-x))
    
def relu(x):
    x[x<0]=0
    return x    

def DAE(kdata):

    h1 = relu(np.dot(kdata,W1 )+be1)
    h2 = relu(np.dot(   h1,W2 )+be2)
    h3 = relu(np.dot(   h2,Wp1)+bd1)
    h4 = sigmoid(np.dot(   h3,Wp2)+bd2)    
    return h4.reshape(-1,18)
    

    
src_path = 'D:/Project/K_project/data/Motion and Kinect unified/'
Mpath    = 'Unified_MData/'
Kpath    = 'Unified_KData/'
Rpath    = 'reliability/'

Mdata  = cPickle.load(open(src_path+Mpath+'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl','rb'),encoding = 'latin1')
kdata  = cPickle.load(open(src_path+Kpath+'Andy_data201612151615_unified_ex4.pkl','rb'),encoding = 'latin1')
reconk = cPickle.load(open(src_path+Kpath+'Andy_data201612151615_unified_ex4.pkl','rb'),encoding = 'latin1')
Rel    = cPickle.load(open(src_path+Rpath+'Andy_data201612151615_Rel_ex4.pkl','rb'),encoding = 'latin1')


NUM_LABELS = len(Mdata)  # total number of the joints
NUM_FRAMES = len(Mdata[0][1])   # total number of the frames
kNUM_FRAMES = len(kdata[0][1]) 



  
th = 0.6

Rel6  = np.array(Rel[6])>0.75
Rel10 = np.array(Rel[10])>0.75

len6  = 135.5
len10 = 135.5


for fidx in range(min(kNUM_FRAMES,NUM_FRAMES)):
    print(fidx)
    
    veccmp = {}
    if (Rel[6][fidx]<th) or (Rel[10][fidx]<th):
        Kj= np.hstack([kdata[4][:,fidx],kdata[5][:,fidx],kdata[6][:,fidx],kdata[8][:,fidx],kdata[9][:,fidx],kdata[10][:,fidx]]).reshape((-1,18))

        Mp = DAE((Kj-Min)/Max)
        reconJ, _ = gp.predict(Mp , return_std=True)
        
        diff = np.roll(reconJ,-3)-reconJ   
        dnmntr = [(sum([diff[:,i*3]**2,diff[:,i*3+1]**2,diff[:,i*3+2]**2]))**0.5 for i in range(6)]
#        pdb.set_trace()
        if (Rel[6][fidx]<th) :
            veccmp[6] = diff[0,3:6]/dnmntr[1]
            reconk[6][:,fidx] = kdata[5][:,fidx]+veccmp[6]*len6


        if (Rel[10][fidx]<th):
            veccmp[10] = diff[0,12:15]/dnmntr[4]
            reconk[10][:,fidx] = kdata[9][:,fidx]+veccmp[10]*len6


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


ax.set_xlabel('Z axis')
ax.set_ylabel('X axis')
ax.set_zlabel('Y axis') 

for frame_no in range(min(kNUM_FRAMES,NUM_FRAMES)):
   
    plt.cla()
    
    xs = []
    ys = []
    zs = []
    mxs = []
    mys = []
    mzs = []
    kxs = []
    kys = []
    kzs = []

    for joint_idx in  Mdata.keys() :
        xs.append(Mdata[joint_idx][0][frame_no])
        ys.append(Mdata[joint_idx][1][frame_no])
        zs.append(Mdata[joint_idx][2][frame_no])
        mxs.append(reconk[joint_idx][0][frame_no])
        mys.append(reconk[joint_idx][1][frame_no])
        mzs.append(reconk[joint_idx][2][frame_no])        
        
        kxs.append(kdata[joint_idx][0][frame_no])
        kys.append(kdata[joint_idx][1][frame_no])
        kzs.append(kdata[joint_idx][2][frame_no])

    ax.scatter(kzs, kxs, kys, c = 'red', s = 100,label='Kinect Joints')    
    ax.scatter(zs, xs, ys,c = 'green',s = 50,alpha=.4,label='MoCam Joints')
    ax.scatter(mzs, mxs, mys,c = 'blue',s = 50,alpha=.4,label='reconstruct')
    ax.set_xlim(-300,300)
    ax.set_ylim(-200,400)
    ax.set_zlim(50,600)
    ax.set_title(frame_no)
    ax.set_xlabel('Z axis')
    ax.set_ylabel('X axis')
    ax.set_zlabel('Y axis')
    plt.legend( loc=1)
    plt.draw()
    plt.pause(1.0/120)
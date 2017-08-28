# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 14:21:52 2017

@author: medialab
"""

import cPickle,pdb
import numpy as np
from scipy.spatial.distance import euclidean
import scipy.signal as signal
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf

gt_src   = 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'
test_src = 'Angela_2017-03-06 09.09.00 AM_ex4_FPS30_motion_unified.pkl'
#test_src = 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'
#gt_data      = cPickle.load(open(gt_src ,'rb') ,encoding = 'latin1')[18:,30:].T
#test_data    = cPickle.load(open(test_src,'rb') ,encoding = 'latin1')[18:,30:].T

gt_data      = cPickle.load(file(gt_src,'rb'))[12:,:].T
test_data    = cPickle.load(file(test_src,'rb'))[12:,:].T

# === initialization ===
e                   = 20
delta               = 6

distlist            = []
distplist           = []

seglist             =[]
gtseglist           =[]
# === data segment ===

#th                  = 3
#
#
#grad  = gt_data[:,6]-np.roll(gt_data[:,6],-1)
#gidx  = np.arange(gt_data.shape[0])[np.abs(grad)<th]
##gidx  = np.append(np.append([0],gidx),[gt_data.shape[0]-1])
#sidx  = gidx[np.abs(gidx-np.roll(gidx,1))>th]
##eidx  = gidx[np.abs(gidx-np.roll(gidx,-1))>th]
##idx   = list((sidx+eidx)//2) + [len(gt_data)]
#idx   =  list(sidx)+[len(gt_data)-1]

from scipy.signal import argrelextrema

datax  = gf(gt_data[:,6],15)
dx     = np.gradient(datax)
xidx = np.where(((dx > -0.1) & (dx<0.2))==True)[0]
xtmp = np.roll(xidx,1)-xidx

datay  = gf(gt_data[:,7],15)
dy     = np.gradient(datay)
yidx = np.where(((dy > -0.1) & (dy<0.2))==True)[0]
ytmp = np.roll(yidx,1)-yidx

dataz  = gf(gt_data[:,8],15)
dz     = np.gradient(dataz)
zidx = np.where(((dz > -0.1) & (dz<0.2))==True)[0]
ztmp = np.roll(zidx,1)-zidx

grad = (dx**2+dy**2+dz**2)**0.5

minm = argrelextrema(grad, np.less)

#plt.plot(dy,color='blue')
#plt.plot(dz,color='green')
#plt.plot(dx,color='red')
plt.plot(grad,color='black')
plt.plot(minm,[10]*len(minm),'o')

plt.show()

idx = xidx[np.where(abs(xtmp)>20)[0]]



# === data segment ===

#data  = gf(gt_data[:,6],11)
#
#grad  = np.gradient(data)
#grad2 = np.gradient(grad)
#
#curv  = abs(grad2)/(abs(1+grad**2))**1.5 
#
#
#datax  = gf(gt_data[:,6],7)
#datay  = gf(gt_data[:,7],7)
#dataz  = gf(gt_data[:,8],7)
#gradx  = np.gradient(datax)
#gradx2 = np.gradient(gradx)
#grady  = np.gradient(datay)
#grady2 = np.gradient(grady)
#gradz  = np.gradient(dataz)
#gradz2 = np.gradient(gradz)
#
#curv  = (((gradz2*grady-grady2*gradz)**2+\
#          (gradx2*gradz-gradz2*gradx)**2+\
#          (grady2*gradx-gradx2*grady)**2)**0.5)/(gradx**2+grady**2+gradz**2)**1.5
#
#id_clip      = np.where(curv >1)[0]
#idx = id_clip[np.abs(id_clip-np.roll(id_clip,1))>10]

          
# === main function ===


cnt = 0
test_idx   = 0
chk_flag   = False
err        = []
dist_prev  = 0
distp_prev = 0 


for gt_idx in range(len(idx)-1):
    test_data_p  = test_data + np.atleast_2d((gt_data[idx[gt_idx],6]-test_data[test_idx,6]))
    distlist = []
    distplist = []
    for j in  range(test_idx+1,test_data.shape[0]-1):
        dist  , path   = fastdtw(gt_data[idx[gt_idx]:idx[gt_idx+1],6], test_data[test_idx:j,6]  , dist=euclidean)
        dist_p, path_p = fastdtw(gt_data[idx[gt_idx]:idx[gt_idx+1],6], test_data_p[test_idx:j,6], dist=euclidean)


        print j
#        print dist
#        print dist_p
#        print np.abs(dist_p-dist)/dist
        
        distlist.append(dist)
        distplist.append(dist_p) 
        
        if j > (test_idx+30): 
            print dist_p-distp_prev
            if chk_flag:  # in check global min status
                cnt +=1
                err.append(np.abs(dist_p-dist)/dist) 
                if cnt == 20:
                    Err_mean = np.mean(err)
#                    pdb.set_trace()
                    print('err mean')
                    print(Err_mean)
                    if Err_mean <1:
                        chk_flag = False
#                        pdb.set_trace()
                        pidx  = np.argmin(distplist)
                        grad2 = np.gradient(np.gradient(distplist))
                        gidx  = np.where(grad2 <2)[0]
                        endidx = gidx[gidx>pidx][0]+test_idx
                        
                        seglist.append([test_idx,endidx])
                        gtseglist.append([idx[gt_idx],idx[gt_idx+1]])
                        test_idx = endidx+1
                        distlist = []
                        distplist = []
                        break
                        
                    else:
                        print('Ooops!!')
#                    
            else:  
                print dist_p-distp_prev
                if (dist_p-distp_prev)>20:   # turning point
                    print (' ==============  turning ====================')

                    chk_flag = True
                    err      = []
                    cnt      = 0
                    
        dist_prev  = dist
        distp_prev = dist_p 
        print ('===========\n')
    fig = plt.figure(1)
    plt.plot(test_data[:endidx,6]-500,color = 'red')
#    plt.plot(np.arange(57,endidx),test_data[57:endidx,6]-500,color = 'red')
#    plt.plot(np.arange(idx[1],idx[2]),gt_data[idx[1]:idx[2],6], color = 'blue')
    plt.plot(gt_data[idx[0]:idx[gt_idx+1],6], color = 'blue')
    plt.title('matching')
    plt.plot(idx,[-10]*len(idx),'.m')
        
#    plt.show()
    fig.savefig(str(gt_idx).zfill(2)+'.jpg')
    plt.close(fig)




        
#    fig = plt.figure(2)
#    plt.plot(np.arange(len(distplist))+57,distplist,color = 'red')
#    plt.title('dist')
##    plt.show()
#
#    fig = plt.figure(3)
#    plt.plot(np.arange(len(distplist))+57,np.gradient(distplist),color = 'green')
#    plt.title('dist grad')
#
#    fig = plt.figure(4)
#    plt.plot(np.arange(len(distplist))+57,np.gradient(np.gradient(distplist)),color = 'green')
#    plt.title('dist grad 2')    
#    
#    plt.show()



















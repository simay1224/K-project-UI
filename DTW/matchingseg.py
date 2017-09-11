# -*- coding: utf-8 -*-
"""
Created on Tue Sep 05 14:48:06 2017

@author: medialab
"""

import h5py,cPickle,pdb
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy.signal import argrelextrema

src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'
#src_path  = 'D:/Project/K_project/data/unified data array/Unified_MData/'
gt_src   = 'GT_V_data.h5'

test_src = src_path + 'Andy_2017-03-06 02.19.08 PM_ex4_FPS30_motion_unified.pkl'

data       = h5py.File('GT_V_data.h5','r')
gt_data    = {}
gt_data[1] = data['GT_1'][:]
gt_data[2] = data['GT_2'][:]
gt_data[3] = data['GT_3'][:]
gt_data[4] = data['GT_4'][:]



test_data    = cPickle.load(file(test_src,'rb'))[12:,:].T


distlist            = []
distplist           = []

seglist             =[]
gtseglist           =[]
cnt         = 0
dcnt        = 0      # decreasing cnt
test_idx    = 0
offset      = test_idx 
chk_flag    = False
deflag      = False  # decreasing flag
err         = []
dist_prev   = 0
distp_prev  = 0 
argmin      = []
distp_cmp  = np.inf

order = {}
order[0] = [1]
order[1] = [3]
order[2] = 'end'
order[3] = [4]
order[4] = [2,3]
oidx     = 0      # initail
idxlist  = [0]
j    = 0
ccnt = 1

while not ((order[oidx] == 'end') | (j == (test_data.shape[0]-1))):
#    if ccnt >11:
#        pdb.set_trace()
#    ccnt+=1
    
    if len(order[oidx])>1:
        
        
#        minval = np.inf
#        minidx = 0
#        for ii in order[oidx]:
#            d_p = []
#            for jj in range(test_idx+1,test_idx+5):
#                test_p = test_data[:,:] + np.atleast_2d((gt_data[ii][0,:]-test_data[test_idx,:]))
#                dist_p, _ = fastdtw(gt_data[ii], test_p[test_idx:jj,:], dist=euclidean)
#                d_p.append(dist_p)
#            if minval>np.mean(d_p):
#               minval = np.mean(d_p) 
#               minidx = ii
#        gt_idx = minidx  
        test_p2 = test_data[:,:] + np.atleast_2d((gt_data[2][0,:]-test_data[test_idx,:]))
        test_p3 = test_data[:,:] + np.atleast_2d((gt_data[3][0,:]-test_data[test_idx,:]))
        dist_p2, _ = fastdtw(gt_data[2], test_p2[test_idx:test_idx+40,:], dist=euclidean)
        dist_p3, _ = fastdtw(gt_data[3], test_p3[test_idx:test_idx+40,:], dist=euclidean)
        if dist_p2<dist_p3:
            gt_idx =2
        else:
            gt_idx =3
        offset = 40
#        pdb.set_trace()    
    else:
        gt_idx = order[oidx][0]
        offset = 1
        
    idxlist.append(gt_idx)    
    test_data_p  = test_data[:,:] + np.atleast_2d((gt_data[gt_idx][0,:]-test_data[test_idx,:]))
    

    distplist = []
   
    dcnt        = 0 
    deflag      = False
    
    for jidx,j in  enumerate(range(test_idx+offset,test_data.shape[0])): 

        dist_p, path_p = fastdtw(gt_data[gt_idx], test_data_p[test_idx:j,:], dist=euclidean)


        print j
        if jidx == 0:
            testlist = test_data[j,:]
        else:
            testlist = np.vstack([testlist,test_data[j,:]])
       

        distplist.append(dist_p)
        
        if len(distlist)>1:

            gdistp = np.gradient(distplist)
        
        if (j > test_idx+offset+1) & (not deflag):
            print distplist[-1]-distplist[-2]
            if (distplist[-1]-distplist[-2]) <= 0:
                dcnt +=1
                if dcnt == 1:
                    dpfirst = dist_p
            else:
                dcnt = 0
         
            if dcnt == 10:

                if (dpfirst - dist_p)>2000:
                    print('deflag on')
                    deflag = True
                else:
                    dcnt = 1       
        
        if deflag : 
            if chk_flag:  # in check global min status
                cnt +=1

                
                if dist_p < distp_cmp : # find another small value
                    cnt = 0

                    distp_cmp = dist_p
                    idx_cmp   = j
                    print(' ==== reset ====')
                    
                elif cnt == 20:




                    chk_flag = False

                    tgrad = 0

                    for ii in range(testlist.shape[1]):
                        tgrad += np.gradient(gf(testlist[:,ii],3))**2
                        
                    tgrad = tgrad**0.5
                    pdb.set_trace()
                    endidx = np.argmin(tgrad[idx_cmp-test_idx-offset-10:idx_cmp-test_idx-offset+10])+(idx_cmp-10) 
                    seglist.append([test_idx,endidx])
#                    gtseglist.append([idx[gt_idx],idx[gt_idx+1]])
                    argmin.append(np.argmin(distplist)+test_idx)                        
                    test_idx = endidx+1
                    cnt      = 0
                    oidx = gt_idx
                    
                    break
                        

#                    
            else:  
                print dist_p-distp_prev
                
#                if (((dist_p-distp_prev)>2) &  ((distp_prev-distp_prev2)<0)):  # turning point
                if (dist_p-distp_prev)>0:
#                if (gdistp[-2]<0)&(gdistp[-1]>0):
                    print (' ==============  large ====================')
#                    pdb.set_trace()
                    distp_cmp = distp_prev
                    idx_cmp   = j
                    chk_flag = True
                    err      = []
                    

#        dist_prev   = dist
        distp_prev  = dist_p 
        
        print ('===========\n')
     
#    pdb.set_trace()    
    if cnt > 0:
       seglist.append([test_idx,idx_cmp]) 
       argmin.append(np.argmin(distplist)+test_idx)
#       gtseglist.append([idx[gt_idx],idx[gt_idx+1]]) 
       endidx =  idx_cmp
    elif j == (test_data.shape[0]-1):
        seglist.append([test_idx,test_data.shape[0]-1]) 
        argmin.append(np.argmin(distplist)+test_idx)
        endidx = test_data.shape[0]-1
#        gtseglist.append([idx[gt_idx],idx[gt_idx+1]])
    
        
    fig = plt.figure(1)
    plt.plot(test_data[:endidx,6]-500,color = 'red')
    plt.plot(test_data[:,6],color = 'blue')
    plt.title('matching')

    fig.savefig(str(len(seglist)).zfill(2)+'.jpg')
    plt.close(fig)
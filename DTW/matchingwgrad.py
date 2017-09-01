# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 00:09:11 2017

@author: Dawnknight
"""
#from __future__ import print_function
import cPickle,pdb,os,glob
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy.signal import argrelextrema

gt_src    = 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'

plotJidx  = 0 
gt_data   = cPickle.load(file(gt_src,'rb'))[12:,:].T[:,6:9]


# === initialization ===

distlist            = []
distplist           = []

seglist             =[]
gtseglist           =[]
# === data segment ===




datax  = gf(gt_data[:,plotJidx],15)
dx     = np.gradient(datax)

datay  = gf(gt_data[:,plotJidx+1],15)
dy     = np.gradient(datay)

dataz  = gf(gt_data[:,plotJidx+2],15)
dz     = np.gradient(dataz)

grad = (dx**2+dy**2+dz**2)**0.5

minm = argrelextrema(grad, np.less,order = 3)[0]
idx  = np.append([0],minm)

          
# === main function ===


src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'

dst_path  = 'C:/Users/Dawnknight/Documents/GitHub/K_project/DTW/figure/0829/1 joint(greater than 0)/'



for infile in glob.glob(os.path.join(src_path,'*.pkl')):
    print infile
    test_data    = cPickle.load(file(infile,'rb'))[12:,:].T[:,6:9]
    foldername   = infile.split('\\')[-1].split('_ex4')[0][:-3]
    
    
    if not os.path.exists(dst_path+foldername):
        os.makedirs(dst_path+foldername)
        
    text_file = open(dst_path+foldername+"/log.txt", "w")
    
    
    # initialize    
    cnt         = 0
    dcnt        = 0      # decreasing cnt
    test_idx    = 0
    chk_flag    = False
    deflag      = False  # decreasing flag
    err         = []
    dist_prev   = 0
    distp_prev  = 0 
    distp_cmp   = np.inf    
    seglist     = []
    gtseglist   = []
    
    for gt_idx in range(len(idx)-1):
        test_data_p  = test_data + np.atleast_2d((gt_data[idx[gt_idx],:]-test_data[test_idx,:]))
        distlist  = []
        distplist = []
        
        dcnt        = 0 
        deflag      = False
        
        for jidx,j in  enumerate(range(test_idx+1,test_data.shape[0])):
            dist  , path   = fastdtw(gt_data[idx[gt_idx]:idx[gt_idx+1],:], test_data[test_idx:j,:]  , dist=euclidean)
            dist_p, path_p = fastdtw(gt_data[idx[gt_idx]:idx[gt_idx+1],:], test_data_p[test_idx:j,:], dist=euclidean)
    
    
            print j
            if jidx == 0:
                testlist = test_data[j,:]
            else:
                testlist = np.vstack([testlist,test_data[j,:]])            
            
            distlist.append(dist)
            distplist.append(dist_p)
            
            
            if (j > test_idx+2) & (not deflag):
                if (distlist[-1]-distlist[-2]) <= 0:
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
                    err.append(np.abs(dist_p-dist)/dist) 
                    
                    if dist_p < distp_cmp : # find another small value
                        cnt = 0
                        err = []
                        distp_cmp = dist_p
                        idx_cmp   = j
                        print(' ==== reset ====')
                        
                    elif cnt == 20:
                        Err_mean = np.mean(err)
                        text_file.write("====== seg %s ======\n" %str(gt_idx) )
                        text_file.write("err mean: %s\n" %str(Err_mean))
                        
#                        print('err mean')
#                        print(Err_mean)
#                        if Err_mean <3:
                        chk_flag = False
                        
                        tgrad = 0

                        for ii in range(testlist.shape[1]):
                            tgrad += np.gradient(gf(testlist[:,ii],3))**2
                            
                        tgrad = tgrad**0.5

                        endidx = np.argmin(tgrad[idx_cmp-test_idx-10:idx_cmp-test_idx+10])+(idx_cmp-10) 


                        seglist.append([test_idx,endidx])
                        gtseglist.append([idx[gt_idx],idx[gt_idx+1]])
                        test_idx = endidx+1
                        cnt      = 0
                        break
                        
                else:  
                    print dist_p-distp_prev
                    

                    if (dist_p-distp_prev)>0:

                        print (' ==============  large ====================')

                        distp_cmp = distp_prev
                        idx_cmp   = j
                        chk_flag = True
                        err      = []
   
            dist_prev   = dist
            distp_prev  = dist_p 
            
            print ('===========\n')
   
        if cnt > 0:
           seglist.append([test_idx,idx_cmp]) 
           gtseglist.append([idx[gt_idx],idx[gt_idx+1]]) 
           endidx =  idx_cmp
           
        elif idx_cmp == (test_data.shape[0]-1):
            seglist.append([test_idx,idx_cmp]) 
            gtseglist.append([idx[gt_idx],idx[gt_idx+1]])
            endidx =  idx_cmp    
 
            
        fig = plt.figure(1)
        plt.plot(test_data[:endidx,plotJidx]-500,color = 'red')
        plt.plot(gt_data[idx[0]:idx[gt_idx+1],plotJidx], color = 'blue')
        plt.title('matching_'+foldername)
        plt.plot(idx,[-10]*len(idx),'.m')

        fig.savefig(dst_path+foldername+'/'+str(gt_idx).zfill(2)+'.jpg')
        plt.close(fig)
        
    text_file.write("\n === seglist === \n"  )
    text_file.write(" %s \n\n" %str(seglist) )
    text_file.write(" === gtseglist === \n"  )
    text_file.write(" %s \n" %str(gtseglist) )
    text_file.close()        
        

fig = plt.figure(2)
plt.plot(test_data[:,plotJidx]-500,color = 'red')
plt.plot(gt_data[:,plotJidx], color = 'blue')
fig.savefig(dst_path+foldername+'/whole_plot.jpg')
plt.close(fig)























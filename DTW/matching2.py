# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 14:21:52 2017

@author: medialab
"""
#from __future__ import print_function
import cPickle,pdb,os,glob
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf


gt_src   = 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'
gt_data      = cPickle.load(file(gt_src,'rb'))[12:,:].T


# === initialization ===

distlist            = []
distplist           = []

seglist             =[]
gtseglist           =[]
# === data segment ===


from scipy.signal import argrelextrema

datax  = gf(gt_data[:,6],15)
dx     = np.gradient(datax)

datay  = gf(gt_data[:,7],15)
dy     = np.gradient(datay)

dataz  = gf(gt_data[:,8],15)
dz     = np.gradient(dataz)

grad = (dx**2+dy**2+dz**2)**0.5

minm = argrelextrema(grad, np.less,order = 3)[0]
idx  = np.append([0],minm)

          
# === main function ===


src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'
dst_path  = 'C:/Users/Dawnknight/Documents/GitHub/K_project/DTW/figure/0828/'
text_file = open(dst_path+"log.txt", "w")


for infile in glob.glob(os.path.join(src_path,'*.pkl')):
    print infile
    test_data    = cPickle.load(file(infile,'rb'))[12:,:].T
    foldername   = infile.split('\\')[-1].split('_ex4')[0][:-3]
    
    if not os.path.exists(dst_path+foldername):
        os.makedirs(dst_path+foldername)
    
    # initialize    
    cnt         = 0
    dcnt        = 0      # decreasing cnt
    test_idx    = 0
    chk_flag    = False
    deflag      = False  # decreasing flag
    err         = []
    dist_prev   = 0
    distp_prev  = 0 
    distp_cmp  = np.inf    
    
    for gt_idx in range(len(idx)-1):
        test_data_p  = test_data + np.atleast_2d((gt_data[idx[gt_idx],6]-test_data[test_idx,6]))
        distlist  = []
        distplist = []
        
        dcnt        = 0 
        deflag      = False
        
        for j in  range(test_idx+1,test_data.shape[0]-1):
            dist  , path   = fastdtw(gt_data[idx[gt_idx]:idx[gt_idx+1],6], test_data[test_idx:j,6]  , dist=euclidean)
            dist_p, path_p = fastdtw(gt_data[idx[gt_idx]:idx[gt_idx+1],6], test_data_p[test_idx:j,6], dist=euclidean)
    
    
            print j
            
            
            distlist.append(dist)
            distplist.append(dist_p)
            if len(distlist)>1:
                gdist  = np.gradient(distlist)
                gdistp = np.gradient(distplist)
            
            if (j > test_idx+2) & (not deflag):
                if (distlist[-1]-distlist[-2]) <= 0:
                    dcnt +=1
                    if dcnt == 1:
                        dpfirst = dist_p
                else:
                    dcnt = 0
    
                if dcnt == 10:
                    if (dpfirst - dist_p)>3000:
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
                        print('err mean')
                        print(Err_mean)
                        if gt_idx ==4:
                            pdb.set_trace()
                        if Err_mean <2:
                            chk_flag = False

                            pidx  = np.argmin(distplist)
                            grad2 = np.gradient(np.gradient(distplist))
                            gidx  = np.where(grad2 <2)[0]
                            try:
                                endidx = gidx[gidx>=pidx][0]+test_idx
                            except:
                                endidx = pidx+test_idx
                                text_file.write("file name: %s\n" %foldername)
                                text_file.write("test_idx :  %s\n" %str(test_idx))
                                text_file.write("gt_idx   :  %s\n" %str(gt_idx))
                                text_file.write("====================\n\n\n" )

                            seglist.append([test_idx,endidx])
                            gtseglist.append([idx[gt_idx],idx[gt_idx+1]])
                            test_idx = endidx+1
                            cnt      = 0
                            break
                            
                        else:
                            print('Ooops!!')
                   
                else:  
                    print dist_p-distp_prev
                    

                    if (dist_p-distp_prev)>2:

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
        plt.plot(test_data[:endidx,6]-500,color = 'red')
        plt.plot(gt_data[idx[0]:idx[gt_idx+1],6], color = 'blue')
        plt.title('matching')
        plt.plot(idx,[-10]*len(idx),'.m')

        fig.savefig(dst_path+foldername+'/'+str(gt_idx).zfill(2)+'.jpg')
        plt.close(fig)

text_file.close()




















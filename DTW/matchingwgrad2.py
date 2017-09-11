# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 20:21:40 2017

@author: Dawnknight
"""
import h5py,cPickle,pdb,os,glob
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf





#test_src = src_path + 'Andy_2017-03-06 02.19.08 PM_ex4_FPS30_motion_unified.pkl'

data       = h5py.File('GT_V_data_mod_EX4.h5','r')
gt_data    = {}
gt_data[1] = data['GT_1'][:]
gt_data[2] = data['GT_2'][:]
gt_data[3] = data['GT_3'][:]
gt_data[4] = data['GT_4'][:]



#test_data    = cPickle.load(file(test_src,'rb'))[12:,:].T


src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'
#src_path  = 'D:/Project/K_project/data/unified data array/Unified_MData/'
dst_path  = 'C:/Users/Dawnknight/Documents/GitHub/K_project/DTW/figure/0911/7 joints/'


for infile in glob.glob(os.path.join(src_path,'*.pkl')):
    print infile
    test_data    = cPickle.load(file(infile,'rb'))[12:,:].T
    foldername   = infile.split('\\')[-1].split('_ex4')[0][:-3]
    
    if not os.path.exists(dst_path+foldername):
        os.makedirs(dst_path+foldername)
        
    text_file = open(dst_path+foldername+"/log.txt", "w")

    # === initial setting ===
    flag = True
    chkflag = False
    start = []
    cnt = 0
    test_idx = 0
    seglist = []
    gt_idx  = 0
    
    order = {}
    order[0] = [1]
    order[1] = [3]
    order[2] = 'end'
    order[3] = [4]
    order[4] = [2,3]
    oidx     = [1]      # initail
    idxlist = []


    for i in range(test_data.shape[0]):
        print i
        if i == 0:
            inputdata = test_data[i,:]
        else:
            inputdata = np.vstack([inputdata,test_data[i,:]])
     
            tgrad = 0
            for ii in range(test_data.shape[1]):
                tgrad += np.gradient(gf(inputdata[:,ii],3))**2
            tgrad = tgrad**0.5
    
                
            if tgrad[-1] < 0.6:
                if flag:
                    if start == []:
                        start = [i]
                        chkflag = True
                    elif (i - start[-1])>40:
                        start.append(i)
                        chkflag = True
                    flag = False 
            else:
                if not flag:
                    flag = True 
        
            if chkflag & (start[-1]!=1):
                cnt +=1
                if cnt ==10:
                    
                    tgrad = 0
                    for ii in range(inputdata.shape[1]):
                        tgrad += np.gradient(gf(inputdata[:,ii],3))**2   
                    tgrad = tgrad**0.5    
    
                    endidx = np.argmin(tgrad[start[-1]-10:start[-1]+10])+ (start[-1]-10) 
                    
                    # check movment number
                    if len(oidx)>1:
                        minval = np.inf
                        for j in oidx:
                            moddata = inputdata[test_idx:endidx,:] + np.atleast_2d((gt_data[j][0,:]-test_data[test_idx,:]))
                            dist, _ = fastdtw(gt_data[j], moddata, dist=euclidean)
                            if minval>dist:    
                               minval = dist
                               minidx = j
                        gt_idx = minidx   
                    else:
                        gt_idx = oidx[0]
                        
                    idxlist.append(gt_idx)
                    oidx = order[gt_idx]
                    
                    seglist.append([test_idx,endidx])
                    test_idx = endidx+1
                    chkflag = False
                    cnt = 0
            else:
                cnt = 0
        if order[gt_idx] == 'end':
#            idxlist.append(gt_idx)
            break
     
    if (cnt!=0) & ((len(start)-len(seglist))>1):
        endidx = i
        if len(oidx)>1:
            minval = np.inf
            for j in oidx:
                moddata = inputdata[test_idx:endidx,:] + np.atleast_2d((gt_data[j][0,:]-test_data[test_idx,:]))
                dist, _ = fastdtw(gt_data[j], moddata, dist=euclidean)
                if minval>dist:    
                   minval = dist
                   minidx = j
            gt_idx = minidx   
        else:
            gt_idx = oidx[0]
                        
        idxlist.append(gt_idx)    
        seglist.append([test_idx,i])  
        
    text_file.write("\n === seglist === \n"  )
    text_file.write(" %s \n\n" %str(seglist) )
    text_file.write(" === idx list === \n"  )
    text_file.write(" %s \n" %str(idxlist) )
    text_file.close()      
        
    for idx,i in enumerate(seglist):    
    
        fig = plt.figure(1)
        plt.plot(test_data[:i[1],6]-500,color = 'red')
        plt.plot(test_data[:,6],color = 'blue')
        
        plt.title('matching_'+foldername)
        
        fig.savefig(dst_path+foldername+'/'+str(idx).zfill(2)+'.jpg')
        plt.close(fig)    
        
        
        
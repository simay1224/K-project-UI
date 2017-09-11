# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 20:27:18 2017

@author: Dawnknight
"""

import h5py,cPickle,pdb
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf


#src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'
src_path  = 'D:/Project/K_project/data/unified data array/Unified_MData/'
gt_src   = 'GT_V_data.h5'

test_src = src_path + 'Andy_2017-03-06 02.17.39 PM_ex4_FPS30_motion_unified.pkl'

data       = h5py.File('GT_V_data_mod_EX4.h5','r')
gt_data    = {}
gt_data[1] = data['GT_1'][:]
gt_data[2] = data['GT_2'][:]
gt_data[3] = data['GT_3'][:]
gt_data[4] = data['GT_4'][:]



test_data    = cPickle.load(file(test_src,'rb'))[12:,:].T
flag = True
chkflag = False
start = []
end  =[]
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
    
#    pdb.set_trace()
    if i == 0:
        inputdata = test_data[i,:]
    else:
        inputdata = np.vstack([inputdata,test_data[i,:]])
 
        tgrad = 0
        for ii in range(test_data.shape[1]):
            tgrad += np.gradient(gf(inputdata[:,ii],3))**2
        tgrad = tgrad**0.5
#        print tgrad
            
        if tgrad[-1] < 0.6:
            if flag:
#                pdb.set_trace()
                if start == []:
                    start = [i]
                    chkflag = True
                elif (i - start[-1])>40:
                    start.append(i)
                    chkflag = True
                flag = False
        else:
            if not flag:
                end.append(i)
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
                        dist, path = fastdtw(gt_data[j], moddata, dist=euclidean)
                        print dist/len(path)
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
#        idxlist.append(gt_idx)
#        cnt = 0
        break
#pdb.set_trace()
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
     
    
for idx,i in enumerate(seglist):    

    fig = plt.figure(1)
    plt.plot(test_data[:i[1],6]-500,color = 'red')
    plt.plot(test_data[:,6],color = 'blue')
    plt.title('matching')
    
    fig.savefig(str(idx).zfill(2)+'.jpg')
    plt.close(fig)    
    
    
 
Tmp = [] 
  
for i in range(2,test_data.shape[0]):
    tgrad = 0
    for ii in range(test_data.shape[1]):
        tgrad += np.gradient(gf(test_data[:i,ii],3))**2
    tgrad = tgrad**0.5

    Tmp.append(tgrad[-1])
    
if tgrad[-1] < 0.5:
    if flag:
        start.append(i)
        chkflag = True
        flag = False
    
plt.plot(Tmp)
plt.show()



#    tgrad = {}
#    for ii in range(0,test_data.shape[1],3):
#        tgrad[ii] = np.gradient(gf(test_data[:,ii],3))**2
#        tgrad[ii] +=np.gradient(gf(test_data[:,ii+1],3))**2
#        tgrad[ii] +=np.gradient(gf(test_data[:,ii+2],3))**2
#        tgrad[ii] = tgrad[ii]**0.5
#    for i in tgrad.keys():
#        print i
#        plt.figure(i/3)
#        plt.plot(range(600,650),tgrad[i][600:650])
#        
#    plt.show()









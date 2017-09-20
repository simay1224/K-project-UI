# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 03:20:17 2017

@author: Dawnknight
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 14:50:20 2017

@author: medialab
"""



import h5py,cPickle,pdb,glob,os
import numpy as np
from scipy.spatial.distance import euclidean,_validate_vector
from fastdtw import fastdtw as orifastdtw
from w_fastdtw import fastdtw,dtw
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy.linalg import norm

def wt_euclidean(u,v,w):
    u = _validate_vector(u)
    v = _validate_vector(v)
    dist = norm(w*(u - v))
    return dist

Jweight = np.array([0., 0., 0., 3., 3., 3., 9., 9., 9.,\
                    0., 0., 0., 3., 3., 3., 9., 9., 9.,\
                    0., 0., 0.])
    
Jweight = Jweight/sum(Jweight)*1.5

#src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'
src_path  = 'D:/Project/K_project/data/unified data array/Unified_MData/'
gt_src   = 'GT_V_data.h5'

#test_src = src_path + 'Angela_2017-03-06 09.10.02 AM_ex4_FPS30_motion_unified.pkl'
test_src = src_path + 'Angela_2017-03-06 09.09.00 AM_ex4_FPS30_motion_unified.pkl'




data       = h5py.File('GT_V_data_mod_EX4.h5','r')
gt_data    = {}
gt_data[1] = data['GT_1'][:]
gt_data[2] = data['GT_2'][:]
gt_data[3] = data['GT_3'][:]
gt_data[4] = data['GT_4'][:]



test_data    = cPickle.load(file(test_src,'rb'))[12:,:].T


cnt         = 0
dcnt        = 0      # decreasing cnt
test_idx    = 0

chk_flag    = False
deflag      = False  # decreasing flag

distp_prev  = 0 

distp_cmp  = np.inf

order     = {}
order[0]  = [1]
order[1]  = [3]
order[2]  = 'end'
order[3]  = [4]
order[4]  = [2,3]
oidx      = 0      # initail
gt_idx    = 0
idxlist   = []
seglist   = []
j         = 0


while not ((order[oidx] == 'end') | (j == (test_data.shape[0]-1))):
    
    dpfirst     = {}
    dist_p      = {}
    dcnt        = 0 
    deflag      = False
    deflag_mul  = {}
    minval      = np.inf 
    onedeflag   = False
    segend      = False
    if (len(order[oidx])>1 ):
        for ii in order[oidx]:
            deflag_mul[ii] = False 
    else:
       gt_idx = order[oidx][0] 
       idxlist.append(gt_idx)
    
    for jidx,j in  enumerate(range(test_idx,test_data.shape[0])): 

        print j

        if jidx == 0:
            testlist = test_data[j,:]
        else:
            testlist = np.vstack([testlist,test_data[j,:]])
      
        if not deflag :
            if np.mod(j-(test_idx+1),10) == 0:
#                pdb.set_trace()
                if (len(order[oidx])>1 ) & (not onedeflag):#((j- (test_idx+1)) <=80):
                    for ii in order[oidx]:
                        test_p = test_data[:,:] + np.atleast_2d((gt_data[ii][0,:]-test_data[test_idx,:]))
                        dist_p[ii], _ = fastdtw(gt_data[ii], test_p[test_idx:j,:], Jweight, dist=wt_euclidean)  
                        if (j == test_idx+1):
                            dpfirst[ii] = dist_p[ii]
                        else: # j > test_idx+1
                             print(dpfirst[ii] - dist_p[ii])
                             if (dpfirst[ii] - dist_p[ii])>2400:
                                 print('deflag on at moment '+str(ii))
#                                 pdb.set_trace()
                                 deflag_mul[ii] = True
                                 onedeflag = True
#                                 pdb.set_trace()
                                 
                    if onedeflag:#(j- (test_idx+1)) >=80: 


                        seg = []
                        for dekey in deflag_mul:
                            if deflag_mul[dekey] == True:
                                seg.append(dekey)
                        if len(seg)==1:
                            gt_idx = seg[0]
                        
                            print('movment is '+str(gt_idx))
                        else:  # len(seg) > 1:
                    
                            for ii in seg:
                                if minval>dist_p[ii]:
                                    minval = dist_p[ii] 
                                    minidx = ii
                            print('movment is '+str(minidx))
                            gt_idx =  minidx
                        deflag =  True  
                         
                        idxlist.append(gt_idx)
                        distp_prev  = dist_p[gt_idx]
                        dpfirst = dpfirst[gt_idx]

                      
                else:  
                    test_data_p  = test_data[:,:] + np.atleast_2d((gt_data[gt_idx][0,:]-test_data[test_idx,:]))
                    dist_p, _ = fastdtw(gt_data[gt_idx], test_data_p[test_idx:j,:], Jweight, dist=wt_euclidean)
    
                    if (j == test_idx+1):
                        dpfirst = dist_p
                    else: # j > test_idx+1
                        print(dpfirst - dist_p)
                        if (dpfirst - dist_p)>2400:
                            print('deflag on')
                            deflag = True
                            distp_prev  = dist_p
          
        else: 
            test_data_p  = test_data[:,:] + np.atleast_2d((gt_data[gt_idx][0,:]-test_data[test_idx,:]))
            dist_p, path_p = fastdtw(gt_data[gt_idx], test_data_p[test_idx:j,:], Jweight, dist=wt_euclidean)

            if chk_flag:  # in check global min status
                cnt +=1
               
                if dist_p < distp_cmp : # find another small value
                    cnt = 1

                    distp_cmp = dist_p
                    idx_cmp   = j
                    print(' ==== reset ====')
                    
                elif cnt == 20:

                    chk_flag = False

                    tgrad = 0

                    for ii in range(testlist.shape[1]):
                        tgrad += np.gradient(gf(testlist[:,ii],3))**2
                        
                    tgrad = tgrad**0.5

                    endidx = np.argmin(tgrad[idx_cmp-test_idx-10:idx_cmp-test_idx+10])+(idx_cmp-10) 
                    seglist.append([test_idx,endidx])                       
                    test_idx = endidx+1
                    cnt      = 0
                    oidx = gt_idx
                    segend = True
                    break
                
            else:  
                print dist_p-distp_prev
                
                if (dist_p-distp_prev)>0:
                    print (' ==============  large ====================')

                    distp_cmp = distp_prev
                    idx_cmp   = j
                    chk_flag = True
                    err      = []

            distp_prev  = dist_p 
        
            print ('===========\n')
     

    if cnt > 0:
       seglist.append([test_idx,idx_cmp]) 
       endidx =  idx_cmp
       test_idx = endidx+1
       oidx = gt_idx
    elif (j == (test_data.shape[0]-1))&(not segend) & (not deflag)  :
        
        if len(order[oidx])>1:
            # === no decrese happen 
            for i in  order[oidx]: 

                test_p = test_data[:,:] + np.atleast_2d((gt_data[i][0,:]-test_data[test_idx,:]))
                dist_p[i], _ = fastdtw(gt_data[i], test_p[test_idx:,:], Jweight, dist=wt_euclidean)                      
                if minval>dist_p[i]:
                    minval = dist_p[i] 
                    minidx = i  
                gt_idx =  minidx 
                idxlist.append(gt_idx)
        seglist.append([test_idx,len(test_data)-1]) 
        endidx = len(test_data)-1
        test_idx = endidx+1
    
        
    fig = plt.figure(1)
    plt.plot(test_data[:endidx,6]-500,color = 'red')
    plt.plot(test_data[:,6],color = 'blue')
    plt.title('matching')

    fig.savefig(str(len(seglist)).zfill(2)+'.jpg')
    plt.close(fig)
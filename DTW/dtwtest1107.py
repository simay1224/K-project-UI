# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 13:27:08 2017

@author: medialab
"""


import h5py
import cPickle
import pdb
import glob
import os
import numpy as np
from scipy.spatial.distance import _validate_vector
from w_fastdtw import fastdtw
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy.linalg import norm
from collections import defaultdict
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import argrelextrema

from dtw import Dtw

def wt_euclidean(u, v, w):
    u = _validate_vector(u)
    v = _validate_vector(v)
    dist = norm(w*(u - v))
    return dist

Jweight = np.array([0., 0., 0., 3., 3., 3., 9., 9., 9.,\
                    0., 0., 0., 3., 3., 3., 9., 9., 9.,\
                    0., 0., 0.])
Jweight = Jweight/sum(Jweight)*1.5

def clip(seqlist,LB=0):
    #LB : lower bound  
    tgrad = 0

    for ii in [3,4,5,6,7,8,12,13,14,15,16,17]: #maybe can include Jweight
        tgrad += (np.gradient(gf(seqlist[:,ii],1))**2 )*Jweight[ii]       
    tgrad = tgrad**0.5 
    lcalminm = argrelextrema(tgrad, np.less,order = 5)[0]
    # if j > 750:
    # pdb.set_trace()
    foo = np.where(((tgrad<1)*1)==0)[0]
    if (len(foo) == 0) | (len(lcalminm) == []):
        return []
    else:
        LB = max(foo[0],50)
        minm = []
        
        for ii in lcalminm[lcalminm>LB]:
            # pdb.set_trace()
            if tgrad[ii]<1:
                # pdb.set_trace()
                minm.append(ii)
        if len(minm)>1:
            pdb.set_trace()
        return minm


# def seg_update(Dtw, endidx):
#     if dtw.seglist == []:
#         dtw.seglist.append([dtw.seginidx, dtw.seginidx+endidx])
#         dtw.seginidx    = dtw.seginidx+endidx
#     else:
#         dtw.seglist.append([dtw.seginidx+1, dtw.seginidx+1+endidx])
#         dtw.seginidx    = dtw.seginidx+endidx+1
        
        
#     dtw.seqlist_reg = dtw.seqlist_reg[endidx+1:,] # update the seqlist
#     dtw.presv_size  = dtw.seqlist_reg.shape[0] 
#     dtw.cnt         = 0
#     dtw.oidx        = dtw.gt_idx
    
#     dtw.dpfirst     = {}   
#     dtw.dist_p      = {}   
#     dtw.deflag      = False
#     dtw.deflag_mul  = defaultdict(lambda:(bool(False)))                                        
#     dtw.onedeflag   = False                                  
#     dtw.segini      = True
#     dtw.segend      = True

#     return Dtw

data       = h5py.File('GT_V_data_mod_EX4.h5','r')
gt_data    = {}
gt_data[1] = data['GT_1'][:]
gt_data[2] = data['GT_2'][:]
gt_data[3] = data['GT_3'][:]
gt_data[4] = data['GT_4'][:]


# src_path  = './test data/ex4/'
src_path  = 'D:/AllData_0327(0712)/AllData_0327/unified data array/Unified_KData/'
#dst_path  = 'C:/Users/Dawnknight/Documents/GitHub/K_project/DTW/figure/0912/7 joints/'
#dst_path  = './figure/1016/7 joints Weight/'
dst_path  = './figure/EX4/'
#decTh     = 2000

order    = {}
order[0] = [1]
order[1] = [3]
order[2] = 'end'
order[3] = [4]
order[4] = [2, 3]


#AVGdist  ={}
#for i in order.keys():
#    AVGdist[i] = []

Color = ['red', 'blue', 'green', 'black', 'm']    



for infile in glob.glob(os.path.join(src_path,'*.pkl'))[:1]:
    print infile
    test_data    = cPickle.load(file(infile,'rb'))[12:,:].T
    test_data    = gf(test_data, 3, axis = 0)
#    test_data    = cPickle.load(file(infile,'rb')).T
    foldername   = infile.split('\\')[-1].split('_ex4')[0] 
    
    # if not os.path.exists(dst_path+foldername):
    #     os.makedirs(dst_path+foldername)
        
    # text_file = open(dst_path+foldername+"/"+foldername+"_log.txt", "w")   
    
    dtw = Dtw()
    j = 0  



    
#    for j in  range(test_data.shape[0]): 
    
        
    while not ((order[dtw.oidx] == 'end') | (j == (test_data.shape[0]-1))):
        print j
        # pdb.set_trace()
        dtw.matching2(test_data, j, gt_data)

        j=j+1

    if dtw.segend:
        pass
    else:
        dtw.seglist.append([dtw.seginidx+1,j]) 
        
        if (not dtw.deflag):
            if len(order[dtw.oidx])>1:
                # === no decrease happen  ===
                if dtw.seqlist[-1,7] <150:
                    minidx = 2
                else:
                    minidx = 3 
                # for i in  order[dtw.oidx]: 
    
                #     test_p = dtw.seqlist + np.atleast_2d((gt_data[i][0,:]-dtw.seqlist[0,:]))
                #     dtw.dist_p[i], _ = fastdtw(gt_data[dtw.gt_idx], test_p,Jweight, dist=wt_euclidean)                     
                    
                # minidx = min(dtw.dist_p, key = dtw.dist_p.get)
                dtw.gt_idx =  minidx 
                dtw.idxlist.append(dtw.gt_idx)
        
        elif (not dtw.chk_flag) | (dtw.cnt > 0):

            dtw.oidx = dtw.gt_idx   








    # print infile
    # print( dtw.idxlist)
    # print( dtw.seglist)
    # text_file.write(str(dtw.idxlist)+"\n\n")
    # text_file.write(str(dtw.seglist))
    # text_file.close() 

    # cnt = defaultdict(lambda: int(0))   
    # for jj in xrange(len(dtw.idxlist)): 
    #     print jj
    #     cnt[dtw.idxlist[jj]] += 1
    #     for i in xrange(21):
    #         fig = plt.figure(1)
    #         plt.plot(test_data[dtw.seglist[0][0]:dtw.seglist[jj][1],i]-500,color = 'red')
    #         plt.plot(test_data[:,i],color = 'blue')
    #         plt.title('matching _ coordinate number is : ' +str(i))
    #         subfolder = '/coordinate '+str(i)
    #         if not os.path.exists(dst_path+foldername+subfolder+'/matching/'):
    #             os.makedirs(dst_path+foldername+subfolder+'/matching/')
    #         if not os.path.exists(dst_path+foldername+subfolder+'/comparing/'):
    #             os.makedirs(dst_path+foldername+subfolder+'/comparing/')
    #         fig.savefig(dst_path+foldername+subfolder+'/matching/'+str(jj).zfill(2)+'.jpg')
    #         plt.close(fig)
    
    #         fig = plt.figure(1)
    #         offset = test_data[dtw.seglist[jj][0],i]-gt_data[dtw.idxlist[jj]][0,i]
    #         plt.plot(test_data[dtw.seglist[jj][0]:dtw.seglist[jj][1],i]-offset,color = 'red')
    #         plt.plot(gt_data[dtw.idxlist[jj]][:,i],color = 'Blue')
    #         plt.title(foldername + '\n comparing _ coordinate : ' +str(i)+' segment :'+str(dtw.idxlist[jj])+'-'\
    #                                 +str(cnt[dtw.idxlist[jj]]) )#+'\n avgsubdist :' + str(dtw.avgsubdist[i][-1]))
    #         fig.savefig(dst_path+foldername+subfolder+'/comparing/comparing w ground truth '+str(jj).zfill(2)+'.jpg')
    #         plt.close(fig)    

    # fig = plt.figure(1)
    # ax1 = fig.add_subplot(111)
    # tgrad = 0

    # for ii in [3, 4, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17]: 
    #     tgrad += (np.gradient(gf(test_data[:,ii], 1))**2 )*Jweight[ii]       
    # tgrad = tgrad**0.5 
    # plt.plot(tgrad, color = 'b')
    # tmp = np.array(dtw.seglist)[:,1]
    # plt.scatter(tmp, tgrad[tmp], color = 'r')
    # for ii in tmp:
    #     plt.axvline(x = ii, color = 'g')
    # plt.yticks(np.arange(20)/2.)
    # fig.savefig(dst_path+foldername+"/"+foldername+"_grad.jpg")
    # plt.close(fig)



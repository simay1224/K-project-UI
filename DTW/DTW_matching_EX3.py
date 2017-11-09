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


def seg_update(Dtw, endidx):
    if Dtw['seglist'] == []:
        Dtw['seglist'].append([Dtw['seginidx'], Dtw['seginidx']+endidx])
        Dtw['seginidx']    = Dtw['seginidx']+endidx
    else:
        Dtw['seglist'].append([Dtw['seginidx']+1, Dtw['seginidx']+1+endidx])
        Dtw['seginidx']    = Dtw['seginidx']+endidx+1
        
        
    Dtw['seqlist_reg'] = Dtw['seqlist_reg'][endidx+1:,] # update the seqlist
    Dtw['presv_size']  = Dtw['seqlist_reg'].shape[0] 
    Dtw['cnt']         = 0
    Dtw['oidx']        = Dtw['gt_idx']
    
    Dtw['dpfirst']     = {}   
    Dtw['dist_p']      = {}   
    Dtw['deflag']      = False
    Dtw['deflag_mul']  = defaultdict(lambda:(bool(False)))                                        
    Dtw['onedeflag']   = False                                  
    Dtw['segini']      = True
    Dtw['segend']      = True

    return Dtw

data       = h5py.File('GT_V_data_mod_EX4.h5','r')
gt_data    = {}
gt_data[1] = data['GT_1'][:]
gt_data[2] = data['GT_2'][:]
gt_data[3] = data['GT_3'][:]
gt_data[4] = data['GT_4'][:]


# src_path  = './test data/ex4/'
src_path  = 'D:/AllData_0327(0712)/AllData_0327/unified data array/Unified_KData/'
# src_path  = 'I:/AllData_0327/unified data array/Unified_KData/ex4/'
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
    test_data    = gf(test_data,3,axis = 0)
#    test_data    = cPickle.load(file(infile,'rb')).T
    foldername   = infile.split('\\')[-1].split('_ex4')[0] 
    
    if not os.path.exists(dst_path+foldername):
        os.makedirs(dst_path+foldername)
        
    text_file = open(dst_path+foldername+"/"+foldername+"_log.txt", "w")   
    

    # === initial setting ===
    Dtw                = {}
    Dtw['decTh']       = 1800
    Dtw['cnt']         = 0
    Dtw['distp_prev']  = 0         
    Dtw['distp_cmp']   = np.inf             
    Dtw['oidx']        = 0      # initail
    Dtw['gt_idx']      = 0 
    Dtw['presv_size']  = 0
    Dtw['idxlist']     = []   
    Dtw['idx_cmp']     = 0
    Dtw['fcnt']        = 0
    Dtw['seglist']     = []
    Dtw['Thcnt']       = 10     #threshold of cnt
    Dtw['serchLb']     = 20     # lower bound
    
    #
    Dtw['seginidx']    = 0
    Dtw['dpfirst']     = {}
    Dtw['dist_p']      = {}
    Dtw['deflag_mul']  = defaultdict(lambda:(bool(False)))  
    Dtw['seqlist']     = np.array([]) 
    Dtw['seqlist_reg'] = np.array([]) 
    Dtw['seqlist_gf']  = np.array([])                
    Dtw['dcnt']        = 0 
    Dtw['chk_flag']    = False
    Dtw['deflag']      = False   # decreasing flag
    Dtw['onedeflag']   = False
    Dtw['segini']      = True  
    j = 0  



    
#    for j in  range(test_data.shape[0]): 
    
        
    while not ((order[Dtw['oidx']] == 'end') | (j == test_data.shape[0]-1)):
        print j


        Dtw['segend']      = False 

        if Dtw['segini']:  # new segement/movement start
            Dtw['segini'] = False
            
            if (len(order[Dtw['oidx']])==1 ):
               Dtw['gt_idx'] = order[Dtw['oidx']][0]
               Dtw['idxlist'].append(Dtw['gt_idx']) 

        if len(Dtw['seqlist_reg']) == 0: #build sequence list            
            Dtw['seqlist_reg'] = test_data[j,:]
            Dtw['seqlist_reg'] = Dtw['seqlist_reg'].reshape(-1,21)
            Dtw['seqlist'] = Dtw['seqlist_reg']
        else:
            Dtw['seqlist_reg'] = np.vstack([Dtw['seqlist_reg'],test_data[j,:]])                
            Dtw['seqlist_gf'] = gf(Dtw['seqlist_reg'],3,axis = 0)

#            Dtw['seqlist'] = Dtw['seqlist_reg']
            Dtw['seqlist'] = Dtw['seqlist_gf']
        

            

        if not Dtw['deflag'] :
            if np.mod(Dtw['seqlist'].shape[0]-Dtw['presv_size']-1,10) == 0: # check every 10 frames

                if (len(order[Dtw['oidx']])>1 ):# & (not onedeflag):#((j- (test_idx+1)) <=60):
                    if Dtw['seqlist'].shape[0]>1:
                        result = clip(Dtw['seqlist'])
                        if result != []:
                            endidx = result[0]
                            if Dtw['seqlist'][endidx,7] <150:
                               minidx = 2
                            else:
                               minidx = 3 
                            # for ii in order[Dtw['oidx']]:
                            #     test_p = Dtw['seqlist'][:endidx,:] + np.atleast_2d((gt_data[ii][0,:]-Dtw['seqlist'][0,:]))
                            #     Dtw['dist_p'][ii], _ = fastdtw(gt_data[ii], test_p,Jweight, dist=wt_euclidean)
                            # minidx = min(Dtw['dist_p'], key = Dtw['dist_p'].get)   



                            Dtw['gt_idx'] =  minidx
                            Dtw['idxlist'].append(Dtw['gt_idx'])
                            Dtw.update(seg_update(Dtw, endidx))
                else:  
                    test_data_p  = Dtw['seqlist'] + np.atleast_2d((gt_data[Dtw['gt_idx']][0,:]-Dtw['seqlist'][0,:]))
                    Dtw['dist_p'], _ = fastdtw(gt_data[Dtw['gt_idx']], test_data_p,Jweight, dist=wt_euclidean)
                    
                    if (Dtw['seqlist'].shape[0] == 1+Dtw['presv_size']): # new movement initail setting

                        Dtw['dpfirst'],_ = fastdtw(gt_data[Dtw['gt_idx']], test_data_p[:2],Jweight, dist=wt_euclidean)   
                        
                        print('dpfirst is : %f' %Dtw['dpfirst'])
                    else: 
                        print('de diff is :%f' %(Dtw['dpfirst'] - Dtw['dist_p']))
                    
                        if (Dtw['dpfirst'] - Dtw['dist_p'])>Dtw['decTh']:
                            print('=========')
                            print('deflag on')
                            print('=========')
                            Dtw['deidx']       = Dtw['seqlist_reg'].shape[0]
                            Dtw['deflag']      = True
                            Dtw['distp_prev']  = Dtw['dist_p']   
          
        else: 
            test_data_p  = Dtw['seqlist'] + np.atleast_2d((gt_data[Dtw['gt_idx']][0,:]-Dtw['seqlist'][0,:]))
            Dtw['dist_p'], path_p = fastdtw(gt_data[Dtw['gt_idx']], test_data_p,Jweight, dist=wt_euclidean) 
                
            if Dtw['chk_flag']:  # in check global min status
                Dtw['cnt'] +=1
               
                if Dtw['dist_p'] < Dtw['distp_cmp'] : # find smaller value
                    Dtw['cnt'] = 1

                    Dtw['distp_cmp'] = Dtw['dist_p']
                    Dtw['idx_cmp']   = Dtw['seqlist'].shape[0]
                    print(' ==== reset ====')
                    
                elif Dtw['cnt'] == Dtw['Thcnt']:
                    
                    Dtw['evalstr']  = 'Well done'
                    Dtw['chk_flag'] = False   
                    tgrad = 0

                    for ii in range(Dtw['seqlist'].shape[1]): #maybe can include Jweight
                        tgrad += np.gradient(gf(Dtw['seqlist'][:,ii],3))**2
                        
                    tgrad = tgrad**0.5    
                    endidx = np.argmin(tgrad[Dtw['idx_cmp']-Dtw['serchLb']:Dtw['idx_cmp']+Dtw['Thcnt']-1])+(Dtw['idx_cmp']-Dtw['serchLb'])

                    Dtw.update(seg_update(Dtw, endidx))
            else:  
                                                  
                if (Dtw['dist_p']-Dtw['distp_prev'])>0: #turning point
                    print (' ==============  large ====================')

                    Dtw['distp_cmp'] = Dtw['distp_prev']
                    Dtw['idx_cmp']   = Dtw['seqlist'].shape[0]
                    Dtw['chk_flag'] = True
        
            Dtw['distp_prev']  = Dtw['dist_p'] 

            print ('===========\n')
        j=j+1
            
    if Dtw['segend']:
        pass
    else:
        Dtw['seglist'].append([Dtw['seginidx']+1,j]) 
        
        if (not Dtw['deflag']):
            if len(order[Dtw['oidx']])>1:
                # === no decrease happen  ===
                if Dtw['seqlist'][-1,7] <150:
                    minidx = 2
                else:
                    minidx = 3 
                # for i in  order[Dtw['oidx']]: 
    
                #     test_p = Dtw['seqlist'] + np.atleast_2d((gt_data[i][0,:]-Dtw['seqlist'][0,:]))
                #     Dtw['dist_p'][i], _ = fastdtw(gt_data[Dtw['gt_idx']], test_p,Jweight, dist=wt_euclidean)                     
                    
                # minidx = min(Dtw['dist_p'], key = Dtw['dist_p'].get)
                Dtw['gt_idx'] =  minidx 
                Dtw['idxlist'].append(Dtw['gt_idx'])
        
        elif (not Dtw['chk_flag']) | (Dtw['cnt'] > 0):

            Dtw['oidx'] = Dtw['gt_idx']   
    # print infile
    # print( Dtw['idxlist'])
    # print( Dtw['seglist'])
    # text_file.write(str(Dtw['idxlist'])+"\n\n")
    # text_file.write(str(Dtw['seglist']))
    # text_file.close() 

    # cnt = defaultdict(lambda: int(0))   
    # for jj in xrange(len(Dtw['idxlist'])): 
    #     print jj
    #     cnt[Dtw['idxlist'][jj]] += 1
    #     for i in xrange(21):
    #         fig = plt.figure(1)
    #         plt.plot(test_data[Dtw['seglist'][0][0]:Dtw['seglist'][jj][1],i]-500,color = 'red')
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
    #         offset = test_data[Dtw['seglist'][jj][0],i]-gt_data[Dtw['idxlist'][jj]][0,i]
    #         plt.plot(test_data[Dtw['seglist'][jj][0]:Dtw['seglist'][jj][1],i]-offset,color = 'red')
    #         plt.plot(gt_data[Dtw['idxlist'][jj]][:,i],color = 'Blue')
    #         plt.title(foldername + '\n comparing _ coordinate : ' +str(i)+' segment :'+str(Dtw['idxlist'][jj])+'-'\
    #                                 +str(cnt[Dtw['idxlist'][jj]]) )#+'\n avgsubdist :' + str(Dtw['avgsubdist'][i][-1]))
    #         fig.savefig(dst_path+foldername+subfolder+'/comparing/comparing w ground truth '+str(jj).zfill(2)+'.jpg')
    #         plt.close(fig)    

    # fig = plt.figure(1)
    # ax1 = fig.add_subplot(111)
    # tgrad = 0

    # for ii in [3, 4, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17]: 
    #     tgrad += (np.gradient(gf(test_data[:,ii], 1))**2 )*Jweight[ii]       
    # tgrad = tgrad**0.5 
    # plt.plot(tgrad, color = 'b')
    # tmp = np.array(Dtw['seglist'])[:,1]
    # plt.scatter(tmp, tgrad[tmp], color = 'r')
    # for ii in tmp:
    #     plt.axvline(x = ii, color = 'g')
    # plt.yticks(np.arange(20)/2.)
    # fig.savefig(dst_path+foldername+"/"+foldername+"_grad.jpg")
    # plt.close(fig)



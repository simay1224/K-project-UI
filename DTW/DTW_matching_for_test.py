# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 15:45:29 2017

@author: medialab
"""



import h5py,cPickle,pdb,glob,os
import numpy as np
from scipy.spatial.distance import _validate_vector
from w_fastdtw import fastdtw
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy.linalg import norm
from collections import defaultdict
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema


def wt_euclidean(u,v,w):
    u = _validate_vector(u)
    v = _validate_vector(v)
    dist = norm(w*(u - v))
    return dist



Jweight = np.array([0., 0., 0., 3., 3., 3., 9., 9., 9.,\
                    0., 0., 0., 3., 3., 3., 9., 9., 9.,\
                    0., 0., 0.])
Jweight = Jweight/sum(Jweight)*1.5

def clip(seqlist):
    tgrad = 0
    for ii in [3,4,5,6,7,8,12,13,14,15,16,17]: #maybe can include Jweight
        tgrad += (np.gradient(gf(seqlist[:,ii],5))**2 )*Jweight[ii]       
    tgrad = tgrad**0.5 
    
    minm = argrelextrema(tgrad, np.less,order = 10)[0]
    
    return minm


#data       = h5py.File('GT_V_data_mod_EX4.h5','r')
#gt_data    = {}
#gt_data[1] = data['GT_1'][:]
#gt_data[2] = data['GT_2'][:]
#gt_data[3] = data['GT_3'][:]
#gt_data[4] = data['GT_4'][:]

data       = h5py.File('GT_kinect_EX4_40_40_40.h5','r')
gt_data    = {}
gt_data[1] = data['GT_kinect_1'][:]
gt_data[2] = data['GT_kinect_2'][:]
gt_data[3] = data['GT_kinect_3'][:]
gt_data[4] = data['GT_kinect_4'][:]



#src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'
#src_path  = 'D:/Project/K_project/data/unified data array/Unified_MData/'
src_path  = 'D:/Project/K_project/DTW/test data/'

#dst_path  = 'C:/Users/Dawnknight/Documents/GitHub/K_project/DTW/figure/0912/7 joints/'
dst_path  = './figure/1016/7 joints Weight/'

#decTh     = 2000

order    = {}
order[0] = [1]
order[1] = [3]
order[2] = 'end'
order[3] = [4]
order[4] = [2,3]

#AVGdist  ={}
#for i in order.keys():
#    AVGdist[i] = []

Color = ['red','blue','green','black','m']    



for infile in glob.glob(os.path.join(src_path,'*.pkl'))[3:]:
    print infile
    test_data    = cPickle.load(file(infile,'rb'))[12:,:].T
#    test_data    = cPickle.load(file(infile,'rb')).T
    foldername   = infile.split('\\')[-1].split('_ex4')[0][:-3]  
    
    if not os.path.exists(dst_path+foldername):
        os.makedirs(dst_path+foldername)
        
#    text_file = open(dst_path+foldername+"/"+foldername+"_log.txt", "w")    

    # === initial setting ===
    Dtw                = {}
    Dtw['decTh']       = 2000
    Dtw['cnt']         = 0
    Dtw['distp_prev']  = 0         
    Dtw['distp_cmp']   = np.inf             
    Dtw['presv_size']  = 0
    Dtw['idxlist']     = []   
    Dtw['idx_cmp']     = 0
    Dtw['fcnt']        = 0
    Dtw['seglist']     = []
    Dtw['deidx']       = {}    # decrease index 
    Dtw['Thcnt']       = 10
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
    
    
    
    # tunable parameter
    j                  = 271
    Dtw['seginidx']    = j
    Dtw['oidx']        = 3      # initail
    Dtw['gt_idx']      = 3 

        
    while not ((order[Dtw['oidx']] == 'end') | (j == 400)):#(test_data.shape[0]-1))):
        print j
        Dtw['segend']      = False 

        if Dtw['segini']:  # new segement/movement start
            Dtw['segini'] = False
            
            if (len(order[Dtw['oidx']])==1 ):
               Dtw['gt_idx'] = order[Dtw['oidx']][0]
               Dtw['idxlist'].append(Dtw['gt_idx']) 

#        pdb.set_trace()
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
                    for ii in order[Dtw['oidx']]:

                        test_p = Dtw['seqlist'] + np.atleast_2d((gt_data[ii][0,:]-Dtw['seqlist'][0,:]))
                        Dtw['dist_p'][ii], _ = fastdtw(gt_data[ii], test_p,Jweight, dist=wt_euclidean)

                        if (Dtw['seqlist'].shape[0] == 1+Dtw['presv_size']): # new movement initail setting
                             Dtw['dpfirst'][ii], _ = fastdtw(gt_data[Dtw['gt_idx']], test_p[:2],Jweight, dist=wt_euclidean)
                        else: 
                             print('%s : ' %ii)
                             print('%.2f \n'   %(Dtw['dpfirst'][ii] - Dtw['dist_p'][ii]))
                             if (Dtw['dpfirst'][ii] - Dtw['dist_p'][ii])>Dtw['decTh']:
                                 print('deflag on')
                                 Dtw['deflag_mul'][ii] = True
                                 Dtw['deidx'][ii] = j
                                 Dtw['onedeflag'] = True  
                                 
                    if Dtw['onedeflag']:#(j- (test_idx+1)) >=60:   # compare the dist_p to decide which movement it is. 
                                                            #(may need further modification when doing muilti-ex)
                        seg = []
                        for dekey in Dtw['deflag_mul']:
                            if Dtw['deflag_mul'][dekey] == True:
                                seg.append(dekey)
                        if len(seg)==1: # only 1 movement is decreasing
                            Dtw['gt_idx'] = seg[0]
                        
                            print('movment is '+str(Dtw['gt_idx']))
                        else:  # len(seg) > 1:
                    
                            minidx = min(Dtw['dist_p'], key = Dtw['dist_p'].get)
                            
                            print('movment is '+str(minidx))
                            Dtw['gt_idx'] =  minidx
                        Dtw['deflag'] =  True  
                         
                        Dtw['idxlist'].append(Dtw['gt_idx'])
                        Dtw['distp_prev'] = Dtw['dist_p'][Dtw['gt_idx']]
                        Dtw['dpfirst']    = Dtw['dpfirst'][Dtw['gt_idx']]
                        Dtw['deidx']      = Dtw['deidx'][minidx]
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
                            Dtw['deflag']      = True
                            Dtw['distp_prev']  = Dtw['dist_p']   
                            Dtw['deidx']       = j
          
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
                    endidx = np.argmin(tgrad[Dtw['idx_cmp']-10:Dtw['idx_cmp']+Dtw['Thcnt']-1])+(Dtw['idx_cmp']-10) 
       
                    
                    if Dtw['seglist'] == []:
                        Dtw['seglist'].append([Dtw['seginidx'],Dtw['seginidx']+endidx])
                        Dtw['seginidx']    = Dtw['seginidx']+endidx
                    else:
                        Dtw['seglist'].append([Dtw['seginidx']+1,Dtw['seginidx']+1+endidx])
                        Dtw['seginidx']    = Dtw['seginidx']+endidx+1
                        
                    Dtw['seqlist_reg'] = Dtw['seqlist_reg'][endidx+1:,] # update the seqlist
                    Dtw['presv_size']  = Dtw['seqlist_reg'].shape[0] 
                    Dtw['cnt']         = 0
                    Dtw['oidx']        = Dtw['gt_idx']
                    Dtw['deidx']       = {}
                    
                    Dtw['dpfirst']     = {}   
                    Dtw['dist_p']      = {}   
                    Dtw['deflag']      = False
                    Dtw['deflag_mul']  = defaultdict(lambda:(bool(False)))                                        
                    Dtw['onedeflag']   = False                                  
                    Dtw['segini']      = True
                    Dtw['segend']      = True
              
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
                for i in  order[Dtw['oidx']]: 
    
                    test_p = Dtw['seqlist'] + np.atleast_2d((gt_data[i][0,:]-Dtw['seqlist'][0,:]))
                    Dtw['dist_p'][i], _ = fastdtw(gt_data[Dtw['gt_idx']], test_p,Jweight, dist=wt_euclidean)                     
                    
                minidx = min(Dtw['dist_p'], key = Dtw['dist_p'].get)
                Dtw['gt_idx'] =  minidx 
                Dtw['idxlist'].append(Dtw['gt_idx'])
        
        elif (not Dtw['chk_flag']) | (Dtw['cnt'] > 0):

            Dtw['oidx'] = Dtw['gt_idx']   
            

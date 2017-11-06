# -*- coding: utf-8 -*-
"""
Created on Tue Oct 03 14:52:09 2017

@author: medialab
"""
from scipy.spatial.distance import _validate_vector
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy.linalg import norm
from collections import defaultdict
from w_fastdtw import fastdtw
import numpy as np 

def wt_euclidean(u,v,w):
    u = _validate_vector(u)
    v = _validate_vector(v)
    dist = norm(w*(u - v))
    return dist

order    = {}
order[0] = [1]
order[1] = [3]
order[2] = 'end'
order[3] = [4]
order[4] = [2,3]

Jweight = np.array([0., 0., 0., 3., 3., 3., 9., 9., 9.,\
                    0., 0., 0., 3., 3., 3., 9., 9., 9.,\
                    0., 0., 0.])
Jweight = Jweight/sum(Jweight)*1.5

def DTW_matching(Dtw,reconJ,gt_data):
    if not (order[Dtw['oidx']] == 'end'):
        
        if Dtw['segini']:  # new segement/movement start
            Dtw['segini'] = False
            if (len(order[Dtw['oidx']])==1 ):
                Dtw['gt_idx'] = order[Dtw['oidx']][0]
                Dtw['idxlist'].append(Dtw['gt_idx']) 
            
        if len(Dtw['seqlist']) == 0: #build sequence list
            Dtw['seqlist'] = reconJ
            Dtw['seqlist'] = Dtw['seqlist'].reshape(-1,21)
        else:
            Dtw['seqlist'] = np.vstack([Dtw['seqlist'],reconJ])
            Dtw['seqlist'] = gf(Dtw['seqlist'],3,axis = 0)
            
        if not Dtw['deflag']: # Not yet decreasing

            if np.mod(Dtw['seqlist'].shape[0]-Dtw['presv_size']-1,10) == 0: # check every 10 frames    
                if (len(order[Dtw['oidx']])>1 ) :#& (not Dtw['onedeflag']): # if candidate more than 1 and not anyone is decreasing
                    for ii in order[Dtw['oidx']]:
                        test_p = Dtw['seqlist'] + np.atleast_2d((gt_data[ii][0,:]-Dtw['seqlist'][0,:]))
                        Dtw['dist_p'][ii], _ = fastdtw(gt_data[ii], test_p,Jweight, dist=wt_euclidean)
                        
                        if (Dtw['seqlist'].shape[0] == 1+Dtw['presv_size']): # new movement initail setting
#                            if Dtw['presv_size'] != 0:  # seglist contains some previous joints data
#                                # compare the DTW btw Gt and first two row in test_p to get the dpfirst
#                                Dtw['dist_p'][ii], _ = fastdtw(gt_data[Dtw['gt_idx']], test_p[:2],Jweight, dist=wt_euclidean)
#                                
#                            Dtw['dpfirst'][ii] = Dtw['dist_p'][ii]
                            Dtw['dpfirst'][ii], _ = fastdtw(gt_data[Dtw['gt_idx']], test_p[:2],Jweight, dist=wt_euclidean)
                        else: 
                             if (Dtw['dpfirst'][ii] - Dtw['dist_p'][ii])>Dtw['decTh']:
                                 print('deflag on')
                                 Dtw['deflag_mul'][ii] = True
                                 Dtw['onedeflag'] = True             
                                 
                    if Dtw['onedeflag']:# at least one DTW value of candidate movements is decreasing    
                                                                  
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
                        Dtw['distp_prev']  = Dtw['dist_p'][Dtw['gt_idx']]
                        Dtw['dpfirst'] = Dtw['dpfirst'][Dtw['gt_idx']]
                        
                else:  
                    test_data_p  = Dtw['seqlist'] + np.atleast_2d((gt_data[Dtw['gt_idx']][0,:]-Dtw['seqlist'][0,:]))
                    Dtw['dist_p'], _ = fastdtw(gt_data[Dtw['gt_idx']], test_data_p,Jweight, dist=wt_euclidean)
                    
                    if (Dtw['seqlist'].shape[0] == 1+Dtw['presv_size']): # new movement initail setting
                           
#                        if Dtw['presv_size'] != 0:  # seglist contains some previous joints data
#                            # compare the DTW btw Gt and first two row in test_p to get the dpfirst
#                        Dtw['dist_p'], _ = fastdtw(gt_data[Dtw['gt_idx']], test_data_p[:2],Jweight, dist=wt_euclidean)                            
#                        Dtw['dpfirst'] = Dtw['dist_p'] 
                        Dtw['dpfirst'],_ = fastdtw(gt_data[Dtw['gt_idx']], test_data_p[:2],Jweight, dist=wt_euclidean)   
                        
                        print('dpfirst is : %f' %Dtw['dpfirst'])
                    else: 
                        print('de diff is :%f' %(Dtw['dpfirst'] - Dtw['dist_p']))
                    
                        if (Dtw['dpfirst'] - Dtw['dist_p'])>Dtw['decTh']:
                            print('=========')
                            print('deflag on')
                            print('=========')
                            Dtw['deflag'] = True
                            Dtw['distp_prev']  = Dtw['dist_p']                                    
 
                            
        else: # already start decreasing
            test_data_p  = Dtw['seqlist'] + np.atleast_2d((gt_data[Dtw['gt_idx']][0,:]-Dtw['seqlist'][0,:]))
            Dtw['dist_p'], path_p = fastdtw(gt_data[Dtw['gt_idx']], test_data_p,Jweight, dist=wt_euclidean)                                    
    
            if Dtw['chk_flag']:  # in check global min status
                Dtw['cnt'] +=1
               
                if Dtw['dist_p'] < Dtw['distp_cmp'] : # find smaller value
                    Dtw['cnt'] = 1

                    Dtw['distp_cmp'] = Dtw['dist_p']
                    Dtw['idx_cmp']   = Dtw['seqlist'].shape[0]
                    print(' ==== reset ====')
                    
                elif Dtw['cnt'] == 20:
                    
                    Dtw['evalstr']  = 'Well done'
                    Dtw['chk_flag'] = False   
                    tgrad = 0

                    for ii in range(Dtw['seqlist'].shape[1]): #maybe can include Jweight
                        tgrad += np.gradient(gf(Dtw['seqlist'][:,ii],3))**2
                        
                    tgrad = tgrad**0.5    
                    endidx = np.argmin(tgrad[Dtw['idx_cmp']-10:Dtw['idx_cmp']+19])+(Dtw['idx_cmp']-10) 
       
                    # update or reset dtw parameter
#                    if Dtw['gt_idx'] == 4:
#                       Dtw['periodcnt'] += 1
                    Dtw['seqlist'] = Dtw['seqlist'][endidx+1:,] # update the seqlist
                    Dtw['presv_size'] =Dtw['seqlist'].shape[0] 
                    Dtw['cnt']     = 0
                    Dtw['oidx'] = Dtw['gt_idx']
                    
                    Dtw['dpfirst']     = {}   
                    Dtw['dist_p']      = {}   
                    Dtw['deflag']      = False
                    Dtw['deflag_mul']  = defaultdict(lambda:(bool(False)))                                        
                    Dtw['onedeflag']   = False                                  
                    Dtw['segini']      = True
                    
              
            else:  
                                                  
                if (Dtw['dist_p']-Dtw['distp_prev'])>0: #turning point
                    print (' ==============  large ====================')

                    Dtw['distp_cmp'] = Dtw['distp_prev']
                    Dtw['idx_cmp']   = Dtw['seqlist'].shape[0]
                    Dtw['chk_flag'] = True
        
            Dtw['distp_prev']  = Dtw['dist_p'] 
                                                  
    else:
        print('================= exe END ======================')
        Dtw['exechk'] = False    
        
    return Dtw
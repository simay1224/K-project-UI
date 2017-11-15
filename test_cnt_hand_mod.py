# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 13:27:08 2017

@author: medialab
"""


import h5py,cPickle,pdb,glob,os
import numpy as np
from scipy.spatial.distance import _validate_vector
from w_fastdtw import fastdtw
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy import signal
from scipy.linalg import norm
from collections import defaultdict
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter as gf_2D
import cv2


def wt_euclidean(u,v,w):
    u = _validate_vector(u)
    v = _validate_vector(v)
    dist = norm(w*(u - v))
    return dist

Jweight = np.array([0., 0., 0., 3., 3., 3., 9., 9., 9.,\
                    0., 0., 0., 3., 3., 3., 9., 9., 9.,\
                    0., 0., 0.])
Jweight = Jweight/sum(Jweight)*1.5
Joi_ID = [1,4,20,8]


data       = h5py.File('GT_V_data_mod_EX2_seg_2.h5','r')
gt_data    = {}
gt_data[1] = data['GT_1'][:]
gt_data[2] = data['GT_2'][:]



src_path    = './output/test/file/'
hand_path   = './output/test/hand/'
breath_path = './output/test/file/'
#dst_path  = 'C:/Users/Dawnknight/Documents/GitHub/K_project/DTW/figure/0912/7 joints/'
#dst_path  = './figure/1016/7 joints Weight/'
dst_path  = './figure/'
#decTh     = 2000

order    = {}
order[0] = [1]
order[1] = [2]
order[2] = 'end'

#AVGdist  ={}
#for i in order.keys():
#    AVGdist[i] = []

Color = ['red','blue','green','black','m']    


for infile, hand_file, breath_file in zip(glob.glob(os.path.join(src_path, '*.pkl')),\
                                          glob.glob(os.path.join(hand_path,'*.pkl')),\
                                          glob.glob(os.path.join(breath_path,'*.h5'))):
    print infile
    test_data    = cPickle.load(file(infile,'rb'))[12:,:].T
    hand_data    = cPickle.load(file(hand_file,'rb'))
    breath_h5    = h5py.File(breath_file,'r')

    joi_list = []
    for frame_num in xrange(len(hand_data)):
        joi_list_1frame = []
        for joi_N in Joi_ID:
            X = hand_data[frame_num]['depth_jointspts'][joi_N].x
            Y = hand_data[frame_num]['depth_jointspts'][joi_N].y
            joi_list_1frame.append([int(X),int(Y)])
        joi_list.append(joi_list_1frame)

    depth_data =[] 
    for frame_num in xrange(test_data.shape[0]):
        map_ID         = 'd_'+'{0:04}'.format(frame_num)
        depth_map      = breath_h5['imgs']['dimgs'][map_ID][:]
        X_b            = [joi_list[frame_num][1][0] , joi_list[frame_num][3][0]]
        Y_b            = [joi_list[frame_num][2][1] , joi_list[frame_num][0][1]]
        depth_data.append([depth_map,X_b,Y_b])               # depth data read


    foldername   = infile.split('\\')[-1].split('_ex2')[0][:-3]  
    if not os.path.exists(dst_path+foldername):
        os.makedirs(dst_path+foldername)
           

    # === initial setting ===
    Dtw                = {}
    Dtw['decTh']       = 2000
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
    Dtw['serchLb']     = 10     # lower bound
    
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
    #=====================================#
    Dtw['hold']        = [False,True]   # the flag using for hold the state
    Dtw['hold_list']   = np.array([])   # save hold coordinate data when holding
    Dtw['cnt_hand']    = [0,0]          # the first is the number of close hand,
    Dtw['hand_list']   = np.array([])
    Dtw['breath_first'] = np.array([])
    Dtw['mask']        = np.zeros((424,512))
    Dtw['breath_list'] = np.array([])   # using for saving breath data
    Dtw['breath_list1'] = np.array([])
    Dtw['hcnt']        = 0              # count the number of hold frames
    #=====================================#
    j = 0
    open_cnt_list  = []   
    close_cnt_list = [] 
    hold_change    = []

    while not ((order[Dtw['oidx']] == 'end') | (j == (test_data.shape[0]-1))):
        print j
#===============================================================================#
        if order[Dtw['oidx']] == [2]:                                # comepare data with the first read frame (hand up frame) 
            Dtw['hold'][0] = True                                    # if there is a huge change the DTW will one and move to the hand down step
        if (Dtw['hold'][0] == True) and (Dtw['hold'][1]==True) :
            Dtw['hcnt'] += 1      
            if len(Dtw['hold_list']) == 0:
                Dtw['hold_list'] = test_data[j,:].reshape(-1,21)
            else:
                Dtw['hold_list'] = np.vstack((Dtw['hold_list'],test_data[j,:]))
            #========================= read breath data in

            if len(Dtw['breath_list']) == 0:
                Dtw['breath_first'] = depth_data[j]             # save the first frame of the depth data
                Dtw['breath_list']  = np.array([0.0])
                                                                # depth_data[0] is the depth map data. depth_data[1] is two X coordinate
                                                                # depth_data[2] is the list of two Y coordinate
                                                                
            else:                                               # get the bound of  current mask
                cur_bound = [[max(depth_data[j][1][0],Dtw['breath_first'][1][0]),min(depth_data[j][1][1],Dtw['breath_first'][1][1])],\
                             [max(depth_data[j][2][0],Dtw['breath_first'][2][0]),min(depth_data[j][2][1],Dtw['breath_first'][2][1])]]
                

                ref_dblk = gf_2D(Dtw['breath_first'][0][cur_bound[0][0]:cur_bound[0][1],cur_bound[1][0]:cur_bound[1][1]],5)
                cur_dblk = gf_2D(depth_data[j][0][cur_bound[0][0]:cur_bound[0][1],cur_bound[1][0]:cur_bound[1][1]],5)

                Dtw['breath_list'] = np.hstack((Dtw['breath_list'],np.mean(np.abs(cur_dblk-ref_dblk))))

            Dtw['breath_list'] = gf(Dtw['breath_list'],1)

            Dtw['hold_list'] = gf(Dtw['hold_list'],5,axis = 0)
            #========================= read hand data in
            data_L = hand_data[j]['LHS'] 
            data_R = hand_data[j]['RHS']

            if data_L == 4: # lasso left
                data_L = 0
            if data_R == 4: # lasso right
                data_R = 0
            if (data_L == 0 or data_L == 1 ) and (data_R == 2 or data_R == 3): # if left hand is no tracking , using right
                data_L = data_R
            if (data_R == 0 or data_R == 1 ) and (data_L == 2 or data_L == 3): # if right hand is no tracking , using left
                data_R = data_L
            if data_L == 0:                                                    # if all lose (for left)
                if len(Dtw['hand_list'])==0:                                   # all lose and hand is the first frame
                    data_L = 2                                                 # using open   
                else:
                    data_L = Dtw['hand_list'][-1,0]                            # using previous frame
            if data_R == 0:                                                    
                if len(Dtw['hand_list'])==0:                                   # if all lose (for right)
                    data_R = 2
                else:
                    data_R = Dtw['hand_list'][-1,1]
            
            hand_frame = np.array([data_L,data_R])                    

            if len(Dtw['hand_list']) == 0:                                     # write hand frame into Dtw dictionary
                Dtw['hand_list'] = hand_frame.reshape(-1,2)
            else:
                Dtw['hand_list'] = np.vstack((Dtw['hand_list'],hand_frame))

            hold_change=np.sum(np.abs(Dtw['hold_list'][0]-Dtw['hold_list'][-1]))
            if hold_change>400:                                                # if there is a huge change go to DTW step
                Dtw['hold'][1] = False
            # hand_change    = Dtw['hand_list'] - np.roll(Dtw['hand_list'],-1, axis = 0)
            # if np.mod(Dtw['hcnt'],5) == 0:                                     # check open and close in every n frames
            #     hand_chg = hand_change[-6:-1,0]+hand_change[-6:-1,1]
            #     print(hand_chg)
            #     if np.sum(hand_chg) == 2:                                      # hand open to hand close change
            #         open_cnt_list.append(Dtw['hcnt'])
            #         Dtw['cnt_hand'][0] += 1
            #     if np.sum(hand_chg) == -2:                                     # hand close to hand open change
            #         close_cnt_list.append(Dtw['hcnt'])
            #         Dtw['cnt_hand'][1] += 1

            #     if np.sum(hand_chg) == 1:                                      # if only one hand close
            #         if np.sum(hand_chg[0]) ==1 and np.sum(hand_chg[1]) == 0 :
            #             print('please open your left hand')
            #         if np.sum(hand_chg[1]) ==1 and np.sum(hand_chg[0]) == 0 :
            #             print('please open your right hand')

            #     if np.sum(hand_chg) == -1:                                     # if only one hand open
            #         if np.sum(hand_chg[0]) == -1 and np.sum(hand_chg[1]) == 0 :
            #             print('please close your left hand')
            #         if np.sum(hand_chg[1]) == -1 and np.sum(hand_chg[0]) == 0 :
            #             print('please close your right hand')

#===============================================================================#
        if (Dtw['hold'][0] == False) or (Dtw['hold'][1] == False):
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
                                     Dtw['onedeflag'] = True 
    #                                 Dtw['deidx'][ii] = Dtw['seqlist_reg'].shape[0]
                                     
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
                            Dtw['distp_prev']  = Dtw['dist_p'][Dtw['gt_idx']]
                            Dtw['dpfirst']     = Dtw['dpfirst'][Dtw['gt_idx']]
    #                        Dtw['deidx']       = Dtw['deidx'][minidx]
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
                        try:
                            endidx = np.argmin(tgrad[Dtw['idx_cmp']-Dtw['serchLb']:Dtw['idx_cmp']+Dtw['Thcnt']-1])+(Dtw['idx_cmp']-Dtw['serchLb'])
                        except:
                            pdb.set_trace()
                            endidx = test_data.shape[0]
                        
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

    
    #===================================================================================#           
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
#===============================================================================================#


    # hand_open_flag       = [False,False]
    # hand_cnt        = 0
    Dtw['hand_list'] = signal.medfilt(Dtw['hand_list'], kernel_size=3)
    if np.sum(Dtw['hand_list'][0]) != 4: 
        Dtw['hand_list'][:10] = 2
    if np.sum(Dtw['hand_list'][-1])!= 4: 
        Dtw['hand_list'][-10:] = 2
    pdb.set_trace()
    hand_change     = (Dtw['hand_list'] - np.roll(Dtw['hand_list'],-1, axis = 0))[:-1]
    l_open_idx      = np.where(hand_change[:,0] == 1)[0]  # find the left open index
    r_open_idx      = np.where(hand_change[:,1] == 1)[0]  # find the right open index
    l_close_idx     = np.where(hand_change[:,0] == -1)[0] # find the left close index
    r_close_idx     = np.where(hand_change[:,1] == -1)[0] # find the right close index
    cnt_open        = 0
    cnt_close       = 0
    hand_seg        = []

    if len(l_open_idx)>len(r_open_idx):
        for i in l_open_idx:
            right_state = hand_change[i-5:i+5,1]
            if np.sum(right_state) == 1:
                cnt_open += 1
                print('both hand open at frame'+str(i))
            else: 
                print('please open right')
    else:
        for i in r_open_idx:
            left_state = hand_change[i-5:i+5,0]
            if np.sum(left_state) == 1:
                cnt_open += 1
                print('both hand open at frame'+str(i))
            else: 
                print('please open left')

    if len(l_close_idx)>len(r_close_idx):
        for i in l_close_idx[:]:
            right_state = hand_change[i-5:i+5,1]
            if np.sum(right_state) == -1:
                cnt_close += 1
                print('both hand close at frame'+str(i))
            else:
                print('please close right')
    else:
        for i in r_close_idx:
            left_state = hand_change[i-5:i+5,0]
            if np.sum(left_state) == -1:
                cnt_close += 1
                print('both hand close at frame'+str(i))
            else: 
                print('please close left')
        

    print('open '+str(cnt_open)+'    close ' +str(cnt_close))

    # plot the state of hold section

    breath_chg_list = np.gradient(Dtw['breath_list'][:])
    breath_chg_list[breath_chg_list>0]  = 1
    breath_chg_list[breath_chg_list<0]  = 0
    breath_chg = breath_chg_list[:-2]-np.roll(breath_chg_list,-1)[:-2]

    plt.plot((Dtw['breath_list'][:]-Dtw['breath_list'][0])/1000,label = 'depth of chest')
    plt.plot(Dtw['hand_list'][:,0],label = 'left hand state')
    plt.plot(Dtw['hand_list'][:,1],label = 'right hand state')
    plt.legend()
    plt.title('hand and breath state of '+foldername)
    plt.show()
        




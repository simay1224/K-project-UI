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
dst_path    = './output/figure/EX2/'
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
    # extract depth
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
        depth_map_clip = depth_map[X_b[0]:X_b[1],Y_b[0]:Y_b[1]]
        # depth_map_clip = depth_map_clip[0:100,0:100,:]
        depth_map_clip = depth_map_clip
        depth_data.append(depth_map_clip)
    # depth_data = np.array(depth_data)

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
    Dtw['breath_list'] = np.array([])   # using for saving breath data
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
            breath_clip = depth_data[j][:,:]
            breath_mean = np.mean(breath_clip)
            
            if len(Dtw['breath_list']) == 0:
                Dtw['breath_list'] = np.array([breath_mean])
            else:
                Dtw['breath_list'] = np.hstack((Dtw['breath_list'],breath_mean))
            
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
            
            hand_change    = Dtw['hand_list'] - np.roll(Dtw['hand_list'],-1, axis = 0)
            # pdb.set_trace() 
            if np.mod(Dtw['hcnt'],5) == 0:  
                # pdb.set_trace()                                   # check open and close in every n frames
                hand_chg = hand_change[-6:-1,0]+hand_change[-6:-1,1]
                print(hand_chg)
                if np.sum(hand_chg) == 2:                                      # hand open to hand close change
                    open_cnt_list.append(Dtw['hcnt'])
                    Dtw['cnt_hand'][0] += 1
                if np.sum(hand_chg) == -2:                                     # hand close to hand open change
                    close_cnt_list.append(Dtw['hcnt'])
                    Dtw['cnt_hand'][1] += 1

                if np.sum(hand_chg) == 1:                                      # if only one hand close
                    if np.sum(hand_chg[0]) ==1 and np.sum(hand_chg[1]) == 0 :
                        print('please open your left hand')
                    if np.sum(hand_chg[1]) ==1 and np.sum(hand_chg[0]) == 0 :
                        print('please open your right hand')

                if np.sum(hand_chg) == -1:                                     # if only one hand open
                    if np.sum(hand_chg[0]) == -1 and np.sum(hand_chg[1]) == 0 :
                        print('please close your left hand')
                    if np.sum(hand_chg[1]) == -1 and np.sum(hand_chg[0]) == 0 :
                        print('please close your right hand')

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
    # plot the state of hold section
    pdb.set_trace() 
    impluse = np.zeros(Dtw['hand_list'][:,0].shape)                 # using for plot the change (hand change state)
    impluse[np.array(open_cnt_list)-1] = 10
    impluse[np.array(close_cnt_list)-1] = -10

    breath_chg_list = np.gradient(Dtw['breath_list'][:])
    breath_chg_list[breath_chg_list>0]  = 1
    breath_chg_list[breath_chg_list<0]  = 0
    breath_chg = breath_chg_list[:-2]-np.roll(breath_chg_list,-1)[:-2]

    plt.plot((Dtw['breath_list'][:]-Dtw['breath_list'][0])/10,label = 'depth of chest')
    plt.plot(Dtw['hand_list'][:,0],label = 'left hand state')
    plt.plot(Dtw['hand_list'][:,1]-5,label = 'right hand state')
    # plt.plot(impluse)
    # plt.plot(breath_chg)
    plt.legend()
    plt.title('hand and breath state of '+foldername)
    plt.show()

    # produce report for the hold section
    breath_in_flag  = False
    breath_out_flag = False
    hand_flag       = [False,False]                                            # hand open/close flag , all false is open , all True is close
    breath_state    = []
    breath_state_cnt_flag = False
    breath_state_cnt= 0                                                        # breath state change should exceed 10 frames
    for i in range(1,len(breath_chg_list)):# may modify in the future
        if breath_state_cnt_flag:
            breath_state_cnt += 1 
        if (breath_chg_list[i] == 1 and breath_chg_list[i-1] == 0) \
            and (breath_state_cnt>10 or breath_state_cnt_flag == False):

            print('breath in start at frame:'+str(Dtw['seglist'][0][1]+i))
            breath_in_flag  = True                                             # open breath in flag
            breath_out_flag = False                                            # close breath out flag
            breath_state.append([Dtw['seglist'][0][1]+i , 1])                  # save state
            breath_state_cnt_flag = True
            breath_state_cnt = 0

        if (breath_chg_list[i] == 0 and breath_chg_list[i-1] == 1) \
            and (breath_state_cnt>10 or breath_state_cnt_flag == False) :

            print('breath out start at frame:'+str(Dtw['seglist'][0][1]+i))
            breath_in_flag  = False                                            # open breath out flag
            breath_out_flag = True                                             # close breath in flag
            breath_state.append([Dtw['seglist'][0][1]+i , 0])                  # save state
            breath_state_cnt_flag = True
            breath_state_cnt = 0

        if breath_in_flag :                                                    # in breath in period

            if Dtw['hand_list'][i,0] == 3 and Dtw['hand_list'][i-1,0] == 2:    # when left hand close 
                print('left hand close at frame:'+str(Dtw['seglist'][0][1]+i))
                hand_flag[0] = True
            if Dtw['hand_list'][i,1] == 3 and Dtw['hand_list'][i-1,1] == 2:    # when right hand close 
                print('right hand close at frame:'+str(Dtw['seglist'][0][1]+i))
                hand_flag[1] = True

            if Dtw['hand_list'][i,0] == 2 and Dtw['hand_list'][i-1,0] == 3:    # when left hand open 
                print('left hand open at frame:'+str(Dtw['seglist'][0][1]+i))
                print('your left hand cannot open')
                hand_flag[1] = False
            if Dtw['hand_list'][i,1] == 2 and Dtw['hand_list'][i-1,1] == 3:    # when right hand open 
                print('right hand open at frame:'+str(Dtw['seglist'][0][1]+i))
                print('your right hand cannot open')
                hand_flag[1] = False

        if breath_out_flag :                                                   # in breath out period

            if Dtw['hand_list'][i,0] == 3 and Dtw['hand_list'][i-1,0] == 2:    # when left hand close 
                print('left hand close at frame:'+str(Dtw['seglist'][0][1]+i))
                print('your left hand cannot close')
                hand_flag[0] = True
            if Dtw['hand_list'][i,1] == 3 and Dtw['hand_list'][i-1,1] == 2:    # when right hand close 
                print('right hand close at frame:'+str(Dtw['seglist'][0][1]+i))
                print('your right hand cannot close')
                hand_flag[1] = True

            if Dtw['hand_list'][i,0] == 2 and Dtw['hand_list'][i-1,0] == 3:    # when left hand open 
                print('left hand open at frame:'+str(Dtw['seglist'][0][1]+i))
                hand_flag[1] = False
            if Dtw['hand_list'][i,1] == 2 and Dtw['hand_list'][i-1,1] == 3:    # when right hand open 
                print('right hand open at frame:'+str(Dtw['seglist'][0][1]+i))
                hand_flag[1] = False
    print('===========================================================\n\n\n')
    for j in range(1,len(breath_state)):
        if breath_state[j][1]-breath_state[j-1][1] == 1:
            print('breath in from frame ' + str(breath_state[j-1][0])+ ' to frame '+str(breath_state[j][0]) )
            print('frequency = '+ str(30.0/(breath_state[j][0]-breath_state[j-1][0]))+'Hz')
        if breath_state[j][1]-breath_state[j-1][1] == -1:
            print('breath out from frame ' + str(breath_state[j-1][0])+ ' to frame '+str(breath_state[j][0]) )
            print('frequency = '+ str(30.0/(breath_state[j][0]-breath_state[j-1][0]))+'Hz')
        

        




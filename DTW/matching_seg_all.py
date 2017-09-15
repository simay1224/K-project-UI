# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 00:25:04 2017

@author: Dawnknight
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 14:50:20 2017

@author: medialab
"""

import h5py,cPickle,pdb,glob,os
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf



data       = h5py.File('GT_V_data_mod_EX4.h5','r')
gt_data    = {}
gt_data[1] = data['GT_1'][:]
gt_data[2] = data['GT_2'][:]
gt_data[3] = data['GT_3'][:]
gt_data[4] = data['GT_4'][:]




src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'
#src_path  = 'D:/Project/K_project/data/unified data array/Unified_MData/'
#dst_path  = 'C:/Users/Dawnknight/Documents/GitHub/K_project/DTW/figure/0912/7 joints/'
dst_path  = './figure/0912/7 joints/'

order    = {}
order[0] = [1]
order[1] = [3]
order[2] = 'end'
order[3] = [4]
order[4] = [2,3]

AVGdist  ={}
for i in order.keys():
    AVGdist[i] = []
    


for infile in glob.glob(os.path.join(src_path,'*.pkl')):
    print infile
    test_data    = cPickle.load(file(infile,'rb'))[12:,:].T
    foldername   = infile.split('\\')[-1].split('_ex4')[0][:-3]
    
    if not os.path.exists(dst_path+foldername):
        os.makedirs(dst_path+foldername)
        
    text_file = open(dst_path+foldername+"/log.txt", "w")    

    # === initial setting ===
    cnt         = 0
    dcnt        = 0      # decreasing cnt
    test_idx    = 0
    
    chk_flag    = False
    deflag      = False  # decreasing flag
    
    distp_prev  = 0 
    
    distp_cmp  = np.inf
    

    oidx     = 0      # initail
    gt_idx   = 0
    idxlist  = []
    seglist  = []
    j        = 0
    
    DTW_path = {}
    avgdist  = {}
    for i in order.keys():
        avgdist[i]  = []
        DTW_path[i] = []
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
                if np.mod(j-(test_idx+1),10) == 0: # check every 10 frames
                    if (len(order[oidx])>1 ) & (not onedeflag):#((j- (test_idx+1)) <=60):
                        for ii in order[oidx]:
                            test_p = test_data[:,:] + np.atleast_2d((gt_data[ii][0,:]-test_data[test_idx,:]))
                            dist_p[ii], _ = fastdtw(gt_data[ii], test_p[test_idx:j,:], dist=euclidean)  
                            if (j == test_idx+1):
                                dpfirst[ii] = dist_p[ii]
                            else: # j > test_idx+1
                                 if (dpfirst[ii] - dist_p[ii])>3000:
                                     print('deflag on')
                                     deflag_mul[ii] = True
                                     onedeflag = True
                        if onedeflag:#(j- (test_idx+1)) >=60:   # compare the dist_p to decide which movement it is. 
                                                                #(may need further modification when doing muilti-ex)
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
                        dist_p, _ = fastdtw(gt_data[gt_idx], test_data_p[test_idx:j,:], dist=euclidean)
        
                        if (j == test_idx+1):
                            dpfirst = dist_p
                        else: # j > test_idx+1
                            if (dpfirst - dist_p)>2000:
                                print('deflag on')
                                deflag = True
                                distp_prev  = dist_p
              
            else: 
                test_data_p  = test_data[:,:] + np.atleast_2d((gt_data[gt_idx][0,:]-test_data[test_idx,:]))
                dist_p, path_p = fastdtw(gt_data[gt_idx], test_data_p[test_idx:j,:], dist=euclidean)
    
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
                        # === avg dist test ===
                        dist_p, path_p = fastdtw(gt_data[gt_idx], test_data_p[test_idx:endidx,:], dist=euclidean)
                        avgdist[gt_idx].append(dist_p/len(path_p))
                        DTW_path[gt_idx].append(path_p)
                        # ===
                        
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
           oidx = gt_idx
           # === avg dist test ===
           dist_p, path_p = fastdtw(gt_data[gt_idx], test_data_p[test_idx:endidx,:], dist=euclidean)
           avgdist[gt_idx].append(dist_p/len(path_p)) 
           DTW_path[gt_idx].append(path_p)
           # ===
           test_idx = endidx+1
        elif (j == (test_data.shape[0]-1))&(not segend) & (not deflag) :
            seglist.append([test_idx,test_data.shape[0]-1]) 
            endidx = test_data.shape[0]-1
            if len(order[oidx])>1:
            # === no decrease happen 
                for i in  order[oidx]: 
                    test_p = test_data[:,:] + np.atleast_2d((gt_data[i][0,:]-test_data[test_idx,:]))
                    dist_p[i], _ = fastdtw(gt_data[i], test_p[test_idx:,:], dist=euclidean)                      
                    if minval>dist_p[i]:
                        minval = dist_p[i] 
                        minidx = i  
                    gt_idx =  minidx 
                    idxlist.append(gt_idx)  
           
            # === avg dist test ===
            dist_p, path_p = fastdtw(gt_data[gt_idx], test_data_p[test_idx:endidx,:], dist=euclidean)
            avgdist[gt_idx].append(dist_p/len(path_p))       
            DTW_path[gt_idx].append(path_p)                 
            # ===    
            
            test_idx = endidx+1
       
        for i in range(21):
            fig = plt.figure(1)
            plt.plot(test_data[:endidx,i]-500,color = 'red')
            plt.plot(test_data[:,i],color = 'blue')
            plt.title('matching _ coordinate number is : ' +str(i))
            subfolder = '/coordinate '+str(i)
            if not os.path.exists(dst_path+foldername+subfolder):
                os.makedirs(dst_path+foldername+subfolder)
            fig.savefig(dst_path+foldername+subfolder+'/'+str(len(seglist)).zfill(2)+'.jpg')
            plt.close(fig)

            fig = plt.figure(1)
            offset = test_data[seglist[-1][0],i]-gt_data[idxlist[-1]][0,i]
            plt.plot(test_data[seglist[-1][0]:seglist[-1][1],i]-offset,color = 'red')
            plt.plot(gt_data[idxlist[-1]][:,i],color = 'Blue')
            plt.title('comparing _ coordinate number is : ' +str(i))
            fig.savefig(dst_path+foldername+subfolder+'/comparing w ground truth '+str(len(seglist)).zfill(2)+'.jpg')
            plt.close(fig)
            
    
    for i in order.keys():
        AVGdist[i].append(avgdist[i])    
        
    text_file.write("\n === seglist === \n"  )
    for i in range(len(seglist)):
        text_file.write(" %s :" %str(idxlist[i]) )
        text_file.write(" %s \n\n" %str(seglist[i]) )
    text_file.write(" === idx list === \n"  )
    text_file.write(" %s \n\n" %str(idxlist) )
    text_file.write(" === avgerage distant === \n"  )
    for i in avgdist.keys():
        text_file.write(" %s :" %str(i) )
        text_file.write(" %s \n" %str(avgdist[i]) )        
    text_file.close() 
    cPickle.dump(DTW_path,file(dst_path+foldername+subfolder+'DTW_path.pkl','wb'))

text_file_total = open(dst_path+"/log.txt", "w") 
text_file_total.write(" === avgerage distant === \n"  )
text_file_total.write(" %s \n" %str(AVGdist) )

cPickle.dump(AVGdist,file('AVGdist.pkl','wb'))
tmp = {} 
for i in order.keys():
    tmp[i] = [] 
    for j in range(len(AVGdist[i])):
        tmp[i] = tmp[i]+AVGdist[i][j]
    if tmp[i] != []:
        tmp[i] = [np.mean(tmp[i]),np.std(tmp[i])] 
        text_file_total.write(" === avgerage distant and std in movement %s === \n"%str(i) )
        text_file_total.write(" %s \n" %str(tmp[i]) )

text_file_total.close()










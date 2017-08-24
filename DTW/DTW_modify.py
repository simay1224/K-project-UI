# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 20:58:04 2017

mainly for test dtw in paper

@author: admin
"""
import _pickle as cPickle
import numpy as np
from scipy.spatial.distance import euclidean
import scipy.signal as signal
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import scipy
###################### function for 3D ########################################
def curvature_3D(Track_3D):
    dx            = np.gradient(Track_3D[:,0])
    dy            = np.gradient(Track_3D[:,1])
    dz            = np.gradient(Track_3D[:,2])
    
    dx2           = np.gradient(dx)
    dy2           = np.gradient(dy)
    dz2           = np.gradient(dz)
    
    k_fractions   = np.sqrt( ( dz2*dy - dy2*dz)**2 +
                             ( dx2*dz - dz2*dx)**2 + 
                             ( dy2*dx - dx2*dy)**2 )
    k_numerator   = np.power( dx**2+dy**2+dz**2 , 3/2 )
    
    k             = k_fractions / k_numerator
    return k

###################### product test data #####################################
#GT_ex_src   = 'Andy_2017-03-06 02.17.39 PM_ex4_FPS30_motion_unified.pkl'
GT_ex_src   = 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'
GT_name     = 'Andy2016'

Test_ex_src = 'Angela_2017-03-06 09.09.00 AM_ex4_FPS30_motion_unified.pkl'
Test_name   = 'Angela2017'

save_file_path = './/figure//'
#===================== combine two dataset ===================================#
GT_ex_WL      = cPickle.load(open(GT_ex_src,'rb') ,encoding = 'latin1')[18:21,:].T
Test_ex_WL    = cPickle.load(open(Test_ex_src,'rb') ,encoding = 'latin1')[18:21,:].T

GT_ex_WR      = cPickle.load(open(GT_ex_src,'rb') ,encoding = 'latin1')[24:30,:].T
Test_ex_WR    = cPickle.load(open(Test_ex_src,'rb') ,encoding = 'latin1')[24:30,:].T

GT_ex         = np.concatenate((GT_ex_WL,GT_ex_WR),axis=1)
Test_ex       = np.concatenate((Test_ex_WL,Test_ex_WR),axis=1)
#h          = np.atleast_2d(signal.firwin(10,0.2).T)
#Test_ex    = signal.convolve(Test_ex.T,h).T
#GT_ex      = signal.convolve(GT_ex.T,h).T

##Test_ex    = Test_ex[60:,:]
#GT_ex      = GT_ex[30:,:]
#Test_ex    = Test_ex[30:,:]

 

################### apply DTW to data ######################################

##=================== clip data =============================================#
GT_ex_clip = scipy.ndimage.filters.gaussian_filter1d(GT_ex.T,sigma=11).T

th           = 5
k            = curvature_3D(GT_ex_clip)
k[k<1]       = 0
k[k>1]       = 10
id_clip      = np.where(k==10)[0]
id_clip = id_clip[np.abs(id_clip-np.roll(id_clip,1))>th]
id_clip = np.hstack((0,id_clip))
id_clip = np.array([23,88,175,279,377,477,579,682,789,875,939,962])

##GT_ex               = GT_ex[0:100,:]
#Th                  = 10
#id_clip             = [0]
#y                   = [0]
#for i in range (21,GT_ex.shape[0]):
#    if np.abs(np.sum(GT_ex[i-21:i-1,0]-GT_ex[i-20:i,0])) < Th:
#        if i-id_clip[len(id_clip)-1]<=100:
#            continue
#        id_clip.append(i)
#        y.append(0)
#id_clip.append(GT_ex.shape[0])
#
#y.append(0)

#===========================================================================#
e                   = 30
id_joint            = 0
sita                = 6
distance_global     = []
distance_global_P   = []
distance_previous   = np.inf
id_f                = 0
id_list  = [0]
err      = []
cnt      = 0
grad_cnt = 10
check_flag = False
break_flag = False
distant_count  = 0
distant_list   = [0]
distant_P_list = [0]
skip_frame     = 50
for j in range (len(id_clip)-1): 
    Test_ex_P  = Test_ex + np.atleast_2d((GT_ex[id_clip[j]]-Test_ex[id_f]))
    for i in range (id_f+skip_frame,Test_ex.shape[0]):
#        distance, path     = fastdtw(GT_ex[id_clip[j]:id_clip[j+1],:], Test_ex[id_f:i,:],  dist=euclidean)
        distance_P, path_P = fastdtw(GT_ex[id_clip[j]:id_clip[j+1],:], Test_ex_P[id_f:i,:], dist=euclidean)
#        distant_list.append(distance)
        distant_P_list.append(distance_P)
        len_disp   = len(distant_P_list)
        if i-skip_frame-id_f > grad_cnt  :
            grad_dis   = np.gradient(distant_P_list[len_disp-grad_cnt:len_disp])
            if grad_dis[grad_dis.shape[0]-1]>0 and grad_dis[grad_dis.shape[0]-grad_cnt]<0:
                print('local min found in frame: '+str(i))
                distant_count = distance_P
                check_flag = True
            if check_flag:
                distant_compare = distance_P
                cnt = cnt + 1 
#                print (cnt)
                if  distant_count - distant_compare > 10 :
                    print ('ooooops')
                    check_flag = False
                    cnt        = 0
            if cnt == e:
                print('global min found in frame:'+str(i-e))
                id_f       = i-e
                id_list.append(id_f)
                break
        if i==Test_ex.shape[0]-1: 
            break_flag   = True
            id_f       = i-e
            id_list.append(id_f)  
            print('find bound program going to stop')
    cnt = 0        
    distant_P_list = []  
    check_flag     = False
    fig = plt.figure()
    plt.plot(Test_ex[0:id_f,id_joint]-500)
    plt.plot(GT_ex[0:id_clip[j+1],id_joint])
    plt.plot(id_clip,[10]*len(id_clip),'o')#GT_ex[id_clip-2,id_joint])
#    plt.legend(['Test data('+Test_name+')', 'Ground Truth data('+GT_name+')', 'Clip'], loc='best')
#    plt.show()
    fig.savefig(save_file_path+'ID'+str(j)+'_'+Test_name+'_'+'.jpg')
    plt.close(fig)
    if break_flag:
        break
############################## compare data ################################### 
for idx in range(1,len(id_list)):
    len_inter = max(id_list[idx],id_clip[idx] )
    x_test = np.linspace(id_list[idx-1], id_list[idx], num=id_list[idx]-id_list[idx-1], endpoint=True)
    y_test = interp1d(x_test,Test_ex[id_list[idx-1]:id_list[idx] ,id_joint],kind='cubic')
    x_GT   = np.linspace(id_clip[idx-1], id_clip[idx], num=id_clip[idx]-id_clip[idx-1], endpoint=True)
    y_GT   = interp1d(x_GT,GT_ex[id_clip[idx-1]:id_clip[idx] ,id_joint],kind='cubic')
    xnew_test = np.linspace(id_list[idx-1], id_list[idx], num=len_inter, endpoint=True)
    xnew_GT   = np.linspace(id_clip[idx-1], id_clip[idx], num=len_inter, endpoint=True)
    fig = plt.figure()
    plt.plot(y_test(xnew_test))
    plt.plot(y_GT(xnew_GT))
    plt.legend(['Test data('+Test_name+')', 'Ground Truth data('+GT_name+')'], loc='best')
    plt.title('sequence '+ str(idx))
    plt.show()
    fig.savefig(save_file_path+'sequence'+str(idx)+'_'+Test_name+'_'+'.jpg')
    plt.close(fig)
        


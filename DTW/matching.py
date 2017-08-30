# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 14:21:52 2017

@author: medialab
"""
#from __future__ import print_function
import cPickle,pdb
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy.signal import argrelextrema

src_path  = 'I:/AllData_0327/unified data array/Unified_MData/ex4/'
gt_src   = 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'


test_src = src_path + 'Andy_2017-03-06 02.18.16 PM_ex4_FPS30_motion_unified.pkl'


#test_src = 'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl'
#gt_data      = cPickle.load(open(gt_src ,'rb') ,encoding = 'latin1')[18:,30:].T
#test_data    = cPickle.load(open(test_src,'rb') ,encoding = 'latin1')[18:,30:].T

gt_data      = cPickle.load(file(gt_src,'rb'))[12:,:].T
test_data    = cPickle.load(file(test_src,'rb'))[12:,:].T

# === initialization ===
e                   = 20
delta               = 6

distlist            = []
distplist           = []

seglist             =[]
gtseglist           =[]
# === data segment ===

#th                  = 3
#
#
#grad  = gt_data[:,6]-np.roll(gt_data[:,6],-1)
#gidx  = np.arange(gt_data.shape[0])[np.abs(grad)<th]
##gidx  = np.append(np.append([0],gidx),[gt_data.shape[0]-1])
#sidx  = gidx[np.abs(gidx-np.roll(gidx,1))>th]
##eidx  = gidx[np.abs(gidx-np.roll(gidx,-1))>th]
##idx   = list((sidx+eidx)//2) + [len(gt_data)]
#idx   =  list(sidx)+[len(gt_data)-1]



datax  = gf(gt_data[:,6],15)
dx     = np.gradient(datax)
xidx = np.where(((dx > -0.1) & (dx<0.2))==True)[0]
xtmp = np.roll(xidx,1)-xidx

datay  = gf(gt_data[:,7],15)
dy     = np.gradient(datay)
yidx = np.where(((dy > -0.1) & (dy<0.2))==True)[0]
ytmp = np.roll(yidx,1)-yidx

dataz  = gf(gt_data[:,8],15)
dz     = np.gradient(dataz)
zidx = np.where(((dz > -0.1) & (dz<0.2))==True)[0]
ztmp = np.roll(zidx,1)-zidx

grad = (dx**2+dy**2+dz**2)**0.5

minm = argrelextrema(grad, np.less,order = 3)[0]
idx  = np.append([0],minm)
#plt.plot(dy,color='blue')
#plt.plot(dz,color='green')
#plt.plot(dx,color='red')
#plt.plot(gt_data[:,6]/10,color='red')
#plt.plot(grad,color='black')
#plt.plot(minm,grad[minm],'o')
#
#plt.show()

#idx = xidx[np.where(abs(xtmp)>20)[0]]



# === data segment ===

#data  = gf(gt_data[:,6],11)
#
#grad  = np.gradient(data)
#grad2 = np.gradient(grad)
#
#curv  = abs(grad2)/(abs(1+grad**2))**1.5 
#
#
#datax  = gf(gt_data[:,6],7)
#datay  = gf(gt_data[:,7],7)
#dataz  = gf(gt_data[:,8],7)
#gradx  = np.gradient(datax)
#gradx2 = np.gradient(gradx)
#grady  = np.gradient(datay)
#grady2 = np.gradient(grady)
#gradz  = np.gradient(dataz)
#gradz2 = np.gradient(gradz)
#
#curv  = (((gradz2*grady-grady2*gradz)**2+\
#          (gradx2*gradz-gradz2*gradx)**2+\
#          (grady2*gradx-gradx2*grady)**2)**0.5)/(gradx**2+grady**2+gradz**2)**1.5
#
#id_clip      = np.where(curv >1)[0]
#idx = id_clip[np.abs(id_clip-np.roll(id_clip,1))>10]

          
# === main function ===


cnt         = 0
dcnt        = 0      # decreasing cnt
test_idx    = 536
offset      = test_idx 
chk_flag    = False
deflag      = False  # decreasing flag
err         = []
dist_prev   = 0
distp_prev  = 0 

distp_cmp  = np.inf

for gt_idx in range(9,len(idx)-1):
    test_data_p  = test_data[:,6:9] + np.atleast_2d((gt_data[idx[gt_idx],6:9]-test_data[test_idx,6:9]))
    distlist  = []
    distplist = []


#    
    dcnt        = 0 
    deflag      = False
    
    for jidx,j in  enumerate(range(test_idx+1,test_data.shape[0])): 
        dist  , path   = fastdtw(gt_data[idx[gt_idx]:idx[gt_idx+1],6:9], test_data[test_idx:j,6:9]  , dist=euclidean)
        dist_p, path_p = fastdtw(gt_data[idx[gt_idx]:idx[gt_idx+1],6:9], test_data_p[test_idx:j,:]    , dist=euclidean)


        print j
        if jidx == 0:
            testlist = test_data[j,6:9]
        else:
            testlist = np.vstack([testlist,test_data[j,6:9]])
            

        
        distlist.append(dist)
        distplist.append(dist_p)
        
        if len(distlist)>1:
            gdist  = np.gradient(distlist)
            gdistp = np.gradient(distplist)
        
        if (j > test_idx+2) & (not deflag):
            if (distlist[-1]-distlist[-2]) <= 0:
                dcnt +=1
                if dcnt == 1:
                    dpfirst = dist_p
            else:
                dcnt = 0

            if dcnt == 10:
                if (dpfirst - dist_p)>3000:
                    print('deflag on')
                    deflag = True
                else:
                    dcnt = 1       
        
        if deflag : 
            if chk_flag:  # in check global min status
                cnt +=1
                err.append(np.abs(dist_p-dist)/dist) 
                
                if dist_p < distp_cmp : # find another small value
                    cnt = 0
                    err = []
                    distp_cmp = dist_p
                    idx_cmp   = j
                    print(' ==== reset ====')
                    
                elif cnt == 20:
                    Err_mean = np.mean(err)
                    pdb.set_trace()
                    print('err mean')
                    print(Err_mean)
                    if Err_mean <3:
                        chk_flag = False
#                        pdb.set_trace()
#                        pidx  = np.argmin(distplist)
#                        grad2 = np.gradient(np.gradient(distplist))
#                        gidx  = np.where(grad2 <2)[0]
#                        endidx = gidx[gidx>=pidx][0]+test_idx
##                        endidx = pidx+test_idx
                        
#                        tdatax  = gf(testlist[:,0],3)
#                        tdx     = np.gradient(tdatax)
#                       
#                        tdatay  = gf(testlist[:,1],3)
#                        tdy     = np.gradient(tdatay)
#                        
#                        tdataz  = gf(testlist[:,2],3)
#                        tdz     = np.gradient(tdataz)
#                                                
#                        tgrad = (tdx**2+tdy**2+tdz**2)**0.5
                        tgrad = 0

                        for ii in range(testlist.shape[1]):
                            tgrad += np.gradient(gf(testlist[:,ii],3))**2
                            
                        tgrad = tgrad**0.5


#                        pdb.set_trace()
                        endidx = np.argmin(tgrad[idx_cmp-test_idx-10:idx_cmp-test_idx+10])+(idx_cmp-10) 
                        # (idx_cmp-10)  = (idx_cmp-test_idx-10)+ test_idx
                        

                        seglist.append([test_idx,endidx])
                        gtseglist.append([idx[gt_idx],idx[gt_idx+1]])                        
                        test_idx = endidx+1
                        cnt      = 0
                        break
                        
                    else:
                        print('Ooops!!')
                        pdb.set_trace()
#                    
            else:  
                print dist_p-distp_prev
                
#                if (((dist_p-distp_prev)>2) &  ((distp_prev-distp_prev2)<0)):  # turning point
                if (dist_p-distp_prev)>2:
#                if (gdistp[-2]<0)&(gdistp[-1]>0):
                    print (' ==============  large ====================')
#                    pdb.set_trace()
                    distp_cmp = distp_prev
                    idx_cmp   = j
                    chk_flag = True
                    err      = []
                    

        dist_prev   = dist
        distp_prev  = dist_p 
        
        print ('===========\n')
     
#    pdb.set_trace()    
    if cnt > 0:
       seglist.append([test_idx,idx_cmp]) 
       gtseglist.append([idx[gt_idx],idx[gt_idx+1]]) 
       endidx =  idx_cmp
    elif idx_cmp == (test_data.shape[0]-1):
        seglist.append([test_idx,idx_cmp]) 
        gtseglist.append([idx[gt_idx],idx[gt_idx+1]])
        endidx =  idx_cmp
#       
#    
    fig = plt.figure(1)
    plt.plot(test_data[:endidx,6]-500,color = 'red')
#    plt.plot(np.arange(675,endidx),test_data[675:endidx,6]-500,color = 'red')
#    plt.plot(np.arange(idx[1],idx[2]),gt_data[idx[1]:idx[2],6], color = 'blue')
    plt.plot(gt_data[idx[0]:idx[gt_idx+1],6], color = 'blue')
    plt.title('matching')
    plt.plot(idx,[-10]*len(idx),'.m')
        
#    plt.show()
    fig.savefig(str(gt_idx).zfill(2)+'.jpg')
    plt.close(fig)


#    fig = plt.figure(1)
#    plt.plot(range(57,300),test_data[57:300,6],color = 'blue') 
#    plt.plot(range(offset,450),test_data[offset:450,6],color = 'blue') 
#    plt.plot(range(idx[3],idx[4]),gt_data[idx[3]:idx[4],6],color = 'green')
#    plt.plot(pidx+offset,distplist[pidx]/1,'o',color = 'blue')
#    plt.plot(idx_cmp,distplist[idx_cmp-offset]/1,'o',color = 'red')
#    plt.title('data')
        

    plt.plot(np.arange(len(distplist))+offset,np.array(distplist)/1,color = 'red')
    plt.title('dist')
#    plt.show()
##
    fig = plt.figure(3)
    plt.plot(np.arange(len(distplist))+offset,np.gradient(distplist),color = 'green')
    plt.title('dist grad')

    fig = plt.figure(4)
    plt.plot(np.arange(len(distplist))+offset,np.gradient(np.gradient(distplist)),color = 'green')
    plt.title('dist grad 2')    
    
    plt.show()



plt.plot(np.arange(testlist.shape[0])+test_idx,abs(np.gradient(testlist[:,0])))
plt.title('grad of data')
plt.show()

##
#tdatax  = gf(testlist[:,0],3)
#tdx     = np.gradient(tdatax)
#
#
#tdatay  = gf(testlist[:,1],3)
#tdy     = np.gradient(tdatay)
#
#tdataz  = gf(testlist[:,2],3)
#tdz     = np.gradient(tdataz)
#
#
#tgrad = (tdx**2+tdy**2+tdz**2)**0.5
#
#
#
#plt.plot(np.arange(len(tgrad))+test_idx,tgrad,color='black')
#
#plt.show()
##
##
#datax  = gf(test_data[:,6],15)
#dx     = np.gradient(datax)
#
#
#datay  = gf(test_data[:,7],15)
#dy     = np.gradient(datay)
#
#
#dataz  = gf(test_data[:,8],15)
#dz     = np.gradient(dataz)
#
#
#grad = (dx**2+dy**2+dz**2)**0.5
#
#minm = argrelextrema(grad, np.less,order = 3)[0]
#idx  = np.append([0],minm)
##plt.plot(dy,color='blue')
##plt.plot(dz,color='green')
##plt.plot(dx,color='red')
#plt.plot(test_data[:,6]/10,color='red')
#plt.plot(grad,color='black')
#plt.plot(minm,grad[minm],'o')
#
#plt.show()
#
#
#
#
#

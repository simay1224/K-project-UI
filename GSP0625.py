# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 16:25:26 2017

@author: Dawnknight
"""

import cPickle,h5py,pdb
import numpy as np
import glob,os
from scipy.stats import pearsonr
from numpy.linalg import eig
from scipy.linalg import eig as seig
from numpy.linalg import norm,inv

src_path = 'I:/AllData_0327/unified data array/'
#src_path = './data/unified data array/'
Mfolder  = 'Unified_MData/'
Kfolder  = 'Unified_KData/'
Rfolder  = 'reliability/'
dst_folder = 'GSP_test/'


Mfile = glob.glob(os.path.join(src_path+Mfolder,'*.pkl'))

Jnum   = 6   # joint number
Tnum   = 1   # time interval
sigma  = 2
sigma_x = 150
sigma_y = 6
sigma_z = 17

Rel_th = 0.7
cor_th = 0.1

def corr(A,B):
    ma = np.mean(A)
    mb = np.mean(B)
    sa = np.std(A)
    sb = np.std(B)
    if ((sa ==0)&(sb ==0)):
        return 1.
    elif ((sa ==0)|(sb ==0)):
        return 0.
    else:    
        return np.mean((A-ma)*(B-mb))/sa/sb

distmtx    = np.zeros((Jnum*Tnum,Jnum*Tnum,len(Mfile)))
distmtx3   = np.zeros((Jnum*Tnum,Jnum*Tnum,3,len(Mfile)))
adjmtx     = np.zeros((Jnum*Tnum,Jnum*Tnum))
adjmtx_th  = np.zeros((Jnum*Tnum,Jnum*Tnum))
thmtx      = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx     = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx_x   = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx_y   = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx_z   = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx_th  = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx_xth = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx_yth = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx_zth = np.zeros((Jnum*Tnum,Jnum*Tnum))
Lapmtx     = np.zeros((Jnum*Tnum,Jnum*Tnum))
Lapmtx_th  = np.zeros((Jnum*Tnum,Jnum*Tnum))
L          = np.zeros((Jnum*Tnum))
Cidx       = np.arange(Jnum*Tnum)  #column idx
Ridx       = np.arange(Jnum*Tnum)  #row idx



thmtx[0,1] = 1
thmtx[1,2] = 1
thmtx[3,4] = 1
thmtx[4,5] = 1

thmtx[0,3] = 1 
    
for i in range(Jnum):
    thmtx[i,i::Jnum] = 1



corrmtx3 = np.zeros([Jnum*Tnum,Jnum*Tnum,3,len(Mfile)])
corrmtx = np.zeros([Jnum*Tnum,Jnum*Tnum])

for midx,mfile in enumerate(Mfile):
    print mfile
    data = cPickle.load(file(mfile,'rb'))[12:30]
    data = data.reshape(-1,3,data.shape[1])
    
    if  Tnum != 1:    # if consider more than one time sample
        M = data[:,:,:-(Tnum-1)]
        for i in range(1,Tnum):
            M = np.vstack([M,np.roll(data,-i,axis = 2)[:,:,:-(Tnum-1)]])
    else:
        M = data    
    ### calculate correlation between joints
    for i in range(Jnum*Tnum-1):
        for j in range(i+1,Jnum*Tnum):
            corrmtx3[i,j,0,midx] = corr(data[i,0,:],data[j,0,:])
            corrmtx3[i,j,1,midx] = corr(data[i,1,:],data[j,1,:])
            corrmtx3[i,j,2,midx] = corr(data[i,2,:],data[j,2,:])
    ### calculate distant's weight between joints
    for idx in range(1,Jnum*Tnum/2+1):   # precisely should be np.round((Jnum*Tnum-1)/2.).astype('int')+1
        
        curRidx = np.roll(Ridx,-idx) 
        Diff = abs(M - np.roll(M,-idx,axis = 0))

        L2   = np.mean((np.sum(Diff**2,axis = 1))**0.5,axis = 1)
        W    = np.exp(-L2/sigma**2)
        W_x = np.mean(np.exp(-Diff[:,0,:]**2/sigma_x**2),axis = 1)
        W_y = np.mean(np.exp(-Diff[:,1,:]**2/sigma_y**2),axis = 1)
        W_z = np.mean(np.exp(-Diff[:,2,:]**2/sigma_z**2),axis = 1)
        
        for Lidx,(i,j) in enumerate(zip(Cidx,curRidx)):
            col = min(i,j)
            row = max(i,j)
            distmtx[col,row,midx]    = W[Lidx]
            distmtx3[col,row,0,midx] = W_x[Lidx]
            distmtx3[col,row,1,midx] = W_y[Lidx]
            distmtx3[col,row,2,midx] = W_z[Lidx]

#corrmtx3[0,3,2,:][np.isnan(corrmtx3[0,3,2,:])] = 1  # L and R shoulder in Z axis's correlation
#corrmtx3[np.isnan(corrmtx3)] = 0
corrmtx3[corrmtx3<cor_th] = 0

corrmtx[:] = np.mean(np.sum(corrmtx3**2,axis=2)**0.5,axis = 2)        
corrmtx_x  = np.mean(corrmtx3,axis = 3)[:,:,0]
corrmtx_y  = np.mean(corrmtx3,axis = 3)[:,:,1]
corrmtx_z  = np.mean(corrmtx3,axis = 3)[:,:,2]
   
adjmtx[:]    = np.mean(distmtx,axis=2)+ corrmtx
adjmtx_x     = np.mean(distmtx3,axis=3)[:,:,0]* corrmtx_x
adjmtx_y     = np.mean(distmtx3,axis=3)[:,:,1]* corrmtx_y
adjmtx_z     = np.mean(distmtx3,axis=3)[:,:,2]* corrmtx_z

adjmtx_th[:]  = adjmtx*thmtx
adjmtx_xth = adjmtx_x*thmtx
adjmtx_yth = adjmtx_y*thmtx
adjmtx_zth = adjmtx_z*thmtx

#pdb.set_trace()
adjmtx[:] = adjmtx + adjmtx.T
adjmtx_x  = adjmtx_x + adjmtx_x.T
adjmtx_y  = adjmtx_y + adjmtx_y.T
adjmtx_z  = adjmtx_z + adjmtx_z.T

adjmtx_th[:] = adjmtx_th + adjmtx_th.T
adjmtx_xth   = adjmtx_xth + adjmtx_xth.T
adjmtx_yth   = adjmtx_yth + adjmtx_yth.T
adjmtx_zth   = adjmtx_zth + adjmtx_zth.T
        

for i in range(Jnum*Tnum):
    degmtx[i,i]    = sum(adjmtx[i,:])
    degmtx_x[i,i]  = sum(adjmtx_x[i,:])
    degmtx_y[i,i]  = sum(adjmtx_y[i,:])
    degmtx_z[i,i]  = sum(adjmtx_z[i,:])

    degmtx_th[i,i]  = sum(adjmtx_th[i,:]) 
    degmtx_xth[i,i] = sum(adjmtx_xth[i,:])
    degmtx_yth[i,i] = sum(adjmtx_yth[i,:])
    degmtx_zth[i,i] = sum(adjmtx_zth[i,:])    
    
    
Lapmtx[:]    = degmtx - adjmtx    
Lapmtx_x     = degmtx_x - adjmtx_x
Lapmtx_y     = degmtx_y - adjmtx_y
Lapmtx_z     = degmtx_z - adjmtx_z

Lapmtx_th[:] = degmtx_th - adjmtx_th  
Lapmtx_xth   = degmtx_xth - adjmtx_xth  
Lapmtx_yth   = degmtx_yth - adjmtx_yth    
Lapmtx_zth   = degmtx_zth - adjmtx_zth
    
Eval,Evec         = eig(Lapmtx)
Eval_x,Evec_x     = eig(Lapmtx_x)
Eval_y,Evec_y     = eig(Lapmtx_y)
Eval_z,Evec_z     = eig(Lapmtx_z)

Eval_th,Evec_th   = eig(Lapmtx_th)   
Eval_xth,Evec_xth = eig(Lapmtx_xth)
Eval_yth,Evec_yth = eig(Lapmtx_yth)
Eval_zth,Evec_zth = eig(Lapmtx_zth)    
    

Rel_th = 0.5
gamma_x = 8.75
gamma_y = 0.001
gamma_z = 0.001


for Kfile,Rfile in zip(glob.glob(os.path.join(src_path+Kfolder,'*ex4.pkl')),glob.glob(os.path.join(src_path+Rfolder,'*ex4.pkl'))):
    print Kfile
    Kdata = cPickle.load(file(Kfile,'rb'))[12:30,:]     
    Rdata = cPickle.load(file(Rfile,'rb'))[4:10,:]
    unrelidx = np.where(np.sum((Rdata<Rel_th)*1,0)!=0)[0]   # frames which have unreliable  joints
    Kdata = Kdata.reshape((-1,3,Kdata.shape[1]))
    corKdata = np.zeros(Kdata.shape)
    corKdata += Kdata 
    
    
    
    for idx in unrelidx:
        pdb.set_trace()
        
        R = np.zeros(6)+Rdata[:,idx]
        R[R>=Rel_th] = 1.
        R[R< Rel_th] = 0.
        W = np.diag(R)
        
        
        mx = np.matmul(np.matmul(inv(np.matmul(W.T,W)+gamma_x*Lapmtx_x),np.matmul(W.T,W)),Kdata[:,0,idx].reshape(6,-1))
        my = np.matmul(np.matmul(inv(np.matmul(W.T,W)+gamma_y*Lapmtx_y),np.matmul(W.T,W)),Kdata[:,1,idx].reshape(6,-1))
        mz = np.matmul(np.matmul(inv(np.matmul(W.T,W)+gamma_z*Lapmtx_z),np.matmul(W.T,W)),Kdata[:,2,idx].reshape(6,-1))
          
        corKdata[R==0,0,idx]    = mx[R==0].flatten()
        corKdata[R==0,1,idx]    = my[R==0].flatten()
        corKdata[R==0,2,idx]    = mz[R==0].flatten()

        fname =src_path +dst_folder +Kfile.split('\\')[-1][:-3]+'h5'
        f = h5py.File(fname,'w')
        f.create_dataset('data',data = corKdata)
        f.close()
    
    
    
'''  
Mdata = cPickle.load(file(src_path+Mfolder+'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl','rb'))[12:30,:]    
Kdata = cPickle.load(file(src_path+Kfolder+'Andy_data201612151615_unified_ex4.pkl','rb'))[12:30,:]
Rdata = cPickle.load(file(src_path+Rfolder+'Andy_data201612151615_Rel_ex4.pkl','rb'))[4:10]

    
idx = 168

Kdata = Kdata.reshape((-1,3,Kdata.shape[1])) 
R = np.diag(np.array([1.,1.,0.,1.,1.,1.]))#Rdata[:,idx]#



opt_x = []
opt_y = []
opt_z = []
opt_xth = []
opt_yth = []
opt_zth = []

N = 1000
scale = 0.01

for i in range(1,N):
    gamma = i*scale

    opt_x.append(np.matmul(np.matmul(inv(np.matmul(R.T,R)+gamma*Lapmtx_x),np.matmul(R.T,R)),Kdata[:,0,idx].reshape(6,-1))[2])
    opt_y.append(np.matmul(np.matmul(inv(np.matmul(R.T,R)+gamma*Lapmtx_y),np.matmul(R.T,R)),Kdata[:,1,idx].reshape(6,-1))[2])
    opt_z.append(np.matmul(np.matmul(inv(np.matmul(R.T,R)+gamma*Lapmtx_z),np.matmul(R.T,R)),Kdata[:,2,idx].reshape(6,-1))[2])
    
    opt_xth.append(np.matmul(np.matmul(inv(np.matmul(R.T,R)+gamma*Lapmtx_xth),np.matmul(R.T,R)),Kdata[:,0,idx].reshape(6,-1))[2])
    opt_yth.append(np.matmul(np.matmul(inv(np.matmul(R.T,R)+gamma*Lapmtx_yth),np.matmul(R.T,R)),Kdata[:,1,idx].reshape(6,-1))[2])
    opt_zth.append(np.matmul(np.matmul(inv(np.matmul(R.T,R)+gamma*Lapmtx_zth),np.matmul(R.T,R)),Kdata[:,2,idx].reshape(6,-1))[2])    
    
    

import matplotlib.pyplot as plt
plt.figure(1)
plt.title('normal')
ax1 = plt.subplot(3,1,1)
ax1.set_title('X value with different mu')
plt.plot(np.arange(N-1)*scale,opt_x,color = 'blue',label = 'result')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*Kdata[2,0,idx],color = 'red',label = 'original value')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*-25,color = 'green',label = 'expected value')
plt.legend( loc=1)

ax2 = plt.subplot(3,1,2)
ax2.set_title('Y value with different mu')
plt.plot(np.arange(N-1)*scale,opt_y,color = 'blue',label = 'result')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*Kdata[2,1,idx],color = 'red',label = 'original value')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*347,color = 'green',label = 'expected value')
plt.legend( loc=1)

ax3 = plt.subplot(3,1,3)
ax3.set_title('Z value with different mu')
plt.plot(np.arange(N-1)*scale,opt_z,color = 'blue',label = 'result')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*Kdata[2,2,idx],color = 'red',label = 'original value')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*-148.5,color = 'green',label = 'expected value')
plt.legend( loc=1)
plt.show()



plt.figure(2)

ax1 = plt.subplot(3,1,1)
ax1.set_title('X value with different mu (only connected joints)')
plt.plot(np.arange(N-1)*scale,opt_xth,color = 'blue',label = 'result')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*Kdata[2,0,idx],color = 'red',label = 'original value')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*-25,color = 'green',label = 'expected value')
plt.legend( loc=1)

ax2 = plt.subplot(3,1,2)
ax2.set_title('Y value with different mu (only connected joints)')
plt.plot(np.arange(N-1)*scale,opt_yth,color = 'blue',label = 'result')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*Kdata[2,1,idx],color = 'red',label = 'original value')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*347,color = 'green',label = 'expected value')
plt.legend( loc=1)

ax3 = plt.subplot(3,1,3)
ax3.set_title('Z value with different mu (only connected joints)')
plt.plot(np.arange(N-1)*scale,opt_zth,color = 'blue',label = 'result')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*Kdata[2,2,idx],color = 'red',label = 'original value')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*-148.5,color = 'green',label = 'expected value')
plt.legend( loc=1)
plt.show()


'''

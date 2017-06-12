# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 16:25:26 2017

@author: Dawnknight
"""

import cPickle
import numpy as np
import glob,os
from scipy.stats import pearsonr
from numpy.linalg import eig


src_path = 'I:/AllData_0327/unified data array/'
#src_path = './data/unified data array/'
Mfolder  = 'Unified_MData/'
Kfolder  = 'Unified_KData/'
Rfolder  = 'reliability/'

Mfile = glob.glob(os.path.join(src_path+Mfolder,'*.pkl'))

Jnum   = 6   # joint number
Tnum   = 1   # time interval
sigma  = 20
Rel_th = 0.7

distmtx    = np.zeros((Jnum*Tnum,Jnum*Tnum,len(Mfile)))
adjmtx     = np.zeros((Jnum*Tnum,Jnum*Tnum))
adjmtx_th  = np.zeros((Jnum*Tnum,Jnum*Tnum))
thmtx      = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx     = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx_th  = np.zeros((Jnum*Tnum,Jnum*Tnum))
Lapmtx     = np.zeros((Jnum*Tnum,Jnum*Tnum))
Lapmtx_th  = np.zeros((Jnum*Tnum,Jnum*Tnum))
L          = np.zeros((Jnum*Tnum))
Cidx       = np.arange(Jnum*Tnum)  #column idx
Ridx       = np.arange(Jnum*Tnum)  #row idx



thmtx[0,1] = 1
thmtx[1,2] = 1
thmtx[3,4] = 1
thmtx[4,5] = 1    
for i in range(Jnum):
    thmtx[i,i::Jnum] = 1



corrmtx3 = np.zeros([Jnum*Tnum,Jnum*Tnum,3,len(Mfile)])
corrmtx = np.zeros([Jnum*Tnum,Jnum*Tnum])

for midx,mfile in enumerate(Mfile):
    print mfile
    data = cPickle.load(file(mfile,'rb'))[12:30]
    data = data.reshape(-1,3,data.shape[1])
    if  Tnum != 1:   
        M = data[:,:,:-(Tnum-1)]
        for i in range(1,Tnum):
            M = np.vstack([M,np.roll(data,-i,axis = 2)[:,:,:-(Tnum-1)]])
    else:
        M = data    
    ### calculate correlation between joints
    for i in range(Jnum*Tnum-1):
        for j in range(i+1,Jnum*Tnum):
            corrmtx3[i,j,0,midx] = pearsonr(data[i,0,:],data[j,0,:])[0]
            corrmtx3[i,j,1,midx] = pearsonr(data[i,1,:],data[j,1,:])[0]
            corrmtx3[i,j,2,midx] = pearsonr(data[i,2,:],data[j,2,:])[0]
    ### calculate distant's weight between joints
    for idx in range(1,Jnum*Tnum/2+1):   # precisely should be np.round((Jnum*Tnum-1)/2.).astype('int')+1
        
        curRidx = np.roll(Ridx,-idx) 
        Diff = M - np.roll(M,-idx,axis = 0)
        L2   = np.mean((np.sum(Diff**2,axis = 1))**0.5,axis = 1)
        W    = np.exp(-L2/sigma**2) 
        for Lidx,(i,j) in enumerate(zip(Cidx,curRidx)):
            col = min(i,j)
            row = max(i,j)
            distmtx[col,row,midx] = W[Lidx]



corrmtx3[0,3,2,:][np.isnan(corrmtx3[0,3,2,:])] = 1  # L and R should in Z axis's correlation
corrmtx3[np.isnan(corrmtx3)] = 0
        
corrmtx[:] = np.mean(np.sum(corrmtx3**2,axis=2)**0.5,axis = 2)        
   
adjmtx[:]    = np.mean(distmtx,axis=2)+ corrmtx
adjmtx_th[:] = (np.mean(distmtx,axis=2)+ corrmtx)*thmtx

adjmtx[:] = adjmtx + adjmtx.T

adjmtx_th[:] = adjmtx_th + adjmtx_th.T
        
for i in range(Jnum*Tnum):
    degmtx[i,i]    = sum(adjmtx[i,:])   
    degmtx_th[i,i] = sum(adjmtx_th[i,:]) 

    
Lapmtx[:]    = degmtx - adjmtx    
Lapmtx_th[:] = degmtx_th - adjmtx_th  

   
    
Eval,Evec       = eig(Lapmtx)
Eval_th,Evec_th = eig(Lapmtx_th)   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
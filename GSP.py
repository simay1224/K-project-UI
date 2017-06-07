# -*- coding: utf-8 -*-
"""
Created on Mon Jun 05 22:15:50 2017

@author: Dawnknight
"""

import cPickle
import numpy as np
from scipy import optimize

src_path = 'I:/AllData_0327/unified data array/'
Mfolder  = 'Unified_MData/'
Kfolder  = 'Unified_KData/'

#Mdata = {}
#Kdata = {}
#
#Mdata[0] = cPickle.load(file(src_path+Mfolder+'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl','rb'))#[12:30,:]
#Kdata[0] = cPickle.load(file(src_path+Kfolder+'Andy_data201612151615_unified_ex4.pkl','rb'))#[12:30,:]
#
#Jnum  = 6   # joint number
#Tnum  = 2   # time interval
#sigma = 1
#
#Len   = min(Mdata[0].shape[1],Kdata[0].shape[1])
#Mdata[0] = Mdata[0][:,:Len].reshape((-1,3,Len))
#Kdata[0] = Kdata[0][:,:Len].reshape((-1,3,Len))
#
#for i in range(1,Tnum):
#    Mdata[i] = np.roll(Mdata[0],-i,axis = 2)[:,:,:-(tnum-1)]
#    Kdata[i] = np.roll(Kdata[0],-i,axis = 2)[:,:,:-(tnum-1)]
#    
#Mdata[0] = Mdata[0][:,:,:-(Tnum-1)]
#Kdata[0] = Kdata[0][:,:,:-(Tnum-1)]    

Mdata = cPickle.load(file(src_path+Mfolder+'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl','rb'))[12:30,:]
Kdata = cPickle.load(file(src_path+Kfolder+'Andy_data201612151615_unified_ex4.pkl','rb'))[12:30,:]
Jnum  = 6   # joint number
Tnum  = 2   # time interval
sigma = 20

Len   = min(Mdata.shape[1],Kdata.shape[1])
Mdata = Mdata[:,:Len].reshape((-1,3,Len))
Kdata = Kdata[:,:Len].reshape((-1,3,Len))

M = Mdata[:,:,:-(Tnum-1)]
K = Kdata[:,:,:-(Tnum-1)]
for i in range(1,Tnum):
    M = np.vstack([M,np.roll(Mdata,-i,axis = 2)[:,:,:-(Tnum-1)]])



adjmtx = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx = np.zeros((Jnum*Tnum,Jnum*Tnum))
Lapmtx = np.zeros((Jnum*Tnum,Jnum*Tnum))

Cidx = np.arange(Jnum*Tnum)  #column idx
Ridx = np.arange(Jnum*Tnum)  #row idx

for idx in range(1,Jnum*Tnum/2+1):   # precisely should be np.round((Jnum*Tnum-1)/2.).astype('int')+1
    
    curRidx = np.roll(Ridx,-idx) 
    Diff = M - np.roll(M,-idx,axis = 0)
    L2   = np.mean((np.sum(Diff**2,axis = 1))**0.5,axis = 1)
    W    = np.exp(-L2/sigma**2) 
    for Lidx,(i,j) in enumerate(zip(Cidx,curRidx)):
        col = min(i,j)
        row = max(i,j)
        adjmtx[col,row] = W[Lidx]
adjmtx += adjmtx.T

for i in range(Jnum*Tnum):
    degmtx[i,i] = sum(adjmtx[i,:])
#    print  degmtx[i,i]   
       
Lapmtx[:] = degmtx - adjmtx


#F(x) = (X-Y).T*W*(X-Y)+X.T*L*X



def func(X,u):
    X = X.reshpe((18,-1)) 
    return (X-Y).T*W*(X-Y)+u*X.T*L*X
    
    
x =  optimize.fmin(func, np.random.rand(Jnum*3*Tnum),arg = (0.1) )   
    










#y = np.array([1,2])
#def func(x):
#    
#    
#    return sum((x-y)**2)
#    
#
#w = optimize.fmin(func, np.random.rand(2) )
#
#print w
#        
#    
#from scipy import optimize
#import numpy as np
#import pdb
#
#m = 5
#n = 3
#
#a = np.random.rand(m, n)
#idx = np.arange(n)
#
#def func(w, beta, lam):
#    pdb.set_trace()
#    w = w.reshape(n, n)
#    w2 = np.abs(w)
#    w2[idx, idx] = 0
#    return 0.5*((a - np.dot(a, w2))**2).sum() + lam*w2.sum() + 0.5*beta*(w2**2).sum()
#
#w = optimize.fmin(func, np.random.rand(n*n), args=(0.1, 0.2))
#w = w.reshape(n, n)
#w[idx, idx] = 0
#w = np.abs(w)
#print w            

            



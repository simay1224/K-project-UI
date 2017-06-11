# -*- coding: utf-8 -*-
"""
Created on Mon Jun 05 22:15:50 2017

@author: Dawnknight
"""

import cPickle
import numpy as np
from scipy import optimize

#src_path = 'I:/AllData_0327/unified data array/'
src_path = './data/unified data array/'
Mfolder  = 'Unified_MData/'
Kfolder  = 'Unified_KData/'
Rfolder  = 'reliability/'


Mdata = cPickle.load(file(src_path+Mfolder+'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl','rb'))[12:30,:]
Kdata = cPickle.load(file(src_path+Kfolder+'Andy_data201612151615_unified_ex4.pkl','rb'))[12:30,:]
Rdata = cPickle.load(file(src_path+Rfolder+'Andy_data201612151615_Rel_ex4.pkl','rb'))[4:10]

Jnum   = 6   # joint number
Tnum   = 2   # time interval
sigma  = 20
Rel_th = 0.7


Len   = min(Mdata.shape[1],Kdata.shape[1])
Mdata = Mdata[:,:Len].reshape((-1,3,Len))
Kdata = Kdata[:,:Len].reshape((-1,3,Len))
Rdata = Rdata[:,:Len]

Kv    = Kdata - np.roll(Kdata,1,axis = 2) 
Ka    = Kv - np.roll(Kv,1,axis = 2) 


M = Mdata[:,:,:-(Tnum-1)]
K = Kdata[:,:,:-(Tnum-1)]
for i in range(1,Tnum):
    M = np.vstack([M,np.roll(Mdata,-i,axis = 2)[:,:,:-(Tnum-1)]])



adjmtx = np.zeros((Jnum*Tnum,Jnum*Tnum))
degmtx = np.zeros((Jnum*Tnum,Jnum*Tnum))
Lapmtx = np.zeros((Jnum*Tnum,Jnum*Tnum))
L      = np.zeros((Jnum*Tnum))
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


def func(X,Y):
#    x = X.reshape((12,3))
#    y = Y.reshape((12,3))
    return sum(X-Y)

def func(X,u,Y,R,L):
    Y = Y.reshape((12,3))
    X = X.reshape((12,3))
    L = L.reshape((12,12))
    
    return   (np.matmul(np.matmul((X[:,0]-Y[:,0]).T,np.diag(R)), (X[:,0]-Y[:,0]))**2+\
              np.matmul(np.matmul((X[:,1]-Y[:,1]).T,np.diag(R)), (X[:,1]-Y[:,1]))**2+\
              np.matmul(np.matmul((X[:,2]-Y[:,2]).T,np.diag(R)), (X[:,2]-Y[:,2]))**2)**0.5+\
          u*((np.matmul(np.matmul(X[:,0].T,L),X[:,0])**2+\
              np.matmul(np.matmul(X[:,1].T,L),X[:,1])**2+\
              np.matmul(np.matmul(X[:,2].T,L),X[:,2])**2)**0.5)

def pos_est(fidx,Kv,Ka,Kdata):
    return Kdata[:,:,fidx]+Kv[:,:,fidx]+Ka[:,:,fidx]    
          
 
          
relidx = np.where(np.sum((Rdata<Rel_th)*1,0)!=0)[0]   # frames which have unreliable  joints      
relidx2 = np.where(np.sum((Rdata<Rel_th)*1,0)!=0)[0] 


 

        
for frame_idx in  relidx:
    Y   = np.vstack([Kdata[:,:,frame_idx-1],Kdata[:,:,frame_idx]])
    Rel = np.hstack([Rdata[:,frame_idx-1],Rdata[:,frame_idx]])
    
#    if frame_idx-1 in  relidx: 
#        Xtm1_init = 
#    else:
    Xtm1_init = Kdata[:,:,frame_idx-1]
    Xt_init   = pos_est(frame_idx,Kv,Ka,Kdata)

    X_init = np.vstack([Xtm1_init,Xt_init])
         
          
    x =  optimize.fmin_bfgs(func, X_init.flatten() ,args = (0.001,Y.flatten(),Rel,Lapmtx.flatten(),)) 
    
    
x =  optimize.fmin(func, X_init.flatten() ,args = (Y.flatten(),) )

  
    











from scipy import optimize
import numpy as np

def func(x,Y):
    return sum((x[:-1]-Y[:-1])**2+(x[1:]-Y[1:])**2)
   
y = np.array([1,2,3])
w = optimize.fmin(func, x0 = np.random.rand(3),args =(y,))

print w


        
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
##    pdb.set_trace()
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
#
#            
#
#

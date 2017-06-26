# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 18:44:53 2017

@author: Dawnknight
"""



import cPickle,h5py,time,pdb
import numpy as np
import glob,os
from scipy.stats import pearsonr
from numpy.linalg import eig
from numpy.linalg import norm,inv

from scipy import optimize

#src_path = 'I:/AllData_0327/unified data array/'
src_path = './data/unified data array/'
Mfolder  = 'Unified_MData/'
Kfolder  = 'Unified_KData/'
Rfolder  = 'reliability/'
M2Kfolder = '../GPR_M2K/'

Mfile = glob.glob(os.path.join(src_path+Mfolder,'*.pkl'))

Jnum   = 6   # joint number
Tnum   = 1   # time interval
sigma  = 20
Rel_th = 0.7
cor_th = 0.1
sigma_x = 150
sigma_y = 6
sigma_z = 17

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
            corrmtx3[i,j,0,midx] = corr(data[i,0,:],data[j,0,:])
            corrmtx3[i,j,1,midx] = corr(data[i,1,:],data[j,1,:])
            corrmtx3[i,j,2,midx] = corr(data[i,2,:],data[j,2,:])
    ### calculate distant's weight between joints
    for idx in range(1,Jnum*Tnum/2+1):   # precisely should be np.round((Jnum*Tnum-1)/2.).astype('int')+1
        
        curRidx = np.roll(Ridx,-idx) 
        Diff = M - np.roll(M,-idx,axis = 0)

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

Rel_th = 0.7
st = time.clock()
#corrmtx3[0,3,2,:][np.isnan(corrmtx3[0,3,2,:])] = 1  # L and R shoulder in Z axis's correlation
#corrmtx3[np.isnan(corrmtx3)] = 0
         
for cor_th in [0,0.25,0.5]:  # ============================================================#
    
    corrmtx3[corrmtx3<cor_th] = 0
    
    corrmtx[:] = np.mean(np.sum(corrmtx3**2,axis=2)**0.5,axis = 2)        
    corrmtx_x  = np.mean(corrmtx3,axis = 3)[:,:,0]
    corrmtx_y  = np.mean(corrmtx3,axis = 3)[:,:,1]
    corrmtx_z  = np.mean(corrmtx3,axis = 3)[:,:,2]

    adjmtx[:]    = np.mean(distmtx,axis=2)+ corrmtx
    adjmtx_x     = np.mean(distmtx3,axis=3)[:,:,0]* corrmtx_x
    adjmtx_y     = np.mean(distmtx3,axis=3)[:,:,1]* corrmtx_y
    adjmtx_z     = np.mean(distmtx3,axis=3)[:,:,2]* corrmtx_z

    for adj_type in [0,1]:  # ============================================================#
        
        if adj_type == 0: #consider relation between all joints 
        

            adjmtx[:] = adjmtx + adjmtx.T
            adjmtx_x  = adjmtx_x + adjmtx_x.T
            adjmtx_y  = adjmtx_y + adjmtx_y.T
            adjmtx_z  = adjmtx_z + adjmtx_z.T
            
        else:    # only consider connected joints 
        
            adjmtx[:]  = adjmtx*thmtx
            adjmtx_x   = adjmtx_x*thmtx
            adjmtx_y   = adjmtx_y*thmtx
            adjmtx_z   = adjmtx_z*thmtx
    
            adjmtx[:]  = adjmtx + adjmtx.T
            adjmtx_x   = adjmtx_x + adjmtx_x.T
            adjmtx_y   = adjmtx_y + adjmtx_y.T
            adjmtx_z   = adjmtx_z + adjmtx_z.T
                
        
        for i in range(Jnum*Tnum):
            degmtx[i,i]    = sum(adjmtx[i,:])
            degmtx_x[i,i]  = sum(adjmtx_x[i,:])
            degmtx_y[i,i]  = sum(adjmtx_y[i,:])
            degmtx_z[i,i]  = sum(adjmtx_z[i,:]) 
            
            
        Lapmtx[:]    = degmtx - adjmtx    
        Lapmtx_x     = degmtx_x - adjmtx_x
        Lapmtx_y     = degmtx_y - adjmtx_y
        Lapmtx_z     = degmtx_z - adjmtx_z
        
            
        Eval,Evec         = eig(Lapmtx)
        Eval_x,Evec_x     = eig(Lapmtx_x)
        Eval_y,Evec_y     = eig(Lapmtx_y)
        Eval_z,Evec_z     = eig(Lapmtx_z)   
        
        
        for rel_Btype in [True,False]:                        # ============================================================#
            N = 1000
            scale = 0.01       

            Err_all = np.zeros(N)
            Err_unrel = np.zeros(N)
            
            for gamma in range(1,N):   # ============================================================# 
                gamma = i*scale

                
#                foldername = 'opt_cor_'+repr(cor_th)+'_gam_'+repr(gamma)+'_adj_'+repr(adj_type)+'_relb_'+repr(rel_Btype)[0]
                titlename = 'opt_cor_'+repr(cor_th)+'_adj_'+repr(adj_type)+'_relb_'+repr(rel_Btype)[0]
                #cor_th : threshold of correlation 
                #gamma  : gamma value
                # adj type : whether it is adjmtx or adjmtx_th
                # relb     : reliability in binary or original value  
                print '==================================\n\n\n'
                print titlename
                print '\n\n\n=================================='                                         

                Err = 0
                unErr = 0
                unerr = 0
                uncnt = 0
                err = 0
                cnt = 0 
                
                for Kfile,Rfile,Mfile in zip(glob.glob(os.path.join(src_path+Kfolder,'*ex4.pkl')),\
                                             glob.glob(os.path.join(src_path+Rfolder,'*ex4.pkl')),\
                                             glob.glob(os.path.join(src_path+M2Kfolder,'*.h5'))):

    
                    
                    Kdata = cPickle.load(file(Kfile,'rb'))[12:30,:]
                    Mdata = h5py.File(Mfile)['data'][:]
#                    Mdata = cPickle.load(file(mfile,'rb'))[12:30,:]
                    Rdata = cPickle.load(file(Rfile,'rb'))[4:10,:]
                    unrelidx = np.where(np.sum((Rdata<Rel_th)*1,0)!=0)[0]   # frames which have unreliable  joints
                    
                    
                    Len = min(Kdata.shape[1],Mdata.shape[1])
                    Kdata = Kdata.reshape((-1,3,Len))    
                    Mdata = Mdata.reshape((-1,3,Len))
                    
                    corKdata = np.zeros(Kdata.shape)
                    corKdata += Kdata 
                    
                    for idx in unrelidx:
     
                        R = np.zeros(6)+Rdata[:,idx]
    
                        if rel_Btype == True: #binary the realibility
                           R[R>=Rel_th] = 1 
                           R[R< Rel_th] = 0

                        W = np.diag(R)
                        mx = np.matmul(np.matmul(inv(np.matmul(W.T,W)+gamma*Lapmtx_x),np.matmul(W.T,W)),Kdata[:,0,idx].reshape(6,-1))
                        my = np.matmul(np.matmul(inv(np.matmul(W.T,W)+gamma*Lapmtx_y),np.matmul(W.T,W)),Kdata[:,1,idx].reshape(6,-1))
                        mz = np.matmul(np.matmul(inv(np.matmul(W.T,W)+gamma*Lapmtx_z),np.matmul(W.T,W)),Kdata[:,2,idx].reshape(6,-1))
 
                               
                    uncnt += sum(R==0)
                    cnt += 6
                    unerr  += sum(abs(Mdata[R==0,0,idx]-mx[R==0].flatten()))
                    err  +=  sum(abs(Mdata[:,0,idx]-mx.flatten()))
                    
                Err = err/cnt
                unErr = unerr/uncnt
                
                Err_all[gamma/scale]   = Err
                Err_unrel[gamma/scale] = unErr
                
                
            fname ='./data/GSP/same/Err_'+titlename+'.pkl'
            f = h5py.File(fname,'w')
            f.create_dataset('all',data = Err_all)
            f.create_dataset('unrel',data = Err_unrel)
            f.create_dataset('scale_N',data = [scale,N])
            f.close()    

#                    pdb.set_trace()
#                    if not os.path.isdir('./data/GSP/'+foldername+'/'):
#                        print('\n\n\n')
#                        os.makedirs('./data/GSP/'+foldername+'/')
#                        
#                        
#                    fname ='./data/GSP/'+foldername+'/' +Kfile.split('\\')[-1][:-3]+'h5'
#                    f = h5py.File(fname,'w')
#                    f.create_dataset('data',data = corKdata)
#                    f.close()
#            
                
print('computation time is ' + repr(time.clock()-st))        
            
            
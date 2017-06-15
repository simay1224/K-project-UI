# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 16:54:12 2017

@author: medialab
"""

import cPickle,h5py,time
import numpy as np
import glob,os
from scipy.stats import pearsonr
from numpy.linalg import eig
from scipy.linalg import eig as seig
from numpy.linalg import norm

#src_path = 'I:/AllData_0327/unified data array/'
src_path = './data/unified data array/'
Mfolder  = 'Unified_MData/'
Kfolder  = 'Unified_KData/'
Rfolder  = 'reliability/'

Mfile = glob.glob(os.path.join(src_path+Mfolder,'*.pkl'))

Jnum   = 6   # joint number
Tnum   = 1   # time interval
sigma  = 20
Rel_th = 0.7
cor_th = 0.1



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
            corrmtx3[i,j,0,midx] = pearsonr(data[i,0,:],data[j,0,:])[0]
            corrmtx3[i,j,1,midx] = pearsonr(data[i,1,:],data[j,1,:])[0]
            corrmtx3[i,j,2,midx] = pearsonr(data[i,2,:],data[j,2,:])[0]
    ### calculate distant's weight between joints
    for idx in range(1,Jnum*Tnum/2+1):   # precisely should be np.round((Jnum*Tnum-1)/2.).astype('int')+1
        
        curRidx = np.roll(Ridx,-idx) 
        Diff = M - np.roll(M,-idx,axis = 0)
        Diff_abs = abs(Diff)
        L2   = np.mean((np.sum(Diff**2,axis = 1))**0.5,axis = 1)
        W    = np.exp(-L2/sigma**2)
        W_abs = np.mean(np.exp(-Diff_abs**2/sigma**2),axis = 2)
        for Lidx,(i,j) in enumerate(zip(Cidx,curRidx)):
            col = min(i,j)
            row = max(i,j)
            distmtx[col,row,midx]    = W[Lidx]
            distmtx3[col,row,0,midx] = W_abs[Lidx,0]
            distmtx3[col,row,1,midx] = W_abs[Lidx,1]
            distmtx3[col,row,2,midx] = W_abs[Lidx,2]

Rel_th = 0.7
st = time.clock()
corrmtx3[0,3,2,:][np.isnan(corrmtx3[0,3,2,:])] = 1  # L and R shoulder in Z axis's correlation
corrmtx3[np.isnan(corrmtx3)] = 0
         
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
            for gamma in [0,0.001,0.005,0.01,0.05,0.1,0.5]:   # ============================================================# 
                                           
                for Kfile,Rfile in zip(glob.glob(os.path.join(src_path+Kfolder,'*ex4.pkl')),glob.glob(os.path.join(src_path+Rfolder,'*ex4.pkl'))):
                    
                    print Kfile.split('\\')[-1][:-3]
                    print 'cor_'+repr(cor_th)+'_gam_'+repr(gamma)+'_adj_'+repr(adj_type)+'_relb_'+repr(rel_Btype)[0]
                    print '=================================='
                    
                    Kdata = cPickle.load(file(Kfile,'rb'))[12:30,:]
                    Rdata = cPickle.load(file(Rfile,'rb'))[4:10,:]
                    unrelidx = np.where(np.sum((Rdata<Rel_th)*1,0)!=0)[0]   # frames which have unreliable  joints
                    corKdata = np.zeros(Kdata.shape)
                    corKdata += Kdata 
                    
                    
                    
                    for idx in unrelidx:
                        x_coef = []
                        y_coef = []
                        z_coef = [] 
                        wn_x = []
                        wn_y = []
                        wn_z = []   
                        R = Rdata[:,idx]

                        if rel_Btype == True: #binary the realibility
                           R[R>=Rel_th] = 1 
                           R[R< Rel_th] = 0

#                        R = np.array([1,1,1,1,1,1])

                
                        for i in range(Jnum*Tnum):
                            wn_x.append(sum((R*Evec_x[:,i])**2))
                            wn_y.append(sum((R*Evec_y[:,i])**2))
                            wn_z.append(sum((R*Evec_z[:,i])**2))
                
                
                        for i in range(Jnum*Tnum):
                        
                            x_coef.append(sum(Kdata[0::3,idx]*Evec_x[:,i]*R**2)/norm(Evec_x[:,i]))   
                            y_coef.append(sum(Kdata[1::3,idx]*Evec_y[:,i]*R**2)/norm(Evec_y[:,i]))
                            z_coef.append(sum(Kdata[2::3,idx]*Evec_z[:,i]*R**2)/norm(Evec_z[:,i]))
                                
                        
                        
                        fx = np.zeros(6)
                        fy = np.zeros(6)
                        fz = np.zeros(6)
                        
                        for i in range(Jnum*Tnum):
                            fx += 1/(1+gamma*Eval_x[i])*x_coef[i]/wn_x[i]*Evec_x[:,i]
                            fy += 1/(1+gamma*Eval_y[i])*y_coef[i]/wn_y[i]*Evec_y[:,i]
                            fz += 1/(1+gamma*Eval_z[i])*z_coef[i]/wn_z[i]*Evec_z[:,i] 
                          
                        corKdata[0::3,idx] = fx
                        corKdata[1::3,idx] = fy
                        corKdata[2::3,idx] = fz
                
                    foldername = 'cor_'+repr(cor_th)+'_gam_'+repr(gamma)+'_adj_'+repr(adj_type)+'_relb_'+repr(rel_Btype)[0]
                    #cor_th : threshold of correlation 
                    #gamma  : gamma value
                    # adj type : whether it is adjmtx or adjmtx_th
                    # relb     : reliability in binary or original value
                
                    if not os.path.isdir('./data/GSP/'+foldername+'/'):
                        os.makedirs('./data/GSP/'+foldername+'/')
                        
                        
                    fname ='./data/GSP/'+foldername+'/' +Kfile.split('\\')[-1][:-3]+'h5'
                    f = h5py.File(fname,'w')
                    f.create_dataset('data',data = corKdata)
                    f.close()
            
                
print('computation time is ' + repr(time.clock()-st))        
            
            
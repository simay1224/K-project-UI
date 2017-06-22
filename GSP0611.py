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

#src_path = 'I:/AllData_0327/unified data array/'
src_path = './data/unified data array/'
Mfolder  = 'Unified_MData/'
Kfolder  = 'Unified_KData/'
Rfolder  = 'reliability/'

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
    

Rel_th = 0.7
gamma = 0


for Kfile,Rfile in zip(glob.glob(os.path.join(src_path+Kfolder,'*ex4.pkl')),glob.glob(os.path.join(src_path+Rfolder,'*ex4.pkl'))):
    print Kfile
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
        #R = Rdata[:,idx]
        R = np.array([1,1,1,1,1,1])
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


    
    
    
  
Mdata = cPickle.load(file(src_path+Mfolder+'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl','rb'))[12:30,:]    
Kdata = cPickle.load(file(src_path+Kfolder+'Andy_data201612151615_unified_ex4.pkl','rb'))[12:30,:]
Rdata = cPickle.load(file(src_path+Rfolder+'Andy_data201612151615_Rel_ex4.pkl','rb'))[4:10]

    
idx = 168

Kdata = Kdata.reshape((-1,3,Kdata.shape[1])) 
R = np.array([1.,1.,0.,1.,1.,1.])#Rdata[:,idx]#



#print sum(R*Evec_x[:,i])**2
#print np.matmul(np.matmul(np.matmul(Evec_x[:,i].T,R.reshape(-1,6).T),R.reshape(-1,6)),Evec_x[:,i])
#gamma = 0.02
X = []
Y = []
Z = []

Xth = []
Yth = []
Zth = []
N = 1000
scale = 0.01

for i in range(1,N):
    gamma = i*scale
    w_x = np.matmul(R,Evec_x)**2
    w_y = np.matmul(R,Evec_y)**2
    w_z = np.matmul(R,Evec_z)**2
    
    
    y_proj_x = np.matmul(Kdata[:,0,idx],Evec_x)
    y_proj_y = np.matmul(Kdata[:,1,idx],Evec_y)
    y_proj_z = np.matmul(Kdata[:,2,idx],Evec_z)
    x = np.sum(w_x/(w_x+gamma*Eval_x)*y_proj_x*Evec_x,axis = 1)
    y = np.sum(w_y/(w_y+gamma*Eval_y)*y_proj_y*Evec_y,axis = 1)
    z = np.sum(w_z/(w_z+gamma*Eval_z)*y_proj_z*Evec_z,axis = 1)
    X.append(x[2])
    Y.append(y[2])
    Z.append(z[2])
    
    
    #======================
    
    #gamma = 0.02
    
    w_xth = np.matmul(R,Evec_xth)**2
    w_yth = np.matmul(R,Evec_yth)**2
    w_zth = np.matmul(R,Evec_zth)**2
    
    
    y_proj_xth = np.matmul(Kdata[:,0,idx],Evec_xth)
    y_proj_yth = np.matmul(Kdata[:,1,idx],Evec_yth)
    y_proj_zth = np.matmul(Kdata[:,2,idx],Evec_zth)
    xth = np.sum(w_xth/(w_xth+gamma*Eval_xth)*y_proj_xth*Evec_xth,axis = 1)
    yth = np.sum(w_yth/(w_yth+gamma*Eval_yth)*y_proj_yth*Evec_yth,axis = 1)
    zth = np.sum(w_zth/(w_zth+gamma*Eval_zth)*y_proj_zth*Evec_zth,axis = 1)
    Xth.append(xth[2])
    Yth.append(yth[2])
    Zth.append(zth[2])

import matplotlib.pyplot as plt
plt.figure(1)
plt.title('normal')
ax1 = plt.subplot(3,1,1)
ax1.set_title('X')
plt.plot(np.arange(N-1)*scale,X,color = 'blue')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*Kdata[2,0,idx],color = 'red')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*-25,color = 'green')

ax2 = plt.subplot(3,1,2)
ax2.set_title('Y')
plt.plot(np.arange(N-1)*scale,Y,color = 'blue')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*Kdata[2,1,idx],color = 'red')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*347,color = 'green')


ax3 = plt.subplot(3,1,3)
ax3.set_title('Z')
plt.plot(np.arange(N-1)*scale,Z,color = 'blue')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*Kdata[2,2,idx],color = 'red')
plt.plot(np.arange(N-1)*scale,np.ones(N-1)*-148.5,color = 'green')
plt.show()

#plt.xlabel('gamma value')
#plt.plot(np.arange(N-1)*0.01,X,color = 'blue')
#plt.plot(np.arange(N-1)*0.01,np.ones(N-1)*Kdata[2,0,idx],color = 'red')
#plt.plot(np.arange(N-1)*0.01,Y,color = 'red')
#plt.plot(np.arange(N-1)*0.01,Z,color = 'green')

plt.figure(2)
plt.title('only connected joint')
plt.xlabel('gamma value')
plt.plot(np.arange(N-1)*0.01,Xth,color = 'blue')
plt.plot(np.arange(N-1)*0.01,Yth,color = 'red')
plt.plot(np.arange(N-1)*0.01,Zth,color = 'green')

plt.show()

#======================

x =np.zeros(6)
for i in range(6):
    x +=  w_x[i]/(w_x[i]+Eval_x[i]*gamma)*sum(Kdata[:,0,idx]*Evec_x[:,i])*Evec_x[:,i]      

print x

#========================






W = np.diag(R)
y = Kdata[:,0,idx].reshape(6,-1) 
WtW = np.matmul(W.T,W)

h = np.matmul(inv(WtW+gamma*Lapmtx_x),WtW)

x_opt = np.matmul(h,y)

#x_opt = np.matmul(np.matmul(inv(np.matmul(W.T,W)+gamma*Lapmtx_x),np.matmul(W.T,W)),Kdata[:,0,idx].reshape(6,-1))

print x_opt
          






#=======================================================================

#XX = []
#for i in range(1,1000):
#    print i 
#    gamma = i *0.01
#    
#    try:
#        x = np.matmul(inv(gamma*Lapmtx_x+np.matmul(R.T,R)),np.matmul(np.matmul(R.T,R), Kdata[:,0,idx]))
#        XX.append(x[2])
#    except:        
#        XX.append(-99.)
#
#XX= np.array(XX)
#
#import matplotlib.pyplot as plt
#x = np.arange(1,1000,10)
#y = np.ones(len(x))*Kdata[2,0,idx]
#
##XX[XX>10]=10
##XX[XX<-70]=-70
#
##plt.plot(x*0.1,XX[0::10])
##plt.plot(x*0.1,y,color='red')
#
#plt.scatter(x*0.1,XX[0::10])
#plt.plot(x*0.1,y,color='red')
#plt.ylim([-60,10])
#plt.show()





#=======================================================================





#
#
#
#x_coef = []
#y_coef = []
#z_coef = []
#wn_x = []
#wn_y = []
#wn_z = []
#
#for i in range(Jnum*Tnum):
#    wn_x.append(sum((R*Evec_x[:,i])**2))
#    wn_y.append(sum((R*Evec_y[:,i])**2))
#    wn_z.append(sum((R*Evec_z[:,i])**2))
#    
##    wn_x +=  sum(((R*Evec_x)[:,i])**2)
##    wn_y +=  sum(((R*Evec_y)[:,i])**2)
##    wn_z +=  sum(((R*Evec_z)[:,i])**2)
#
#for i in range(Jnum*Tnum):
#
#    x_coef.append(sum(Kdata[0::3,idx]*Evec_x[:,i]*R**2)/norm(Evec_x[:,i]))   
#    y_coef.append(sum(Kdata[1::3,idx]*Evec_y[:,i]*R**2)/norm(Evec_y[:,i]))
#    z_coef.append(sum(Kdata[2::3,idx]*Evec_z[:,i]*R**2)/norm(Evec_z[:,i]))
#
#gamma = 0.1
#fx = np.zeros(6)
#fy = np.zeros(6)
#fz = np.zeros(6)
#
#for i in range(Jnum*Tnum):
#    fx += 1/(1+gamma*Eval_x[i])*x_coef[i]/wn_x[i]*Evec_x[:,i]
#    fy += 1/(1+gamma*Eval_y[i])*y_coef[i]/wn_y[i]*Evec_y[:,i]
#    fz += 1/(1+gamma*Eval_z[i])*z_coef[i]/wn_z[i]*Evec_z[:,i]
#
#
#
#np.sum(((fx -Kdata[0::3,idx])*R)**2)**0.5
#np.matmul(np.matmul(fx.reshape(-1,6),Lapmtx_x),fx.reshape(6,-1))




#
#for i in range(Jnum*Tnum):
#    x_coef.append(sum(Kdata[0::3,idx]*Evec_x[:,i])/norm(Evec_x[:,i]))   
#    y_coef.append(sum(Kdata[1::3,idx]*Evec_y[:,i])/norm(Evec_y[:,i]))
#    z_coef.append(sum(Kdata[2::3,idx]*Evec_z[:,i])/norm(Evec_z[:,i]))
#
#
#gamma = 0.01
#fx = np.zeros(6)
#fy = np.zeros(6)
#fz = np.zeros(6)
#
#for i in range(Jnum*Tnum):
#    fx += (1/(1+gamma*Eval_x)*x_coef)[i]*Evec_x[:,i]
#    fy += (1/(1+gamma*Eval_y)*y_coef)[i]*Evec_y[:,i]
#    fz += (1/(1+gamma*Eval_z)*z_coef)[i]*Evec_z[:,i]
#    
    
#import h5py
#f = h5py.File('evec.h5','w')
#f.create_dataset('data_x',data=Evec_x)    
#f.create_dataset('data_y',data=Evec_y)
#f.create_dataset('data_z',data=Evec_z)    
#f.close()    
    
#============================================================================   
#
#from scipy import optimize
#Mdata = cPickle.load(file(src_path+Mfolder+'Andy_2016-12-15 04.15.27 PM_ex4_FPS30_motion_unified.pkl','rb'))[12:30,:]    
#Kdata = cPickle.load(file(src_path+Kfolder+'Andy_data201612151615_unified_ex4.pkl','rb'))[12:30,:]
#Rdata = cPickle.load(file(src_path+Rfolder+'Andy_data201612151615_Rel_ex4.pkl','rb'))[4:10]
#
#    
#idx = 219    
#    
#def func(X,u,Y,R,R_b,Lx,Ly,Lz):
#    Y  = Y.reshape((6,3))
#    X  = X.reshape((6,3))
#    Lx = Lx.reshape((6,6))
#    Ly = Ly.reshape((6,6))
#    Lz = Lz.reshape((6,6))
#    return   (np.matmul(np.matmul((X[:,0]-Y[:,0]).T,np.diag(R_b)), (X[:,0]-Y[:,0]))**2+\
#              np.matmul(np.matmul((X[:,1]-Y[:,1]).T,np.diag(R_b)), (X[:,1]-Y[:,1]))**2+\
#              np.matmul(np.matmul((X[:,2]-Y[:,2]).T,np.diag(R_b)), (X[:,2]-Y[:,2]))**2)**0.5+\
#          u*((np.matmul(np.matmul(np.matmul(X[:,0].T,Lx),(2-np.diag(R))),X[:,0])**2+\
#              np.matmul(np.matmul(np.matmul(X[:,1].T,Ly),(2-np.diag(R))),X[:,1])**2+\
#              np.matmul(np.matmul(np.matmul(X[:,2].T,Lz),(2-np.diag(R))),X[:,2])**2)**0.5)
#          
##    return   (np.matmul(np.matmul((X[:,0]-Y[:,0]).T,np.diag(R)), (X[:,0]-Y[:,0]))**2+\
##              np.matmul(np.matmul((X[:,1]-Y[:,1]).T,np.diag(R)), (X[:,1]-Y[:,1]))**2+\
##              np.matmul(np.matmul((X[:,2]-Y[:,2]).T,np.diag(R)), (X[:,2]-Y[:,2]))**2)**0.5+\
##          u*((np.matmul(np.matmul(X[:,0].T,Lx),X[:,0])**2+\
##              np.matmul(np.matmul(X[:,1].T,Ly),X[:,1])**2+\
##              np.matmul(np.matmul(X[:,2].T,Lz),X[:,2])**2)**0.5)
#    
#    
#def pos_est(fidx,Kv,Ka,Kdata):
#    return Kdata[:,:,fidx]+Kv[:,:,fidx]+Ka[:,:,fidx] 
#
#Kdata3 = Kdata.reshape((-1,3,Kdata.shape[1]))    
#Kv    = Kdata3 - np.roll(Kdata3,1,axis = 2) 
#Ka    = Kv - np.roll(Kv,1,axis = 2)    
#    
#R = Rdata[:,idx]# np.array([1,1,0,1,1,1])#  
#R_b = np.zeros(R.shape) 
#Rel_th = 0.7    
#R_b[R>=Rel_th] = 1     
# 
#
#X_init   = pos_est(idx,Kv,Ka,Kdata3)
#x =  optimize.fmin_bfgs(func, X_init.flatten() ,args = (0.001,Kdata[:,idx].flatten(),R,R_b,Lapmtx_x.flatten(),Lapmtx_y.flatten(),Lapmtx_z.flatten(),)) 
#
#x = x.reshape(-1,3)  
#
#xx =  optimize.fmin_bfgs(func, X_init.flatten() ,args = (0.001,Kdata[:,idx].flatten(),R,R_b,Lapmtx_xth.flatten(),Lapmtx_yth.flatten(),Lapmtx_zth.flatten(),)) 
#
#xx = xx.reshape(-1,3)
#
#print Kdata[0::3,idx]
#print x[:,0]
#print xx[:,0]
#
#
#
#
#
#
#
#

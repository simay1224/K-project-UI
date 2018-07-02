# -*- coding: utf-8 -*-
"""
Created on Sun Oct 01 16:51:05 2017

@author: medialab
"""
import numpy as np
from scipy.spatial.distance import  cdist


def cov(sita0,sita1,W1,W2,noise_level,x1,x2):
    
    dists1 = cdist(x1 / W1, x2 / W1,metric='sqeuclidean')
    dists2 = cdist(x1 / W2, x2 / W2,metric='sqeuclidean')
       
        
    k1=np.exp(-.5 * dists1) 
    k2=np.exp(-.5 * dists2)
    k_return=sita0*k1+sita1*k2
    if np.array_equal(x1,x2):
        k_return=k_return+noise_level
    return k_return



def gp_pred(testdata,gp):
    
    #===== find the parameter of gp =====
    parameter=gp.kernel_.get_params(deep=True)
    sita0 = parameter["k1__k1__k1__constant_value"]
    W1    = parameter["k1__k1__k2__length_scale"]
    sita1 = parameter["k1__k2__k1__constant_value"]
    W2    = parameter["k1__k2__k2__length_scale"]
    noise_level = parameter["k2__noise_level"] 
    traindata = gp.X_train_

#    L_    = gp.L_
#    L_inv = np.linalg.inv(L_)
    alpha_= gp.alpha_
    y_train_mean = gp.y_train_mean
    
    #===== Prediction ======
    K_trans = cov(sita0,sita1,W1,W2,noise_level,testdata,traindata)    
#    k1      = cov(sita0,sita1,W1,W2,noise_level,testdata,testdata)    
#    v       = np.dot(L_inv,K_trans.T)             
#    y_cov   = k1-K_trans.dot(v)
    y_mean  = K_trans.dot(alpha_)  
    
    return y_train_mean + y_mean 
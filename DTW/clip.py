# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 21:46:04 2017

@author: Dawnknight
"""

import numpy as np
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy.interpolate import interp1d

 
def clip(data,idx = 6,N_add = 20, N_interp1 = 40,N_interp2 = 48):
    
    apddata  = np.append(np.append(np.ones(N_add)*data[0,idx],data[:,idx]),np.ones(N_add)*data[-1,idx])
    smthdata = gf(apddata,8)
    grad2    = np.gradient(np.gradient(smthdata))
    clip_pts = [0,max(4,min(np.argmax(grad2) , np.argmin(grad2))-N_add),\
                min(data.shape[0]-5,max(np.argmax(grad2) , np.argmin(grad2))-N_add),data.shape[0]-1]
    #
    interp = np.zeros((N_interp1*2+N_interp2,21))
    idx = [[0,N_interp1],[N_interp1,N_interp1+N_interp2],[N_interp1+N_interp2,N_interp1*2+N_interp2]]
    for k in range(3) :
        x_ori    = np.linspace(clip_pts[k],clip_pts[k+1]-1,num = clip_pts[k+1]-clip_pts[k])
        if k == 1 :
            x_interp = np.linspace(clip_pts[k],clip_pts[k+1]-1,num = N_interp2)    
        else:
            x_interp = np.linspace(clip_pts[k],clip_pts[k+1]-1,num = N_interp1)
        y        = interp1d(x_ori , data[clip_pts[k]:clip_pts[k+1],:].T,'cubic')
        interp[idx[k][0]:idx[k][1]]   = y(x_interp).T
        
    return  interp   

    
#def clip(data,idx = 6,N_add = 20, N_interp = 40):
#    
#    apddata  = np.append(np.append(np.ones(N_add)*data[0,idx],data[:,idx]),np.ones(N_add)*data[-1,idx])
#    smthdata = gf(apddata,8)
#    grad2    = np.gradient(np.gradient(smthdata))
#    clip_pts = [0,max(0,min(np.argmax(grad2) , np.argmin(grad2))-N_add),\
#                min(data.shape[0]-1,max(np.argmax(grad2) , np.argmin(grad2))-N_add),data.shape[0]-1]
#    #
#    interp = np.zeros((N_interp*3,21))
#    idx = [[0,N_interp],[N_interp,N_interp*2],[N_interp*2,N_interp*3]]
#    for k in range(3) :
#        x_ori    = np.linspace(clip_pts[k],clip_pts[k+1]-1,num = clip_pts[k+1]-clip_pts[k])
#
#        x_interp = np.linspace(clip_pts[k],clip_pts[k+1]-1,num = N_interp)
#        y        = interp1d(x_ori , data[clip_pts[k]:clip_pts[k+1],:].T,'cubic')
#        interp[idx[k][0]:idx[k][1]]   = y(x_interp).T
#
#    x_ori   = np.linspace(0,interp.shape[0]-1,num = interp.shape[0])
#    x_interp = np.linspace(0,interp.shape[0]-1,num = 128)
#    y = interp1d(x_ori,interp.T,'cubic')
#    interp = y(x_interp).T
#
#       
#    return  interp      
    
    
    
    
    
    
    
    



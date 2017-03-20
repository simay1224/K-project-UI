# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:47:51 2017

@author: medialab
"""

from Mocam2Kinect import *
from Human_mod import *
from rawK2array import *
import cPickle
import numpy as np
import glob,os,win32com.client
from scipy.ndimage.filters import gaussian_filter1d as gf



src_path = 'H:/20170306/Andy/'
dst_path = 'D:/Project/K_project/data/Motion and Kinect/Unified_KData/'
jidx = [0,1,2,3,4,5,6,8,9,10,20]

def folder_retarget(src_path,shortcut):  
    shell = win32com.client.Dispatch("WScript.Shell")    
    return str(shell.CreateShortCut(src_path+shortcut).Targetpath)

def pre_smooth(Kbody,shape,sigma =3):
    for i in Kbody.keys():
        
        Mean = np.tile(np.mean(Kbody[i],axis = 1).reshape((3,-1)),(1,shape[1]))
        Std  = np.tile(np.std(Kbody[i],axis = 1).reshape((3,-1)),(1,shape[1]))
        Kbody[i] = gf((Kbody[i]-Mean)/Std,sigma ,axis = 1)*Std+Mean

    return Kbody
        

for subfolder in os.listdir(src_path):   
    if '.lnk' in subfolder:
        path = folder_retarget(src_path,subfolder)
        filelist = glob.glob(os.path.join(path, '*.pkl') ) # find all pkl files
    else:
        filelist = glob.glob(os.path.join(src_path+subfolder, '*.pkl') ) # find all pkl files
    
    for infile in filelist:
        print infile
        data = cPickle.load(file(infile,'rb'))        
        Kbody = rawK2ary(data,jidx)
        Kbody = pre_smooth(Kbody,Kbody[0].shape)
        
        J     = human_mod(Kbody)        
        
        name = infile.split('\\')[-1].split('ex')
        fname = dst_path + name[0]+'unified_ex'+name[1]
    
    
        cPickle.dump(J,file(fname,'wb'))
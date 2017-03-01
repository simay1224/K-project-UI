# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 16:13:39 2017

@author: medialab
"""
from Kfunc import *
from Kfunc.model import *
import cPickle
import numpy as np
import glob,os,win32com.client
    



mainpath = 'E:/20170224/Kinect data _ h5 and pkl file/'
savepath = 'D:/Project/PyKinect2-master/Kproject/data/Motion and Kinect/Unified_KData/'
jidx = [0,1,2,3,4,5,6,8,9,10,20]

def folder_retarget(mainpath,shortcut):  
    shell = win32com.client.Dispatch("WScript.Shell")    
    return str(shell.CreateShortCut(mainpath+shortcut).Targetpath)


for subfolder in os.listdir(mainpath):   
    if '.lnk' in subfolder:
        path = folder_retarget(mainpath,subfolder)
        filelist = glob.glob(os.path.join(path, '*.pkl') ) # find all pkl files
    else:
        filelist = glob.glob(os.path.join(mainpath+subfolder, '*.pkl') ) # find all pkl files
    
    for infile in filelist:
        print infile
        data = cPickle.load(file(infile,'rb'))
        Kbody = rawK2ary(data,jidx)
        J     = human_mod(Kbody)        
        
        name = infile.split('\\')[-1].split('ex')
        fname = savepath + name[0]+'unified_ex'+name[1]


        cPickle.dump(J,file(fname,'wb'))
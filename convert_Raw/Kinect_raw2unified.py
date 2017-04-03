# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 16:13:39 2017

@author: medialab
"""
from Mocam2Kinect import *
from Human_mod import *
from rawK2array import *
import cPickle
import numpy as np
import glob,os,win32com.client,pdb
    



src_path = 'F:/AllData_0322/raw data/20161216/pkl/'
dst_path = 'F:/AllData_0322/1216/'
jidx = [0,1,2,3,4,5,6,8,9,10,20]

def folder_retarget(src_path,shortcut):  
    shell = win32com.client.Dispatch("WScript.Shell")    
    return str(shell.CreateShortCut(src_path+shortcut).Targetpath)


for subfolder in os.listdir(src_path):   
    if '.lnk' in subfolder:
        path = folder_retarget(src_path,subfolder)
        filelist = glob.glob(os.path.join(path, '*.pkl') ) # find all pkl files
    else:
        filelist = glob.glob(os.path.join(src_path+subfolder, '*.pkl') ) # find all pkl files
#    pdb.set_trace()
    for infile in filelist:
        print infile
        data = cPickle.load(file(infile,'rb'))
        Kbody = rawK2ary(data,jidx)
        J     = human_mod(Kbody)        
        
        name = infile.split('\\')[-1].split('ex')
        fname = dst_path + name[0]+'unified_ex'+name[1]
    
    
        cPickle.dump(J,file(fname,'wb'))
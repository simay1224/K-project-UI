# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 13:30:59 2017

@author: medialab
"""

'''
 convert original kinect data to unified array data
 
 
'''
import cPickle,glob,os
import numpy as np
from Mocam2Kinect import *
from Human_mod import *
from rawK2array import *

src_path = './input/'
dst_path = './output/'

jidx = [0,1,2,3,4,5,6,8,9,10,20]
jnum = 11

for infile in glob.glob(os.path.join(src_path,'*.pkl')):
    print infile
    data  = cPickle.load(file(infile,'rb'))    
    Kbody = rawK2ary(data,jidx)
    kdata = human_mod(Kbody)
    
    Kary  = np.zeros((jnum*3,kdata[20].shape[1]))
    for kidx, i in enumerate(kdata.keys()):
        Kary[3*kidx:3*(kidx+1),:] = kdata[i]
       
    name  = infile.split('\\')[-1].split('ex')        
    kname = name[0]+'unified_ex'+name[1]        
    cPickle.dump(Kary,file(dst_path+kname,'wb'))       
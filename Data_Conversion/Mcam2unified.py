# -*- coding: utf-8 -*-
"""
Created on Tue Mar 07 21:26:39 2017

@author: medialab
"""

from Mocam2Kinect import *
from Human_mod import *
import cPickle

import os,glob

src_path = 'H:/20170306/Converted_Data/'

filelist = glob.glob(os.path.join(src_path, '*.pkl'))

dst_path = 'H:/20170306/Unified_MData/'

for infile in filelist:
    print infile   
    data = cPickle.load(file(infile,'r'))
    pos_Kinect = Mocam2Kinect(data)
    Pos_Unified = human_mod(pos_Kinect)
    
    fname = dst_path+infile.split('\\')[-1]+ '_unified.pkl'
    cPickle.dump(Pos_Unified,file(fname,'wb'))
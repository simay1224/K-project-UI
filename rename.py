# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 14:02:05 2017

@author: medialab
"""

import os

path = 'I:/Unified_MData'

for filename in os.listdir(path):
    if '_unified.pkl' in filename:
        print filename
        name = filename.split('_')
        fname = name[0]+'_'+name[1]+ '_'+name[2]+ '_'+name[3]+ '_'+name[5][:-4]+ '_'+name[4]+ '.pkl'
#        fname = name[0]+'unified_ex'+name[1]
        os.rename(filename, fname)
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 14:02:05 2017

@author: medialab
"""

import os

path = 'D:/Project/PyKinect2-master/Kproject/data/Motion and Kinect/Unified_KData'

for filename in os.listdir(path):
    if 'unified' not in filename:
        print filename
        name = filename.split('\\')[-1].split('ex')
        fname = name[0]+'unified_ex'+name[1]
        os.rename(filename, fname)
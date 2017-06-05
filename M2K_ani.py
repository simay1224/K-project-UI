# -*- coding: utf-8 -*-
"""
Created on Sun Jun 04 21:43:57 2017

@author: Dawnknight
"""

import cv2
import cPcikle
#from pykinect2 import PyKinectV2
#from pykinect2.PyKinectV2 import *

vid_src = 'Andy_data12151615.avi'
dst_path = './data/frame/'
vid     = cv2.VideoCapture(vid_src)

Width     = vid.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
Height    = vid.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
FPS       = vid.get(cv2.cv.CV_CAP_PROP_FPS) 
Nframe    = vid.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)

Kdata ='./data/rawdata/Kdata/Andy_data12151615_ex4.pkl'
Mdata ='./data/rawdata/Mdata/'


count = 0

while count<Nframe:
    
    ret, frame = vid.read()
    fname = dst_path+'frame'+repr(count).zfill(4)+'.jpg'
    cv2.imwrite(fname,frame)
    count += 1



    
    
vid.release()
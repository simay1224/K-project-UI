# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 17:28:16 2016

@author: medialab
"""
import scipy.ndimage.morphology as ndm
import numpy as np

def handseg(frame_in,hw,hc, w = 1920, h = 1080 ):
    '''
    segment hand region
    input frame : type binary
    hc : hand center        
    '''
    rad =  int(((hw.x-hc.x)**2+(hw.y-hc.y)**2)**0.5)*2
    xul =  max(int(hc.x)-rad,0)
    yul =  max(int(hc.y)-rad,0)
    xlr =  min(int(hc.x)+rad,w)
    ylr =  min(int(hc.y)+rad,h)
 
    hand = ndm.binary_opening(frame_in[yul:ylr,xul:xlr],structure=np.ones((5,5))).astype(np.uint8) #hand closing

    #cv2.imshow('hand',hand*255)
    #cv2.waitKey()

    return hand , (xul,yul),rad  
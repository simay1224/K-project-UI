# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 12:55:31 2016

@author: medialab
"""
import cv

def convert2vid(bdjoints,fimgs,fps,Vtype=0):
    
    # Vtype : 0 : color m, 1: depth ,2: body index
    if Vtype == 0 :
        fsize = (1920,1080)
        extname = ''
    elif Vtype == 1:
        fsize = (512,424)
        extname = 'dp'
    else:
        fsize = (512,424)
        extname = 'bdidx'
               
    #now = datetime.datetime.now()        
    vid = 'kinect'+repr(now.month).zfill(2)+repr(now.day).zfill(2)+repr(now.hour).zfill(2)+repr(now.minute).zfill(2)+'_'+extname+'.avi'        
    video = cv.CreateVideoWriter(vid, cv.CV_FOURCC('L','A','G','S'), fps, fsize,True)
    print 'making video .....'

    for i in fimgs:
        bitmap = cv.CreateImageHeader(fsize, cv.IPL_DEPTH_8U, 3)                
        cv.SetData(bitmap, i.tostring(),i.dtype.itemsize * 3 * i.shape[1])                
        cv.WriteFrame(video,bitmap)  
    print 'there r total '+repr(len(fimgs))+' frames'
    del video
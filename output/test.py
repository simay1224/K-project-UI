# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 19:40:58 2016

@author: medialab
"""

import h5py,cv,glob
fps = 30


f = h5py.File('./Andy/data12151611.h5','r')
size = (1920,1080)
video = cv.CreateVideoWriter('data12151611'+'.avi', -1, fps, size,True)
cimg = f['imgs']['cimgs']
#        elif i == 1:
#            size = (512,424)
#            video = cv.CreateVideoWriter(data[:-3]+'_dp.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
#            cimg = f['imgs']['dimgs']
#        else:
#            size = (512,424)
#            video = cv.CreateVideoWriter(data[:-3]+'_bdidx.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
#            cimg = f['imgs']['bdimgs']
    

for i in cimg.keys():
    bitmap = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)                
    cv.SetData(bitmap, cimg[i][:].tostring(),cimg[i][:].dtype.itemsize * 3 * cimg[i][:].shape[1])                
    cv.WriteFrame(video,bitmap)      
del video    

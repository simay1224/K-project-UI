# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 13:33:40 2017

@author: medialab
"""

import h5py,os,glob,win32com.client,cv
import numpy as np

#src_path = 'H:/20170306/Kinect/'
#dst_path = 'D:/20170306/Kinect/avi/'

src_path = 'D:/Project/K_project/convert_Raw/'
dst_path = 'D:/Project/K_project/convert_Raw/'

fps = 30


def folder_retarget(src_path,shortcut):  
    shell = win32com.client.Dispatch("WScript.Shell")    
    return str(shell.CreateShortCut(src_path+shortcut).Targetpath)

for subfolder in os.listdir(src_path):   
    if '.lnk' in subfolder:
        path = folder_retarget(src_path,subfolder)
        filelist = glob.glob(os.path.join(path, '*.h5') ) # find all pkl files        
    else:
        filelist = glob.glob(os.path.join(src_path+subfolder, '*.h5') ) # find all pkl files        
        
    for infile in filelist:
        print infile
        File = infile.split('\\')[-1][:-3]
        
        f = h5py.File(infile, "r")

        if len(f['imgs'].keys()) == 2:

            for j in xrange(2):
                if j == 0:
                    size = (512,424)
                    
                    video = cv.CreateVideoWriter(savepath+File+'_bdidx.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
                    cimg = f['imgs']['bdimgs']
                else:
                    size = (512,424)
                    video = cv.CreateVideoWriter(savepath+File+'_d.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
                    cimg = f['imgs']['dimgs']        
            
                for i in cimg.keys():
                    bitmap = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
                    if j == 1: 
                        cv.SetData(bitmap, np.uint8(cimg[i][:]/256.).tostring(),np.uint8(cimg[i][:]/256.).dtype.itemsize * 3 * cimg[i][:].shape[1])    
                    else:             
                        cv.SetData(bitmap, cimg[i][:].tostring(),cimg[i][:].dtype.itemsize * 3 * cimg[i][:].shape[1])                
                    cv.WriteFrame(video,bitmap)      
                del video   
            
                
        elif len(f['imgs'].keys()) ==3:


            for j in xrange(3):
                if j == 0 :
                    size = (1920,1080)
                    video = cv.CreateVideoWriter(savepath+subfolder+'_'+File+'.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
                    cimg = f['imgs']['cimgs']
                elif j == 1:
                    size = (512,424)
                    video = cv.CreateVideoWriter(savepath+subfolder+'_'+File+'_bdidx.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
                    cimg = f['imgs']['bdimgs']
                else:
                    size = (512,424)
                    video = cv.CreateVideoWriter(savepath+subfolder+'_'+File+'_d.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
                    cimg = f['imgs']['dimgs']        
            
                for i in cimg.keys():
                    bitmap = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
                    if j == 2: 
                        cv.SetData(bitmap, np.uint8(cimg[i][:]/256.).tostring(),np.uint8(cimg[i][:]/256.).dtype.itemsize * 3 * cimg[i][:].shape[1])    
                    else:             
                        cv.SetData(bitmap, cimg[i][:].tostring(),cimg[i][:].dtype.itemsize * 3 * cimg[i][:].shape[1])                
                    cv.WriteFrame(video,bitmap)      
                del video   

            
        else:
            print('Error !!')
    


#for infile in glob.glob(os.path.join(src_path, '*.h5') ):
#        print infile
#        File = infile.split('\\')[-1][:-3]
#        
#        f = h5py.File(infile, "r")
#
#        if len(f['imgs'].keys()) == 2:
#
#            for j in xrange(2):
#                if j == 0:
#                    size = (512,424)
#                    
#                    video = cv.CreateVideoWriter(dst_path+File+'_bdidx.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
#                    cimg = f['imgs']['bdimgs']
#                else:
#                    size = (512,424)
#                    video = cv.CreateVideoWriter(dst_path+File+'_d.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
#                    cimg = f['imgs']['dimgs']        
#            
#                for i in cimg.keys():
#                    bitmap = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
#                    if j == 1: 
#                        cv.SetData(bitmap, np.uint8(cimg[i][:]/256.).tostring(),np.uint8(cimg[i][:]/256.).dtype.itemsize * 3 * cimg[i][:].shape[1])    
#                    else:             
#                        cv.SetData(bitmap, cimg[i][:].tostring(),cimg[i][:].dtype.itemsize * 3 * cimg[i][:].shape[1])                
#                    cv.WriteFrame(video,bitmap)      
#                del video   
#            
#                
#        elif len(f['imgs'].keys()) ==3:
#
#
#            for j in xrange(3):
#                if j == 0 :
#                    size = (1920,1080)
#                    video = cv.CreateVideoWriter(dst_path+File+'.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
#                    cimg = f['imgs']['cimgs']
#                elif j == 1:
#                    size = (512,424)
#                    video = cv.CreateVideoWriter(dst_path+File+'_bdidx.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
#                    cimg = f['imgs']['bdimgs']
#                else:
#                    size = (512,424)
#                    video = cv.CreateVideoWriter(dst_path+File+'_d.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
#                    cimg = f['imgs']['dimgs']        
#            
#                for i in cimg.keys():
#                    bitmap = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
#                    if j == 2: 
#                        cv.SetData(bitmap, np.uint8(cimg[i][:]/256.).tostring(),np.uint8(cimg[i][:]/256.).dtype.itemsize * 3 * cimg[i][:].shape[1])    
#                    else:             
#                        cv.SetData(bitmap, cimg[i][:].tostring(),cimg[i][:].dtype.itemsize * 3 * cimg[i][:].shape[1])                
#                    cv.WriteFrame(video,bitmap)      
#                del video   
#
#            
#        else:
#            print('Error !!')
#            
#

# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 21:27:47 2017

@author: medialab
"""

#import h5py,os,glob,win32com.client
#
#mainpath = 'E:/20170224/Kinect data _ h5 and pkl file/'
#savepath  = 'D:/20170224/Kinect/save/'
#
#def folder_retarget(mainpath,shortcut):  
#    shell = win32com.client.Dispatch("WScript.Shell")    
#    return str(shell.CreateShortCut(mainpath+shortcut).Targetpath)
#
#for subfolder in os.listdir(mainpath):   
#    if '.lnk' in subfolder:
#        path = folder_retarget(mainpath,subfolder)
#        filelist = glob.glob(os.path.join(path, '*.h5') ) # find all pkl files        
#    else:
#        filelist = glob.glob(os.path.join(mainpath+subfolder, '*.h5') ) # find all pkl files        
#        
#    for infile in filelist:
#        print infile
#        File = infile.split('\\')[-1][:-3]
#        Compdata = h5py.File(savepath+File+'_c.h5', "w")
#        imgs = Compdata.create_group('imgs')
#        dimgs = imgs.create_group('dimgs')
#        bdimgs = imgs.create_group('bdimgs')
#        
#        data = h5py.File(infile, "r")['imgs']
#
#        if len(data.keys()) == 2:
#            for i in xrange(len(data['bdimgs'].keys())):
#                print i 
#                bdimgs.create_dataset('bd_'+repr(i).zfill(4), data = data['bdimgs']['bd_'+repr(i).zfill(4)][:],compression="gzip", compression_opts=9)
#                dimgs.create_dataset('d_'+repr(i).zfill(4), data = data['dimgs']['d_'+repr(i).zfill(4)][:],compression="gzip", compression_opts=9)
#                
#        elif len(data.keys()) ==3:
#            cimgs = imgs.create_group('cimgs') 
#            for i in xrange(len(data['bdimgs'].keys())):
#                print i 
#                cimgs.create_dataset('c_'+repr(i).zfill(4), data = data['cimgs']['img_'+repr(i).zfill(4)][:],compression="gzip", compression_opts=9)
#                bdimgs.create_dataset('bd_'+repr(i).zfill(4), data = data['bdimgs']['bd_'+repr(i).zfill(4)][:],compression="gzip", compression_opts=9)
#                dimgs.create_dataset('d_'+repr(i).zfill(4), data = data['dimgs']['d_'+repr(i).zfill(4)][:],compression="gzip", compression_opts=9)
#        else:
#            print('Error !!')
#    
#    Compdata.close()




File = 'E:/20161216/Kinect data _ h5 and pkl file/data12151611_c.h5'
import h5py,cv,glob,pdb
import numpy as np


fps = 30


f = h5py.File(File,'r')
for j in xrange(2,3):
    if j == 0 :
        size = (1920,1080)
        video = cv.CreateVideoWriter('test.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
        cimg = f['imgs']['cimgs']
    elif j == 1:
        size = (512,424)
        video = cv.CreateVideoWriter('test_bdidx.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
        cimg = f['imgs']['bdimgs']
    else:
        size = (512,424)
        video = cv.CreateVideoWriter('test_d.avi', cv.CV_FOURCC('X','V','I','D'), fps, size,True)
        cimg = f['imgs']['dimgs']        

    for i in cimg.keys():
        print i
        bitmap = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
#        pdb.set_trace()
        if j == 2: 
            cv.SetData(bitmap, np.uint8(cimg[i][:]/256.).tostring(),np.uint8(cimg[i][:]/256.).dtype.itemsize * 3 * cimg[i][:].shape[1])    
        else:             
            cv.SetData(bitmap, cimg[i][:].tostring(),cimg[i][:].dtype.itemsize * 3 * cimg[i][:].shape[1])                
        cv.WriteFrame(video,bitmap)      
    del video   




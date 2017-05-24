# -*- coding: utf-8 -*-
"""
Created on Sun May 21 13:57:19 2017

@author: Dawnknight
"""
import os , glob , cPickle
import numpy as np


#src_path  = 'I:/AllData_0327/unified data/'
#dst_path  = 'I:/AllData_0327/unified data array/'

src_path  = 'D:/Project/K_project/data/Motion and Kinect unified/'
dst_path  = 'D:/Project/K_project/data/Motion and Kinect unified array/'
Kfolder   = 'Unified_KData/'
Mfolder   = 'Unified_MData/'
Rfolder   = 'reliability/'

group_size = 30 # sample number per group
jnum = 11      # joint number per sample; *3 (xyz)



for idx,(kinfile,minfile,rinfile)  in enumerate(zip(glob.glob(os.path.join(src_path+Kfolder,'*ex4.pkl')),\
                                                    glob.glob(os.path.join(src_path+Mfolder,'*ex4_FPS30_motion_unified.pkl')),\
                                                    glob.glob(os.path.join(src_path+Rfolder,'*ex4.pkl')))):
    

    print(kinfile)
    print(minfile)  
    print(rinfile)
    print('==================================\n\n\n')    
    kdata = cPickle.load(file(kinfile,'r'))
    mdata = cPickle.load(file(minfile,'r'))
    rdata = cPickle.load(file(rinfile,'r'))

    Kary = np.zeros((jnum*3,kdata[20].shape[1]))
    Mary = np.zeros((jnum*3,mdata[20].shape[1]))
    Rary = np.zeros((jnum  ,len(rdata[20])    ))
    
    for kidx, i in enumerate(kdata.keys()):
        Kary[3*kidx:3*(kidx+1),:] = kdata[i]
        Mary[3*kidx:3*(kidx+1),:] = mdata[i] 
        Rary[kidx:(kidx+1),:]     = rdata[i]     
             
    kname = dst_path+Kfolder + kinfile.split('\\')[-1]
    mname = dst_path+Mfolder + minfile.split('\\')[-1] 
    rname = dst_path+Rfolder + rinfile.split('\\')[-1]

    cPickle.dump(Kary,file(kname,'wb'))
    cPickle.dump(Mary,file(mname,'wb'))
    cPickle.dump(Rary,file(rname,'wb'))    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
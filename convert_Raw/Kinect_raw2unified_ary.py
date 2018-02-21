# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 13:30:59 2017

@author: medialab
"""

'''
 convert original kinect data to unified array data
 
 
'''
import cPickle,glob,os
import numpy as np
from Mocam2Kinect import *
from Human_mod import *
from rawK2array import *

src_path = 'D:/AllData_0327(0220)/AllData_0327/Motion and Kinect raw data/20170306/pkl/'
dst_path = 'D:/AllData_0327(0220)/AllData_0327/unified data array/Unified_KData/'

jidx = [0, 1, 2, 3, 4, 5, 6, 8, 9 ,10, 20]
jnum = 11

# for infile in glob.glob(os.path.join(src_path,'*.pkl')):
#     print infile
#     data  = cPickle.load(file(infile,'rb'))    
#     Kbody = rawK2ary(data,jidx)
#     kdata = human_mod(Kbody)
    
#     Kary  = np.zeros((jnum*3,kdata[20].shape[1]))
#     for kidx, i in enumerate(kdata.keys()):
#         Kary[3*kidx:3*(kidx+1),:] = kdata[i]
       
#     name  = infile.split('\\')[-1].split('ex')        
#     kname = name[0]+'unified_ex'+name[1]        
#     cPickle.dump(Kary,file(dst_path+kname,'wb'))  

for subfolder in os.listdir(src_path):  
    for exeno in [1, 2, 3, 5, 6, 7]:
    
        if '.lnk' in subfolder:
            path = folder_retarget(src_path,subfolder)
            filelist = glob.glob(os.path.join(path, '*ex'+repr(exeno)+'.pkl') ) # find all pkl files
        else:
            filelist = glob.glob(os.path.join(src_path+subfolder, '*ex'+repr(exeno)+'.pkl') ) # find all pkl files
    #    pdb.set_trace()
        for infile in filelist:
            print infile
            data = cPickle.load(file(infile,'rb'))
            Kbody = rawK2ary(data,jidx)
            J     = human_mod(Kbody)

            Kary  = np.zeros((jnum*3,J[20].shape[1]))
            for kidx, i in enumerate(J.keys()):
                Kary[3*kidx:3*(kidx+1),:] = J[i]


            name = infile.split('\\')[-1].split('ex')
            if name[0].split('data')[1][0]=='1':
                year = '2016'
            else:
                year = '2017'
                
            fname = dst_path+'ex'+repr(exeno)+'/' + name[0].replace('data','data'+year)+'unified_ex'+name[1]
    
    
            cPickle.dump(Kary, file(fname,'wb'))     
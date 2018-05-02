# -*- coding: utf-8 -*-
"""
convert dict data to array data

"""
import os, glob, cPickle
import numpy as np

src_path  = 'D:/AllData_0327(0220)/AllData_0327/unified data/'
dst_path  = 'D:/AllData_0327(0220)/AllData_0327/unified data array/'
Kfolder   = 'Unified_KData/'
Mfolder   = 'Unified_MData/'
Rfolder   = 'reliability/'

group_size = 30 # sample number per group
jnum = 11      # joint number per sample; *3 (xyz)

for i in range(1, 8):
    exeno = 'ex'+repr(i)
    for idx,(kinfile,minfile,rinfile)  in enumerate(zip(glob.glob(os.path.join(src_path+Kfolder+exeno+'/','*'+exeno+'.pkl')),\
                                                        glob.glob(os.path.join(src_path+Mfolder+exeno+'/','*'+exeno+'_FPS30_motion_unified.pkl')),\
                                                        glob.glob(os.path.join(src_path+Rfolder+exeno+'/','*'+exeno+'.pkl')))):
    # for idx,(minfile,rinfile)  in enumerate(zip(glob.glob(os.path.join(src_path+Mfolder+exeno+'/','*'+exeno+'_FPS30_motion_unified.pkl')),\
    #                                             glob.glob(os.path.join(src_path+Rfolder+exeno+'/','*'+exeno+'.pkl')))):
                
        print(kinfile)
        print(minfile)  
        # print(rinfile)
        print('==================================\n')    
        kdata = cPickle.load(file(kinfile,'r'))
        mdata = cPickle.load(file(minfile,'r'))
        # rdata = cPickle.load(file(rinfile,'r'))

        Kary = np.zeros((jnum*3,kdata[20].shape[1]))
        Mary = np.zeros((jnum*3,mdata[20].shape[1]))
        # Rary = np.zeros((jnum  ,len(rdata[20])    ))
        
        for kidx, i in enumerate(mdata.keys()):
            Kary[3*kidx:3*(kidx+1),:] = kdata[i]
            Mary[3*kidx:3*(kidx+1),:] = mdata[i] 
            # Rary[kidx:(kidx+1),:]     = rdata[i]     

        # if rinfile.split('\\')[1].split('data')[1][0]=='1':
        #     year = '2016'
        # else:
        #     year = '2017'

        kname = dst_path+Kfolder +exeno+'/' + kinfile.split('\\')[-1]
        mname = dst_path+Mfolder+exeno+'/' + minfile.split('\\')[-1] 
        # rname = dst_path+Rfolder+exeno+'/' + rinfile.split('\\')[-1].replace('data','data'+year)

        cPickle.dump(Kary,file(kname,'wb'))
        cPickle.dump(Mary,file(mname,'wb'))
        # cPickle.dump(Rary,file(rname,'wb'))
        
#====================================================================#        
        
#  ==========  for single file ======================   
        
# exeno      = 'ex4'        
# group_size = 30 # sample number per group
# jnum       = 11          
      
# kinfile = 'D:/Project/K_project/convert_Raw/Yao_data201710131636_unified_ex4.pkl'
# kdata = cPickle.load(file(kinfile,'r'))
# Kary = np.zeros((jnum*3,kdata[20].shape[1]))
# for kidx, i in enumerate(kdata.keys()):
#     Kary[3*kidx:3*(kidx+1),:] = kdata[i] 
# kname = kinfile.split('/')[-1]            
# cPickle.dump(Kary,file(kname,'wb'))   


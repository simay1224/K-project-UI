# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 14:02:05 2017

@author: medialab
"""

import os,glob

path = 'D:/Project/K_project/data/Motion and Kinect unified/reliability/'

#for filename in os.listdir(path)[:-2]:
#    if '_unified.pkl' in filename:
#        print filename
#        name = filename.split('_')
#        fname = name[0]+'_'+name[1]+ '_'+name[2]+ '_'+name[3]+ '_'+name[5][:-4]+ '_'+name[4]+ '.pkl'
##        fname = name[0]+'unified_ex'+name[1]
#        os.rename(filename, fname)

#for foldername in os.listdir(path)[:-2]:
#    print foldername
#    for filename in os.listdir(path+foldername+'/'):
#        print filename
#        name = filename.split('.')
#        fname = foldername+'_'+name[0]+'_ex.'+name[1]
#        print fname
#        os.rename(path+foldername+'/'+filename, path+foldername+'/'+fname)

for idx,filename in enumerate(glob.glob(os.path.join(path+'*.pkl'))):
    print filename  
    name = filename.split('_data')
#    exename = name[1].split('_')[2]
    if name[1][0] == '1':
        
        fname = name[0]+'_data2016'+name[1]
    else:
        fname = name[0]+'_data2017'+name[1]
    print fname
    os.rename(filename, fname)
   


#for idx,filename in enumerate(glob.glob(os.path.join(path+'*.pkl'))):
#    print filename  
#
#    os.rename(filename, filename[:-4])
    
    





 
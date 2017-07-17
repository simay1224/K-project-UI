# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 16:20:07 2017

@author: medialab
"""


import cPickle
import numpy as np
import glob,os

    

src_path = 'F:/AllData_0327/Motion and Kinect raw data/20161216/pkl/'
dst_path = 'F:/AllData_0327/Motion and Kinect raw data/3D_kinect_joint/'
jidx = [0,1,2,3,4,5,6,8,9,10,20]



for subfolder in os.listdir(src_path):  
    for exeno in [1,2,3,4]:
    

        filelist = glob.glob(os.path.join(src_path+subfolder, '*ex'+repr(exeno)+'.pkl') ) # find all pkl files
    #    pdb.set_trace()
        for infile in filelist:
            print infile
            data = cPickle.load(file(infile,'rb'))
            Len  = len(data)
            J    = np.zeros((33,Len))
            for fidx in xrange(Len):
                for idx,j in enumerate(jidx):
                    J[idx*3  ,fidx] = data[fidx]['joints'][j].Position.x
                    J[idx*3+1,fidx] = data[fidx]['joints'][j].Position.y
                    J[idx*3+2,fidx] = data[fidx]['joints'][j].Position.z
        
            name = infile.split('\\')[-1].split('ex')
            if name[0].split('data')[1][0]=='1':
                year = '2016'
            else:
                year = '2017'
                
            fname = dst_path+'ex'+repr(exeno)+'/' + name[0].replace('data','data'+year)+'raw3D_ex'+name[1]
    
    
            cPickle.dump(J,file(fname,'wb'))



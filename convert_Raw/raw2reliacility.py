# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 13:57:34 2017

@author: medialab
"""

# create reliability file

import cPickle
import os

src_path = 'D:/Project/K_project/data/Motion and Kinect raw data/'

#unified data
usrc_path = 'D:/Project/K_project/data/Motion and Kinect unified/Unified_KData/'

dst_path = 'D:/Project/K_project/data/Motion and Kinect unified/reliability/'

jidx = [0,1,2,3,4,5,6,8,9,10,20]

for datefolder in os.listdir(src_path):
    print datefolder
    for user in os.listdir(src_path+datefolder+'/pkl/'):
        print user
        for infile in os.listdir(src_path+datefolder+'/pkl/'+user+'/'):
            #print infile
            Rel = {}
            for idx in jidx:
                Rel[idx] = []
            rawdata = cPickle.load(file(src_path+datefolder+'/pkl/'+user+'/'+infile,'rb'))
            uname = usrc_path + infile.replace('_ex','_unified_ex')
            try:
                Kudata = cPickle.load(file(uname,'rb'))
            except:
                Kudata = cPickle.load(file(uname,'r'))
            for frame_idx in xrange(min(len(rawdata),Kudata[0].shape[1])):
                for idx in jidx:
                    Rel[idx].append(rawdata[frame_idx]['Rel'][idx])
            fname = dst_path + infile.replace('_ex','_Rel_ex')        
            cPickle.dump(Rel,file(fname,'wb'))
                
            
            

    


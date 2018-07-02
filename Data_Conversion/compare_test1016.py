# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 16:00:21 2017

@author: medialab
"""
from Mocam2Kinect import *
from Human_mod import *
from rawK2array import *
import cPickle
import numpy as np
import glob,os,win32com.client,pdb
from Kfunc.model  import Human_mod   as Hmod

jidx = [0,1,2,3,4,5,6,8,9,10,20]
infile = 'C:/exercisetest/output/Qi_data20171016172808_ex4.pkl'



data  = cPickle.load(file(infile,'rb'))

# offline 
Kbody = rawK2ary(data,jidx)
J     = human_mod(Kbody)

jnum       = 11 
Kary = np.zeros((jnum*3,J[20].shape[1]))

for kidx, i in enumerate(J.keys()):
    Kary[3*kidx:3*(kidx+1),:] = J[i]
    
    
Kary = Kary[12:,:]    
    
#online


for i in xrange(len(data)):
    joints = data[i]['joints']
    _, modJary = Hmod.human_mod_pts(joints,True)    
    modJary = modJary.flatten().reshape(-1,21)
    if i == 0:
        Jary = modJary
    else:
        Jary = np.vstack([Jary,modJary])
Jary = Jary.T

print np.sum(np.abs(Jary-Kary))

  
for i in range(len(data)):
    if i == 0:
       reconJary = data[i]['reconJ']
    else:
       reconJary = np.vstack([reconJary,data[i]['reconJ']]) 
       
reconJary = reconJary.T
       
print np.sum(np.abs(Jary-reconJary))       
       
aa = []    
for i in xrange(780):
    if np.sum(Jary[:,i]-reconJary[:,i]) != 0:
       aa.append(i)       
       
cPickle.dump(Jary,file('Qi_data20171016_ex4.pkl','wb'))       
       
    

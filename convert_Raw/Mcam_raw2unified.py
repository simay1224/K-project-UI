# -*- coding: utf-8 -*-
"""
Created on Tue Mar 07 21:44:09 2017

@author: medialab
"""

import csv,cPickle,copy
import numpy as np
import cmath
import os,glob
from Mocam2Kinect import *
from Human_mod import *

key_list_25 = ['LShoulder_1','RUArm_2','LShoulder_2', 
            'LUArm_1', 'RUArm_1', 'LUArm_2', 'Head_3', 
            'Head_2', 'Head_1', 'RShoulder_2', 'Chest_4', 
            'Chest_3', 'Chest_2', 'Chest_1', 'Hip_1', 
            'Hip_3', 'Hip_2', 'Hip_4', 'RShoulder_1', 
            'LHand_3', 'LHand_2', 'LHand_1', 'RHand_1', 
            'RHand_3', 'RHand_2']

# Raw data set up            
src_path = 'F:/Kinect Project/20170224/MoCam/30/'
dst_path = 'F:/Kinect Project/20170224/MoCam/Converted_Data/'

# unified data set up
uni_src_path = dst_path
uni_dst_path30  = 'H:/20170224/Unified_MData/30/'
uni_dst_path120 = 'H:/20170224/Unified_MData/120/'
    
def findKeys(orig_keys, standard_key_list):
    keys_dict = {}
    for jk in standard_key_list:
        for ik in orig_keys: 
            if(jk in ik):
                keys_dict[jk] = ik
    return keys_dict
          
def getAllidx(List, num,offset = 0, findcont = False):
    '''
    find num index in List
    
    if find continues mode on, it will return [seg1, seg2 ... segN]
    
    each sgment represent by following structure
    
    [previous index which has values, Next index which has values, len of not useful value inside]
    
    '''
    result = [a+offset  for a in range(len(List)) if List[a]==num]
    if findcont:
        cont = []
        for idx , i in enumerate(result):
            if idx == 0 :
                tmp = [i]
            else:
                if (result[idx]-result[idx-1]) ==1:
                   tmp.append(i) 
                else:
                    cont.append([min(tmp)-1,max(tmp)+1,len(tmp)])
                    tmp = [i] 
        
        cont.append([min(tmp)-1,max(tmp)+1,len(tmp)])
        return cont 
    else:
        return result  

def interp(start,end,num):
    # linear interpolation
    # input data structure start value,end value,num  
    
    value = end - start 
    offset = value/(num+1.)
    tmp = [start]
    for i in range(num):
        tmp.append(start+offset*(i+1))
        
    return np.array(tmp)  


def rotateary(x,y,theta):
    X = np.cos(theta)*x-np.sin(theta)*y
    Y = np.sin(theta)*x+np.cos(theta)*y

    return X,Y   
        
        


Markernum = 25

# =================== extract from csv, rotate the body, save as numpy array  ================= 

for subfolder in os.listdir(src_path): 
    if '30' in subfolder:
        dst_fps = '_FPS30_'
    else:
        dst_fps = '_FPS120_'
    filelist = glob.glob(os.path.join(src_path+subfolder, '*.csv') ) # find all csv files
    
    for infile in filelist:

        print infile
        data = {}
        Bpidx = {} # Body part index
        
        fname = dst_path + subfolder.split('_')[0]+'_'+ infile.split('\\')[-1][5:-4] + dst_fps + 'motion.pkl' 

                
        f =  open(infile, 'r')
        for idx,row in enumerate(csv.reader(f)):
            if idx ==2:
                a = getAllidx(row,'Marker')[:Markernum*3]         
            if idx ==3:
                Btype = set(row[a[0]:a[-1]+1]) 
                for i in Btype:
                    Bpidx[i]=getAllidx(row[a[0]:a[-1]+1],i,a[0])
                    data[i] = {}
                    data[i]['X']=[]
                    data[i]['Y']=[]
                    data[i]['Z']=[]
            if idx >= 7:
                for part in Btype:
                    try:
                        data[part]['X'].append(float(row[Bpidx[part][0]]))
                    except:
                        if row[Bpidx[part][0]]== '':
                           data[part]['X'].append(-99.0)
                        else:
                            print row[Bpidx[i][0]]
                    try:
                        data[part]['Y'].append(float(row[Bpidx[part][1]]))
                    except:
                        if row[Bpidx[part][1]]== '':
                           data[part]['Y'].append(-99.0)
                        else:
                            print row[Bpidx[i][1]]
                    try:
                        data[part]['Z'].append(float(row[Bpidx[part][2]]))
                    except:
                        if row[Bpidx[part][2]]== '':
                           data[part]['Z'].append(-99.0)
                        else:
                            print row[Bpidx[i][2]]
            
        
        dkey = data.keys()
        # generate key dictionary
        key_dict = findKeys(dkey,key_list_25)
        
        idx = 0
        for i in key_list_25:
            if idx == 0:
                Dary = np.vstack([data[key_dict[i]]['X'],data[key_dict[i]]['Y'],data[key_dict[i]]['Z']])
            else:
                Dary = np.vstack([Dary,data[key_dict[i]]['X'],data[key_dict[i]]['Y'],data[key_dict[i]]['Z']])
            idx = idx + 1
        # complement the array with interplation
        Comary = copy.copy(Dary) 
        
        for i in range(len(Dary)):
            if -99.0 in Dary[i]: 
                foo = getAllidx(Dary[i], -99.0, findcont = True)
                for j in foo:
                    if j[0]<0:
                        Comary[i][:j[1]] = Dary[i][j[1]] 
                    elif j[1]>=len(Dary[i]):
                        Comary[i][j[0]:j[1]] = Dary[i][j[0]]
                    else:
                        Comary[i][j[0]:j[1]] = interp(Dary[i][j[0]],Dary[i][j[1]],j[2]) 
        
        frame_no = 200
        # rotation by chest_4-chest_1 (chest_4 in the middle of front, chest_1 in the middle of back)
        r,theta = cmath.polar(complex(Comary[10*3][frame_no]-Comary[13*3][frame_no],Comary[10*3+2][frame_no]-Comary[13*3+2][frame_no]))                
        
        
        Rcary = copy.copy(Comary)
        for i in xrange(len(dkey)):
        
            Rcary[i*3],Rcary[i*3+2] = rotateary(Comary[i*3],Comary[i*3+2],-np.pi/2-theta)    
                        
                        
                       
        Data = {}
        Data['keys'] = key_list_25
        Data['pos']  = Dary
        Data['cpos'] = Comary
        Data['rcpos'] = Rcary
        
        if Rcary[10*3+2][200]>Rcary[13*3+2][200]:
            print 'warning: fatal wrong!'
        cPickle.dump(Data,file(fname,'wb'))
        
    
#======================== unified the Mcam data ========================
        



filelist = glob.glob(os.path.join(uni_src_path, '*.pkl'))



for infile in filelist:
    print infile   
    data = cPickle.load(file(infile,'r'))
    pos_Kinect = Mocam2Kinect(data)
    Pos_Unified = human_mod(pos_Kinect)
    if 'FPS30' in infile:
        fname = uni_dst_path30+infile.split('\\')[-1][:-4]+ '_unified.pkl'
    else:
        fname = uni_dst_path120+infile.split('\\')[-1][:-4]+ '_unified.pkl'
        
    cPickle.dump(Pos_Unified,file(fname,'wb'))


























        


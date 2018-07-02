# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 14:41:13 2016

@author: medialab
"""

import csv,cPickle,copy,pdb
import numpy as np
import cmath
    
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
        
data = {}
Bpidx = {} # Body part index
Markernum = 25

f =  open('./CSV_Data/1216/Andy_30/Take 2016-12-15 04.11.57 PM.csv', 'r')
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
            
#cPickle.dump(data,file('mocapdata1128.pkl','wb'))


#data = cPickle.load(file('mocapdata1128.pkl','rb'))
#pdb.set_trace()
dkey = data.keys()

#Dary = np.array([])

for idx,i in enumerate(dkey):
    if idx == 0:
        Dary = np.vstack([data[i]['X'],data[i]['Y'],data[i]['Z']])
    else:
        Dary = np.vstack([Dary,data[i]['X'],data[i]['Y'],data[i]['Z']])
        

# complement the array

Comary = copy.copy(Dary) 

for i in range(len(Dary)):
    if -99.0 in Dary[i]: 
        foo = getAllidx(Dary[i], -99.0, findcont = True)
        
        for j in foo:
            
            if j[0]<0:
                #pdb.set_trace()
                Comary[i][:j[1]] = Dary[i][j[1]] 
            elif j[1]>=len(Dary[i]):
                #pdb.set_trace()
                Comary[i][j[0]:j[1]] = Dary[i][j[0]]
            else:
                Comary[i][j[0]:j[1]] = interp(Dary[i][j[0]],Dary[i][j[1]],j[2]) 

                
#
frame_no = 200
chest_1 = 10
chest_4 = 13



r,theta = cmath.polar(complex(Comary[chest_1*3][frame_no]-Comary[chest_4*3][frame_no],Comary[chest_1*3+2][frame_no]-Comary[chest_4*3+2][frame_no]))                


# rotate array 
Rcary = copy.copy(Comary)
for i in xrange(len(dkey)):

    Rcary[i*3],Rcary[i*3+2] = rotateary(Comary[i*3],Comary[i*3+2],-np.pi/2-theta)    
                
                
               
Data = {}
Data['keys'] = dkey
Data['pos']  = Dary
Data['cpos'] = Comary
Data['rcpos'] = Rcary  

cPickle.dump(Data,file('./output/pkl/test0219.pkl','wb'))

























        


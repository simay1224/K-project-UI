# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 14:41:16 2016

@author: medialab
"""
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import numpy as np
import cPickle,glob,os
import copy,pdb

#kinematic segment length (unit:cm)
kinseg = {}
kinseg[0] = 13.4  #head2neck
kinseg[1] = 8.3   #neck2spins
kinseg[2] = 15.4  #spins2spinm
kinseg[3] = 32.5  #spinm2spinb
kinseg[4] = 16.65 #spins2shlder
kinseg[5] = 33.2  #shlder2elbow
kinseg[6]  =27.1  #elbow2wrist

# target joint order
Tjo = [0,1,2,3,4,5,6,8,9,10,20]

# gaussian filter
a = np.arange(2)
sigma = 0.65
gw = 1/(2*np.pi)**2/sigma*np.exp(-0.5*a**2/sigma**2) 
gw = gw*(1/sum(gw))
#initail reliability 

jord = [0,1,2,3,4,5,6,8,9,10,20]

rel = {}
for i in jord:
    rel[i]=0
    
def rel_behav(J,th = 0.03,fsize=3): #behavior term
    #J : 3D joint position in [...,f-4,f-3,f-2,f-1,f]
    #th   : threshold (uint: m)
    r = 1
    if len(J)>=fsize:
        for k in xrange(1):
            dj   = J[-(k+1)]-J[-(k+2)]            
            dj_1 = J[-(k+2)]-J[-(k+3)]
            dj_2 = J[-(k+1)]-J[-(k+3)]
            n_dj = np.linalg.norm(dj)
            n_dj_1 = np.linalg.norm(dj_1)
            n_dj_2 = np.linalg.norm(dj_2)
    

            if (n_dj_2 < th):
                r = 1
            else:
                if (n_dj > th):
                    r = max(1-4*(n_dj-th)/th,0)
                else:
                    r = 1    
            
    return r

        
def rel_kin(joints): # kinematic term    
    order1 = [9,5,20,1,2]
    order2 = [8,6,4,20,3]     # joints' order   
    order3 = [10,4,8,0,20]
    refer1 = [5,6,4,2,0]      # kinseg's order
    refer2 = [6,5,4,3,1]  

    segrel = {}
    result = []
    cnts = np.zeros(21)
    for i in Tjo:
        segrel[i]=0

    for i in xrange(len(order1)):
        A = np.array([joints[order1[i]].Position.x,joints[order1[i]].Position.y,joints[order1[i]].Position.z])
        B = np.array([joints[order2[i]].Position.x,joints[order2[i]].Position.y,joints[order2[i]].Position.z])
        C = np.array([joints[order3[i]].Position.x,joints[order3[i]].Position.y,joints[order3[i]].Position.z])
          
        tmp = min(np.abs(np.linalg.norm(A-B)*100 - kinseg[refer1[i]])/kinseg[refer1[i]],1)
        segrel[order1[i]] += tmp
        segrel[order2[i]] += tmp
        

        tmp = min(np.abs(np.linalg.norm(A-C)*100 - kinseg[refer2[i]])/kinseg[refer2[i]],1)
        segrel[order1[i]] += tmp
        segrel[order3[i]] += tmp

        cnts[order1[i]]+=2
        cnts[order2[i]]+=1
        cnts[order3[i]]+=1

    for i in Tjo:
        result.append( 1-(segrel[i]/cnts[i]))

    return result

    
def rel_trk(joints): # tracking term
    trkrel = []
    for i in Tjo:
        if joints[i].TrackingState == 2:
            trkrel.append(1.0)
        elif joints[i].TrackingState == 1:
            trkrel.append(1.0)
        else:
            trkrel.append(0.0)

    return trkrel
    
def rel_rate(Rb,Rk,Rt,order,flen = 2):
    if (len(Rb[0])>=flen) & (len(Rk[0])>=flen) & (len(Rt[0])>=flen) :
        Rel = copy.copy(rel)
        
        if order == jord :
            for j in order:
                for i in xrange(flen):
                    Rel[j] += gw[i]*min(Rb[j][-(i+1)],Rk[j][-(i+1)],Rt[j][-(i+1)])
        else:
            print 'joints order not match !!'
    else:
        return rel
    return Rel

src_path = 'I:/AllData_0327/raw data/'
dst_path = 'I:/Data_0702/unified data/reliability/'

for datefolder in os.listdir(src_path):  
    for userfolder in os.listdir(src_path+'/'+datefolder+'/pkl/'):
        for infile in glob.glob(os.path.join(src_path+'/'+datefolder+'/pkl/'+userfolder+'/','*ex4.pkl')):
            print infile
            
            Jarray  = {}
            Rb = {}
            Rt = {}
            Rk = {}
            Rel ={}
            for ii in jord:
                Rk[ii]=[]
                Rt[ii]=[]
                Rb[ii]=[]
                Rel[ii]=[]
            
            Alldata = cPickle.load(file(infile,'rb'))
            
            for fidx in range(len(Alldata)):#138,145):#
                Jdic = Alldata[fidx]['joints']
                
                for ii in jord:
                    try : 
                        Jarray[ii].append(np.array([Jdic[ii].Position.x,Jdic[ii].Position.y,Jdic[ii].Position.z]))
                    except:                            
                        Jarray[ii] = []
                        Rb[ii] = []
                        Jarray[ii].append(np.array([Jdic[ii].Position.x,Jdic[ii].Position.y,Jdic[ii].Position.z])) 

                    Rb[ii].append(rel_behav(Jarray[ii]))
                    
                rt = rel_trk(Jdic) 
                rk = rel_kin(Jdic)
                for ii,jj in enumerate(jord):    
                    Rt[jj].append(rt[ii])
                    Rk[jj].append(rk[ii])
                    
                Reltmp = rel_rate(Rb,Rk,Rt,jord)
                
                for jj in Reltmp.keys():
                    Rel[jj].append(Reltmp[jj]) 
                
            #    print fidx
            #    print 'Rb is :'+repr(np.round(Rb[6],2))
            #    print 'Rk is :'+repr(np.round(Rk[6],2))
            #    print 'Rt is :'+repr(np.round(Rt[6],2))
            #    print np.round(Rel[6],2)
            #    print('\n')
            
            for jj in Rel.keys():
                if jj == 0:
                    Relary = Rel[jj]
                else:
                    Relary = np.vstack([Relary,Rel[jj]])
            fname = dst_path+'modified_'+infile.split('\\')[1]
            cPickle.dump(Relary,file(fname,'wb'))








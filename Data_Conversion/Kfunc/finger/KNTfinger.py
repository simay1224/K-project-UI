# -*- coding: utf-8 -*-
"""
Created on Sat Sep 03 14:33:18 2016

@author: user
"""

import numpy as np
import scipy.ndimage.morphology as ndm
from scipy.ndimage.morphology import distance_transform_edt as dte
from numpy.linalg import norm as nlnorm
import cv2,operator
import pygame

def handseg(frame_in,hw,hc, w = 1920, h = 1080 ):
    '''
    segment hand region
    input frame : type binary
    hc : hand center        
    '''
    rad =  int(((hw.x-hc.x)**2+(hw.y-hc.y)**2)**0.5)*2
    xul =  max(int(hc.x)-rad,0)
    yul =  max(int(hc.y)-rad,0)
    xlr =  min(int(hc.x)+rad,w)
    ylr =  min(int(hc.y)+rad,h)
 
    hand = ndm.binary_opening(frame_in[yul:ylr,xul:xlr],structure=np.ones((5,5))).astype(np.uint8) #hand closing

    #cv2.imshow('hand',hand*255)
    #cv2.waitKey()

    return hand , (xul,yul),rad   

def hand_contour_find(contours):
    max_area=0
    largest_contour=-1
    for i in range(len(contours)):
        cont=contours[i]
        area=cv2.contourArea(cont)
        if(area>max_area):
            max_area=area
            largest_contour=i
    
    if(largest_contour==-1):
        return False,0
    else:
        h_contour=contours[largest_contour]
        return True,h_contour
       
def find_hand_center(thresh):

    thresh[thresh>0]=1
    th,tw = thresh.shape
    dist = dte(thresh).flatten() #find dist between hand pts and hand contour (can speed up)
    distidx = dist.argmax()

    return (np.mod(distidx,tw),distidx//tw)
    
def find_angle(fpts,midpt):

    v = fpts-midpt
    vdist = nlnorm(v,axis = 1)
    vlen = len(v)
    indot = [sum(v[i]*v[i+1]) for i in xrange(0,vlen,2)]
    costheta = [indot[i//2]/(vdist[i//2*2]*vdist[i//2*2+1]) for i in xrange(vlen) ]
    return np.arccos(costheta)/np.pi*180
        
def find_fingers(cnt,center,wrist,offset,rad):
    
    bx,by,bw,bh = cv2.boundingRect(cnt)
    hull = cv2.convexHull(cnt,returnPoints = False)
    #deft = cv2.convexityDefects(cnt,hull)
    defects = cv2.convexityDefects(cnt,hull)
    if defects is not None:
        #idx = np.sort(deft.T[3][0].argsort()[-num:]) # choose 4 largest distant
        #defects = deft[idx]
        
        cor = []
        mid = []
        
        for i in xrange(len(defects)):
            s,e,f,d = defects[i,0]
            cor.append(tuple(cnt[s][0])) #append start pt
            cor.append(tuple(cnt[e][0])) #append end pt
            #---append twice ----
            mid.append(tuple(cnt[f][0])) 
            mid.append(tuple(cnt[f][0]))
    
        #-- select real finger points
    
        cmtx = np.array(cor)
        mmtx = np.array(mid)
        distchk = ((cmtx.T[0]-center[0])**2+(cmtx.T[1]-center[1])**2)**0.5 > max(bw,bh)/3. #finger len check
        wristchk = ((mmtx.T[0]-wrist.x+offset[0])**2+(mmtx.T[1]-wrist.y+offset[1])**2)**0.5 > ((center[0]-wrist.x+offset[0])**2+(center[1]-wrist.y+offset[1])**2)**0.5
        aglchk =find_angle(cmtx,np.array(mid))<90     # finger angle check
        #pdb.set_trace()
        chkidx = np.where((aglchk&distchk&wristchk)==True)[0]
        #chkidx = np.where((aglchk&distchk)==True)[0]
        
        cor = list(set([cor[i] for i in chkidx])) #remove duplicate pts 
        cormtx = np.array(cor)
        chk = len(cor)
        X = np.array([])
        Y = np.array([])
        
        if chk>1 :  # more than 5 finger points # merger close pt pairs
        
            # calculate distance
            XX1 = np.tile(cormtx.T[0],(chk,1))
            XX2 = np.tile(np.array([cormtx.T[0]]).T,(1,chk))
            YY1 = np.tile(cormtx.T[1],(chk,1))
            YY2 = np.tile(np.array([cormtx.T[1]]).T,(1,chk))
            
            distpt = ((XX1-XX2)**2+(YY1-YY2)**2)**0.5   #pt dist mtx 
            #th = np.sort(list(set(distpt.flatten())))[chk-5] # set a threshold 
            th = rad/5.
            distpt[distpt>th]= 0
            # find shortest dist in dist matrix (in upper triangle)
            temp = np.nonzero(np.triu(distpt))  # points coordinate
            dup = (np.bincount(temp[0],minlength=chk)>1)|(np.bincount(temp[1],minlength=chk)>1)
            duppts = np.where(dup)[0] #duplicat pts: one pt close to multi pts
            rmidx = np.array([])
            
            for i in duppts:
                dupidx = np.where((temp[0]==i)|(temp[1]==i))[0]
                minidx = distpt[temp[0][dupidx],temp[1][dupidx]].argmin()
                delidx = np.delete(dupidx,minidx)
                rmidx  = np.append(rmidx,delidx)
            
            X = np.delete(temp[0],rmidx)
            Y = np.delete(temp[1],rmidx)
            
        #-- merge points
         
            fingeridx = np.delete(np.arange(chk),np.append(X,Y))
            finger = [cor[i] for i in fingeridx]
                
            for i,j in zip(X,Y):
                finger.append(tuple(np.add(cor[i],cor[j])//2))   
            return finger 
        elif chk == 1:
            return cor
            
        else:
            return False
    else:            
        return False
                
   
def draw_hand(thresh,frame,offset,rad,wrist,color,frame_surface): 
    
    try:
        contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    except:
        return []
        
    if len(contours) == 1: # if has muiltiple contours
        cnt = contours[0]
        found = 1
    else:
        found,cnt = hand_contour_find(contours)    

    if found:
        center = find_hand_center(thresh)
    
        fingers = find_fingers(cnt,center,wrist,offset,rad)
        
        if fingers :
            for i in fingers:
                pts = tuple(map(operator.add,i,offset))
                pygame.draw.circle(frame_surface, color, pts,10,8)
                pygame.draw.line(frame_surface, color, pts, (center[0]+offset[0],center[1]++offset[1]), 8)  
            return fingers
        else:
            return[]
    else:
            return[]
    
    

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 16:24:25 2016

@author: medialab
"""
import cv2
import numpy as np
from Kfunc import *
from Kfunc.IO import *
from KNTfinger import *

def fextr(frame,bkimg,body,bddic,joint_points,color,frame_surface):
    
    hsvimg = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)    
    tmp = np.abs(hsvimg[:,:,2] - bkimg[:,:,2] )                                           
    fgimg = np.zeros([1080,1920])                  
    fgimg[tmp>80] = 1 
                 

    if (body.hand_left_state == 2)| (body.hand_left_state == 0): #hand open
        Lhand,bddic['Loffset'],Lrad = handseg(fgimg,joint_points[6],joint_points[7])                  
        bddic['Lhand'] = draw_hand(Lhand,frame,bddic['Loffset'],Lrad,joint_points[6],color,frame_surface)
        typetext(frame_surface,'Lhand :'+repr(len(bddic['Lhand'])) +' fingers ',(100,100)) 
        if  (body.hand_left_state == 2) & ( len(bddic['Lhand'])<=3):
            typetext(frame_surface,'Open your left hand more !!',(1000,100),(255,0,0),60,True)
        else:
            typetext(frame_surface,'nice job !!',(1600,100),(0,255,0))
    elif (body.hand_left_state == 4): # Lasso
        Lhand,bddic['Loffset'],Lrad = handseg(fgimg,joint_points[6],joint_points[7])                  
        bddic['Lhand'] = draw_hand(Lhand,frame,bddic['Loffset'],Lrad,joint_points[6],color,frame_surface)
        typetext(frame_surface,'Lhand :'+repr(len(bddic['Lhand'])) +' fingers ',(100,100))
            
    elif body.hand_left_state ==3 : # closed
        typetext(frame_surface,'Lhand : closed',(100,100))
    else:
        typetext(frame_surface,'Lhand : Not detect',(100,100))
        
    typetext(frame_surface,'Rhand :'+repr(body.hand_right_state) ,(100,200))     
    if (body.hand_right_state == 2)|(body.hand_right_state == 0):
        Rhand,bddic['Roffset'],Rrad = handseg(fgimg,joint_points[10],joint_points[11])
        bddic['Rhand'] = draw_hand(Rhand,frame,bddic['Roffset'],Rrad, joint_points[10],color,frame_surface) 
        typetext(frame_surface,'Rhand :'+repr(len(bddic['Rhand'])) +' fingers ',(100,150))
        if  (body.hand_right_state == 2) & (len(bddic['Rhand'])<=3):
            typetext(frame_surface,'Open your right hand more !!',(1000,150),(255,0,0),60,True)
        else:
            typetext(frame_surface,'nice job !!',(1600,150),(0,255,0))
        
    elif (body.hand_right_state == 4):
        Rhand,bddic['Roffset'],Rrad = handseg(fgimg,joint_points[10],joint_points[11])
        bddic['Rhand'] = draw_hand(Rhand,frame,bddic['Roffset'],Rrad, joint_points[10],color,frame_surface) 
        typetext(frame_surface,'Rhand :'+repr(len(bddic['Rhand'])) +' fingers ',(100,150))                                                              
    elif body.hand_right_state ==3 :
        typetext(frame_surface,'Rhand : closed',(100,150))
    else:
        typetext(frame_surface,'Rhand : Not detect',(100,150))
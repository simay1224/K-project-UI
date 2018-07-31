# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 16:16:17 2016

@author: medialab
"""
from Kfunc import *
from Kfunc.IO import *

def shld_text(pro,rec,surface):
    string_1='Shoulder Rolls: '+ str(pro.shoulder_roll_count)                
    typetext(surface,string_1 ,(100,800),(0,128,255))        
    if(rec.error_code[1]==2):
        typetext(surface,'Please put your arm down' ,(500,50),(255,0,0)) 
    elif(rec.error_code[1]==3):
        typetext(surface,'What is on your shoulder?' ,(500,50),(255,0,0)) 
    elif(rec.error_code[0]==4):
        typetext(surface,'Please step back!' ,(500,50),(255,0,0)) 
    elif(rec.error_code[0]==5):
        typetext(surface,'Please facing the camera!' ,(500,50),(255,0,0))
    elif(rec.error_code[0]==6):
        typetext(surface,'Please stand vertically!' ,(500,50),(255,0,0))  
      

def shld_act(joints,Jpf,pro,fcnt):    #--shoudler data processing part--
    #---get the data for processing

    temp_ssy=joints[20].Position.y
    temp_ssz=joints[20].Position.z
    cur_data_1=joints[8].Position.z-temp_ssz
    if(Jpf[1]==[]):
        cur_data_2=-1
    else:
        cur_data_2=Jpf[1].y-temp_ssy

    pro.processShoulderOnce(cur_data_1,cur_data_2,fcnt)
        
      
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 03 14:33:19 2016

@author: user
"""
import numpy as np
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import ctypes,math
import collections

class ShoulderTops:
    def __init__(self):
        self.error_code=[1,1] # 1:normal 2: put down arm 3: something on arm 4:
        pass
    
    #========================= detect shoulder tops ==============================
    def myMapDepthPointToCameraSpace(self,kinect,pt_depth,depth_value):
        pt_d=PyKinectV2._DepthSpacePoint(pt_depth[0],pt_depth[1])
        depth_v=ctypes.c_ushort(depth_value)
        camera_point=kinect._mapper.MapDepthPointToCameraSpace(pt_d,depth_v)
        return camera_point 
    #-avoid two case:
    #-1.arm rises too high, then the ST was picked up at the arm
    #-2.ST rises too high, even higher than the middle point of head-neck
    #-the return result: False = not ST; True = it is the ST
    def ifNotShoulder(self,ST_depth,SJ_depth,EB_depth,spine_vector,head_depth,neck_depth,wrist_depth):
        arm_vector=[EB_depth.x-SJ_depth.x,EB_depth.y-SJ_depth.y]
        cos_armspine=(spine_vector[0]*arm_vector[0]+spine_vector[1]*arm_vector[1])  \
                /math.hypot(spine_vector[0],spine_vector[1])/math.hypot(arm_vector[0],arm_vector[1])
        
        if(cos_armspine<-0.3 or wrist_depth.y<SJ_depth.y):
            #print 'Put down your arm!'
            return 2
        if(ST_depth[1]<head_depth.y):
            #print 'What is on your arm?'
            return 3
        return 1
        
    #-return the position of one shoulder top in Depth Space
    def findOneTop(self,index_frame,SJ_ID,depth_joints,spine_vector,idxID):
        top=[]
        SJ_depth=depth_joints[SJ_ID]
        v_x=spine_vector[0]
        v_y=spine_vector[1]
        t_x=int(round(SJ_depth.x))
        t_y=int(round(SJ_depth.y))
        t_norund=t_x
        pre_x=0
        pre_y=0        
        
        if(abs(v_x) <= abs(v_y)): #stand relatively vertical
            while(True):
                if (-1<t_x<512 and -1<t_y<424):
                    if(index_frame[t_y,t_x]==idxID):
                        pre_x=t_x
                        pre_y=t_y
                        t_y-=1
                        t_norund-=v_x/v_y
                        t_x=int(round(t_norund))                  
                    else:
                        break;
                else:
                    break;
            top.append(pre_x)
            top.append(pre_y)
        if(len(top)<1):
            top=[-1,-1]
        return top  
     
    #-find two shoulder tops
    #-the retuen result has the form:
    #   [[position_left_DepthSpace],[position_right_DepthSpace],[position_left_CameraSpace],[position_right_CameraSpace],error_code_L,error_code_R]
    #-the error_code is also an output, which has the code meanings:
    #-1=correct; 2=rise the arm too high;
    #-3=something on the shoulder; 4=not facing camera
    #-5=too far from camera
    def findShouderTops(self,kinect,index_frame,depth_joints,camera_joints,depth_frame,idxID):
        if (camera_joints[20].Position.z<1.0):
            self.error_code[0]=4 #step back
            return [[],[],[],[],5,5]#patient is too close to the camera
        if (abs(camera_joints[4].Position.z-camera_joints[8].Position.z)>0.15):
            self.error_code[0]=5    
            return [[],[],[],[],4,4]#compare left and right shoulders, if not facing the camera right, then error code#4
        if (abs(camera_joints[0].Position.z-camera_joints[20].Position.z)>0.2):
            self.error_code[0]=6
            return [[],[],[],[],4,4]
        tops=[] # this list stores all information of shoulder tops
        spine_vector=[] # the spine vector indicates the direction of spine in Depth Space
        spine_vector.append(depth_joints[PyKinectV2.JointType_SpineBase].x-depth_joints[PyKinectV2.JointType_SpineShoulder].x)
        spine_vector.append(depth_joints[PyKinectV2.JointType_SpineBase].y-depth_joints[PyKinectV2.JointType_SpineShoulder].y)
        tops.append(self.findOneTop(index_frame,4,depth_joints,spine_vector,idxID))#leftShoulder=4
        tops.append(self.findOneTop(index_frame,8,depth_joints,spine_vector,idxID))#rightShoulder=8
        if tops[0]!=[]:
            temp=[tops[0][0],tops[0][1]]
            self.error_code[0]=self.ifNotShoulder(temp,depth_joints[4],depth_joints[5],spine_vector, \
                depth_joints[3],depth_joints[2],depth_joints[6])
            if(self.error_code[0]==1):
                #depth_v=depth_frame[tops[0][1]*512+tops[0][0]]
                depth_v=depth_frame[tops[0][1]][tops[0][0]]
                if not 500<depth_v<4500:
                    #depth_v=depth_frame[(tops[0][1]+1)*512+tops[0][0]]
                    depth_v=depth_frame[tops[0][1]+1][tops[0][0]]
                camera_point=self.myMapDepthPointToCameraSpace(kinect,tops[0],depth_v)
                tops.append(camera_point)
            else:
                tops[0]=[]
                tops.append([])
        else:
            tops.append([])
        if tops[1]!=[]:
            temp=[tops[1][0],tops[1][1]]
            self.error_code[1]=self.ifNotShoulder(temp,depth_joints[8],depth_joints[9],spine_vector, \
                depth_joints[3],depth_joints[2],depth_joints[10])
            if(self.error_code[1]==1):
                #depth_v=depth_frame[tops[1][1]*512+tops[1][0]] 
                depth_v=depth_frame[tops[1][1]][tops[1][0]]
                if not 500<depth_v<4500:
                    #depth_v=depth_frame[(tops[1][1]+1)*512+tops[1][0]]
                    depth_v=depth_frame[tops[1][1]+1][tops[1][0]]
                camera_point=self.myMapDepthPointToCameraSpace(kinect,tops[1],depth_v)
                tops.append(camera_point)
            else:
                tops[1]=[]
                tops.append([])
        else:
            tops.append([])
        return tops
    # Get shoulder info from Kinect part over    
    #-----------------------------------------

class ShoulderRoll:
    def __init__(self):
        self.cur_frame=0  
        #-all the number in variable names below indicates:
        #- 1=from SJoint_Z; 2=from STop_Y
        self.pre_data_1=-1   # SJoint_Z data in previous frame
        self.cur_data_1=-1   # SJoint_Z data in current frame
        self.min_threshold_1=0.0030  # the minimum threshold to decide a turning point (peak or vally in Z)
        self.pre_data_2=-1   # STop_Y data in previous frame
        self.cur_data_2=-1   # STop_Y data in current frame
        self.min_threshold_2=0.0030  # the minimum threshold to decide a turning point (peak or vally in Y)
        
        self.pt_que_1=collections.deque([])  # store raw data points (SJoint_Z)
        self.pt_filt_que_1=collections.deque([]) #store data points filted by gaussian filter
        self.last_convex_1=[0,-1]  # last convex (turning point in SJoint_Z), has form as [state (1=peak or -1=vally or 0=nothing), value(m)]
        self.pt_que_2=collections.deque([])
        self.pt_filt_que_2=collections.deque([])
        self.last_convex_2=[0,-1]  # last convex, as [state, value]
        
        #-last cycle (containing two different turning points and relative information), 
        #-as [state1,value1,state2,value2,abs_difference,start_location,end_location]
        #-state of 1st turning point (state1); value of 1st turning point (value1)
        #-state of 2nd turning point (state2); value of 2nd turning point (value2)
        #-absolute value difference between 1st and 2nd turning points
        #-the frame number of 1st turning number (start_loc :start location of cycle)
        #-the frame number of 2nd turning number (end_loc :end location of cycle)
        self.last_cycle_1=[0,-1,0,-1,0,0,0]  
        self.last_cycle_2=[0,-1,0,-1,0,0,0]
        
        self.complete_cycle_1=True #whether the cycle is completed with two points, stay True or False for a period of time
        self.complete_cycle_2=True
        self.complete_indication_1=False #whether the cycle is completed with two different turning points, Stay true in only ONE frame
        self.complete_indication_2=False
        self.updown_complete=False       # whether the updown cycle is complete
        self.updown_need_update=False    # when a 'updown' appears, it will stay true until next cycle appears
                                    # It is used for avoiding that the cycle ends with an non-minimum turning point
        
        self.start_shoulder_flag=False #flag to start processing the shoulder when press some key
        self.pt_full_flag=False        #flag to denote whether there are enough points in pt_que
        self.pt_filt_full_flag=False   #flag to denote whether there are eoungh points in pt_filt_que
        self.shoulder_roll_count=0       #count the shoulder roll numbercur_frame=0
        self.shoulder_updown_count=0     #count the shoulder updown number
        
        self.calibration_flag=False
        self.min_test=[0.8,0.8,0.3]
        self.y_threshold=0.015
        self.z_yplus_ratio=0.3
        self.dis_z_yplus_ratio=0.3
        self.move_count=0
        
    #----------------------------------
    # Shoulder information processing functions
        
    #-if the latter data is larger, then return 1
    #-if the former data is larger, then return -1
    #-if the same, then return 0
    def sign(self,former,latter):
        if former>latter:
            return -1
        elif former<latter:
            return 1
        else:
            return 0
    
    #-retuen the signs (-1,0 or 1, as described in 'sign' function) of each 
    # junction points pair in a data que
    def returnSign(self,pt_que):
        sign_que=[]
        for i in range(1,7):
            sign_que.append(self.sign(pt_que[i-1],pt_que[i]))
        return sign_que
    
    #-Accomplish a convolution of a data que and gaussian filter array, and 
    # return the convolution result (only one number)
    def gaussianFilt(self,pt_que):
        #gaussian_array=[0.0044,0.0540,0.2420,0.3992,0.2420,0.0540,0.0044] #modified gaussian sigma=1
        return np.dot(pt_que,[0.0044,0.0540,0.2420,0.3992,0.2420,0.0540,0.0044])    
        
    #-Find if there is a maximum(peak) or minimum(vally) pattern in the input data sequence
    #-Return: 1=peak; -1=vally; 0=neither peak or vally
    def sequenceMaxMinPattern(self,pt_que,sign_que):
        middle=pt_que[3]
        max_flag=True
        min_flag=True
        for i in pt_que:
            if i>middle:
                max_flag=False
                break
        for i in pt_que:
            if i<middle:
                min_flag=False
                break
        head=sign_que[0]+sign_que[1]+sign_que[2]
        if(head>=1 and max_flag):
            return 1    # for max_pattern(peak)
        elif(head<=-1 and min_flag):
            return -1   # for min_pattern(vally)
        else:
            return 0
    
    #-find turning point function (peak and valley points)   
    #-if find the turning point,then turning_flag=True
    #-if find a new turning point, which is the same kind (both are peak or vally)
    # as the last one, and last turning point is not a max or min, then update (
    # update_flag=True and update the last_convex list)
    def findTurning(self,cur_data,pt_que,pt_filt_que,last_convex,min_threshold):
        #--definition of variable of processing function part 
        cur_state=0         # state in the current recognition window
        update_flag=False   # When there is a turning point in the recognition window, it becomes True
        turning_flag=False  # When there is a turning point which is the same state as last turning
                            # point (both are peak or vally) in last_convex and it larger(for peak) or, 
                            # smaller than last one, it means last convex need to be corrected (it is 
                            # not a maximum or minimum)
        
        #-input new raw data and filted
        if(len(pt_que)<7):
            pt_que.append(cur_data)
            pt_filt_que.append(self.gaussianFilt(pt_que))
            
        #-- find turning point --
        cur_state=self.sequenceMaxMinPattern(pt_filt_que,self.returnSign(pt_filt_que))
        if(cur_state==1 or cur_state==-1):
            if(last_convex[0]==0):
                last_convex[0]=cur_state
                last_convex[1]=pt_filt_que[3]
                turning_flag=True
            else:
                if(cur_state!=last_convex[0]):  # current turning point is different (state) from last one
                    if((cur_state==1 and pt_filt_que[3]-last_convex[1]>min_threshold) or \
                    (cur_state==-1 and pt_filt_que[3]-last_convex[1]<-min_threshold)):
                        last_convex[0]=cur_state
                        last_convex[1]=pt_filt_que[3]
                        turning_flag=True
                else:   # current turning point is the same (state) as the last one
                    if(cur_state==1 and last_convex[1]<pt_filt_que[3]): # for peak
                        last_convex[0]=cur_state
                        last_convex[1]=pt_filt_que[3]
                        update_flag=True
                        turning_flag=True
                    elif(cur_state==-1 and last_convex[1]>pt_filt_que[3]):  # for vally
                        last_convex[0]=cur_state
                        last_convex[1]=pt_filt_que[3]
                        update_flag=True
                        turning_flag=True
        #-- find turning point over--
        pt_que.popleft()
        pt_filt_que.popleft()
        return turning_flag,update_flag
    
    #-clear all information in the cycle list
    def clearCycle(self,cycle):
        cycle[0]=0      # state of 1st turning point (state1)
        cycle[1]=-1     # value of 1st turning point (value1)
        cycle[2]=0      # state of 2nd turning point (state2)
        cycle[3]=-1     # value of 2nd turning point (value2)
        cycle[4]=0      # absolute value difference between 1st and 2nd turning points
        cycle[5]=65535  # the frame number of 1st turning number (start_loc :start location of cycle)
        cycle[6]=65535  # the frame number of 2nd turning number (end_loc:end location of cycle)
    
    #-when the two time periods of SJoint_Z and STop_Y get overlapped, then return True
    def timeOverlap(self,cycle_1_start,cycle_1_end,cycle_2_start,cycle_2_end):
        return_flag=False
        if(cycle_1_start<cycle_2_start and cycle_1_end>cycle_2_start):
            if(cycle_1_end<cycle_2_end):
                return_flag=True
        elif(cycle_1_start>cycle_2_start and cycle_1_start<cycle_2_end):
            if(cycle_1_end>cycle_2_end):
                return_flag=True
        elif(cycle_1_start==cycle_2_start and abs(cycle_1_end-cycle_2_end)<3):
            return_flag=True
        elif(cycle_1_end==cycle_2_end and abs(cycle_1_start-cycle_2_start)<3):
            return_flag=True
        return return_flag
    
    def updateThreshold(self,y_threshold,z_yplus_ratio,dis_z_yplus_ratio,min_test \
                        ,last_cycle_1,last_cycle_2,move_count,calibration_flag):
        if not calibration_flag:
            return y_threshold,z_yplus_ratio,dis_z_yplus_ratio,0 # if it is not during the initialsation, then doesn't update
        if move_count>=8:
            return y_threshold,z_yplus_ratio,dis_z_yplus_ratio,1 # the initialsation has been complete before this cycle
        if(last_cycle_2[4]<0.015):
            return y_threshold,z_yplus_ratio,dis_z_yplus_ratio,2 # the movement is too small
            
        if(move_count<=4):  #the rolls threshold calibration
            new_ratio=last_cycle_1[4]/last_cycle_2[4]
            if(y_threshold>last_cycle_2[4]):
                y_threshold=last_cycle_2[4]*0.8
            ### test use only
            if(min_test[0]>last_cycle_2[4]):
                min_test[0]=last_cycle_2[4]
            if(min_test[1]>new_ratio):
                min_test[1]=new_ratio
            ### test use only
        else:   #the updown threshold calibration
            new_ratio=last_cycle_1[4]/last_cycle_2[4]
            if(dis_z_yplus_ratio<new_ratio):
                dis_z_yplus_ratio=new_ratio
            ### test use only
            if(min_test[2]<new_ratio):
                min_test[2]=new_ratio
            ### test use only
        if(move_count==4):
            if(y_threshold<min_test[0]):
                y_threshold=min_test[0]*0.8
            if(z_yplus_ratio<min_test[1]):
                z_yplus_ratio=min_test[1]
        if(dis_z_yplus_ratio>z_yplus_ratio and move_count==8):
            z_yplus_ratio=(dis_z_yplus_ratio+z_yplus_ratio)/2
        return y_threshold,z_yplus_ratio,dis_z_yplus_ratio,0
        
    #-processing the shoulder data in one loop
    def processShoulderOnce(self,cur_data_1,cur_data_2,cur_frame):
        roll_update_flag=False
        self.cur_data_1=cur_data_1
        self.cur_data_2=cur_data_2
        self.cur_frame=cur_frame
        #---get the pt_que filled
        if(not self.pt_full_flag):
            #-----insert data into the que
            self.pt_que_1.append(self.cur_data_1)  
            self.pt_que_2.append(self.cur_data_2)
            if(self.cur_data_1==-1 or abs(self.cur_data_1-self.pre_data_1)>0.6 \
                or self.cur_data_2==-1 or abs(self.cur_data_2-self.pre_data_2)>0.6):
                self.pt_que_1.clear()
                self.pt_que_2.clear()
            elif(len(self.pt_que_1)==7):
                #---now there are 6 points in side pt_que
                self.pt_full_flag=True
        
        #---get the pt_filt_que filled
        if(self.pt_full_flag and (not self.pt_filt_full_flag)):
            # ---detect the unavailable data
            if(self.cur_data_1==-1 or type(self.cur_data_1)=='NoneType'):
                self.cur_data_1=self.pre_data_1
            if(self.cur_data_2==-1 or type(self.cur_data_2)=='NoneType'):
                self.cur_data_2=self.pre_data_2
            #-----insert data into the que
            if(len(self.pt_que_1)<7):
                self.pt_que_1.append(self.cur_data_1)  
                self.pt_que_2.append(self.cur_data_2)
            self.pt_filt_que_1.append(self.gaussianFilt(self.pt_que_1))
            self.pt_filt_que_2.append(self.gaussianFilt(self.pt_que_2))
            if (len(self.pt_filt_que_1)==7):
                self.pt_filt_full_flag=True
        
        if(self.pt_full_flag and self.pt_filt_full_flag):
            #----the main processing part----
            #----- if current data is unavailable, use previous frame data instead
            if(self.cur_data_1==-1 or type(self.cur_data_1)=='NoneType'):
                self.cur_data_1=self.pre_data_1
            if(self.cur_data_2==-1 or type(self.cur_data_2)=='NoneType'):
                self.cur_data_2=self.pre_data_2
            
            #----- find the maximum and minimum/turning point
            self.turning_flag_1,self.update_flag_1=self.findTurning(self.cur_data_1,\
                self.pt_que_1,self.pt_filt_que_1,self.last_convex_1,self.min_threshold_1)
            self.turning_flag_2,self.update_flag_2=self.findTurning(self.cur_data_2,\
                self.pt_que_2,self.pt_filt_que_2,self.last_convex_2,self.min_threshold_2)
                
            #------update the last cycle information------
            if(self.turning_flag_1 and (not self.update_flag_1)): # a new turning point appear
                if(self.complete_cycle_1 and self.last_convex_1[0]==-1):  # this is the 1st turning point in a cycle
                    self.clearCycle(self.last_cycle_1)   # clear all the information in the cycle
                    self.last_cycle_1[0]=self.last_convex_1[0]
                    self.last_cycle_1[1]=self.last_convex_1[1]
                    self.last_cycle_1[5]=self.cur_frame-6
                    self.complete_cycle_1=False
                    self.complete_indication_1=False
                elif(self.last_cycle_1[0]==-1 and self.last_convex_1[0]==1):  # this is the 2nd turning point in a cycle
                    self.last_cycle_1[2]=self.last_convex_1[0]
                    self.last_cycle_1[3]=self.last_convex_1[1]
                    self.last_cycle_1[4]=abs(self.last_convex_1[1]-self.last_cycle_1[1])
                    self.last_cycle_1[6]=self.cur_frame-6  
                    self.complete_cycle_1=True
                    self.complete_indication_1=True
            elif(self.update_flag_1):    # the last cycle needs to update
                if(not self.complete_cycle_1):   # the 1st turning point need update
                    self.last_cycle_1[0]=self.last_convex_1[0]
                    self.last_cycle_1[1]=self.last_convex_1[1]
                    self.last_cycle_1[5]=self.cur_frame-6
                else:                       # the 2st turning point need update, also update end_loc and abs_diff
                    self.last_cycle_1[2]=self.last_convex_1[0]
                    self.last_cycle_1[3]=self.last_convex_1[1]
                    self.last_cycle_1[4]=abs(self.last_convex_1[1]-self.last_cycle_1[1])
                    self.last_cycle_1[6]=self.cur_frame-6
                    self.complete_cycle_1=True
                    self.complete_indication_1=True
               
            if(self.turning_flag_2 and (not self.update_flag_2)):
                if(self.complete_cycle_2 and self.last_convex_2[0]==1):
                    self.clearCycle(self.last_cycle_2)
                    self.last_cycle_2[0]=self.last_convex_2[0]
                    self.last_cycle_2[1]=self.last_convex_2[1]
                    self.last_cycle_2[5]=self.cur_frame-6
                    self.complete_cycle_2=False
                    self.complete_indication_2=False
                    self.updown_complete=False
                    self.updown_need_update=False
                elif(self.last_cycle_2[0]==1 and self.last_convex_2[0]==-1):
                    self.last_cycle_2[2]=self.last_convex_2[0]
                    self.last_cycle_2[3]=self.last_convex_2[1]
                    self.last_cycle_2[4]=abs(self.last_convex_2[1]-self.last_cycle_2[1])
                    self.last_cycle_2[6]=self.cur_frame-6
                    self.complete_cycle_2=True
                    self.complete_indication_2=True
                    self.updown_complete=True
            elif(self.update_flag_2):
                if(not self.complete_cycle_2):
                    self.last_cycle_2[0]=self.last_convex_2[0]
                    self.last_cycle_2[1]=self.last_convex_2[1]
                    self.last_cycle_2[5]=self.cur_frame-6
                else:
                    self.last_cycle_2[2]=self.last_convex_2[0]
                    self.last_cycle_2[3]=self.last_convex_2[1]
                    self.last_cycle_2[4]=abs(self.last_convex_2[1]-self.last_cycle_2[1])
                    self.last_cycle_2[6]=self.cur_frame-6
                    self.complete_cycle_2=True
                    self.complete_indication_2=True
                    self.updown_complete=True
            #------update the last cycle information over------
            
            #---detect the cycle
            if(self.complete_indication_2 and self.complete_indication_1):
                if(self.timeOverlap(self.last_cycle_1[5],self.last_cycle_1[6],self.last_cycle_2[5],self.last_cycle_2[6])):
                    if(self.last_cycle_2[4]>self.y_threshold and self.last_cycle_2[4]>=self.last_cycle_1[4]*self.z_yplus_ratio \
                    and self.last_cycle_1[4]>self.last_cycle_2[4]*0.5):
                        self.shoulder_roll_count+=1                        
                        self.complete_indication_1=False
                        self.complete_indication_2=False
                        roll_update_flag=True
                        if(self.calibration_flag and self.move_count<4):
                            self.move_count+=1
                            self.y_threshold,self.z_yplus_ratio,self.dis_z_yplus_ratio,self.test_flag\
                                =self.updateThreshold(self.y_threshold,self.z_yplus_ratio,self.dis_z_yplus_ratio,\
                                self.min_test,self.last_cycle_1,self.last_cycle_2,self.move_count,self.calibration_flag)
        
            if(self.updown_complete and self.last_cycle_2[4]>self.y_threshold):
                if(self.last_cycle_1[4]<0.001 and (not self.updown_need_update)):
                    if(self.timeOverlap(self.last_cycle_1[5],self.last_cycle_1[6],self.last_cycle_2[5],self.last_cycle_2[6])):
                        self.shoulder_updown_count+=1
                        self.updown_complete=False
                        self.updown_need_update=True
                        if(self.calibration_flag and self.move_count>=4):
                            self.move_count+=1
                            self.y_threshold,self.z_yplus_ratio,self.dis_z_yplus_ratio,self.test_flag\
                                =self.updateThreshold(self.y_threshold,self.z_yplus_ratio,self.dis_z_yplus_ratio,\
                                self.min_test,self.last_cycle_1,self.last_cycle_2,self.move_count,self.calibration_flag)
        
            #----the main processing part over----
        #---update the previous frame data
        self.pre_data_1=self.cur_data_1
        self.pre_data_2=self.cur_data_2 
        if(self.move_count>=8):
            self.calibration_flag=False
        return roll_update_flag
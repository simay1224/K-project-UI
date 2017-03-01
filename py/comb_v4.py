# -*- coding: utf-8 -*-
"""
Created on Fri Sep 02 19:04:40 2016

@author: user
"""

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from KNTfinger import *
import QKNTshlder_1 as SDTP
import ctypes
import pygame,h5py,datetime
import pdb,time,cv2,operator,cv,cPickle,math
import numpy as np
#if sys.hexversion >= 0x03000000:
#    import _thread as thread
#else:
#    import thread
fps = 20

bkimg = np.zeros([1080,1920])
fimgs = []
bdidximg = []
depthimg = []
bdjoints = []
# colors for drawing different bodies 
SKELETON_COLORS = [pygame.color.THECOLORS["red"], 
                  pygame.color.THECOLORS["blue"], 
                  pygame.color.THECOLORS["green"], 
                  pygame.color.THECOLORS["orange"], 
                  pygame.color.THECOLORS["purple"], 
                  pygame.color.THECOLORS["yellow"], 
                  pygame.color.THECOLORS["violet"]]




class BodyGameRuntime(object):
    def __init__(self):
        global bkimg
        pygame.init()

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()
        self.now = datetime.datetime.now() 
        self.dstr = 'data'+repr(self.now.month).zfill(2)+repr(self.now.day).zfill(2)+repr(self.now.hour).zfill(2)+repr(self.now.minute).zfill(2)
        self.fno = 0
        
        
        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1), 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

        pygame.display.set_caption("Kinect Body detection")

        # Loop until the user clicks the close button.
        self._done = False
        self._handmode = False
        self.vid_rcd = False
        self.clipNo = 0
        #self.cntno = 0
        # Kinect runtime object, we want only color and body frames 
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body|PyKinectV2.FrameSourceTypes_Depth|PyKinectV2.FrameSourceTypes_BodyIndex)    
        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)
        # here we will store skeleton data 
        self._bodies = None
        
        time.sleep(5)


        if self._kinect.has_new_color_frame():
            frame =  self._kinect.get_last_color_frame().reshape([1080,1920,4])[:,:,:3]                   
            bkimg = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
      
            print ('extract bg....')
        else:
            print 'failed to extract.....'
        
        #time.sleep(3)         
                
#========================= original part =======================================
    def draw_body_bone(self, joints, jointPoints, color, joint0, joint1):
        joint0State = joints[joint0].TrackingState;
        joint1State = joints[joint1].TrackingState;

        # both joints are not tracked
        if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked): 
            return

        # both joints are not *really* tracked
        if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
            return

        # ok, at least one is good 
        start = (jointPoints[joint0].x, jointPoints[joint0].y)
        end = (jointPoints[joint1].x, jointPoints[joint1].y)

        try:
            pygame.draw.line(self._frame_surface, color, start, end, 8)
            #lines(Surface, color, closed, pointlist, width=1)
        except: # need to catch it due to possible invalid positions (with inf)
            pass

    def draw_body(self, joints, jointPoints, color):
        # Torso
        #pdb.set_trace()
        
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft);
        
        # Right Arm    
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight);


        # Left Arm
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft);



    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()
        
    def appendimg(self,frame):
        global fimgs
        fimgs.append(frame)    
    def appendbdimg(self,frame):
        global bdidximg
        bdidximg.append(frame)
    def appenddimg(self,frame):
        global depthimg
        depthimg.append(frame)
    
    
    def convert2vid(self,bdjoints):
        import datetime        
        now = datetime.datetime.now()        
        vid = 'kinect'+repr(now.month).zfill(2)+repr(now.day).zfill(2)+repr(now.hour).zfill(2)+repr(now.minute).zfill(2)+'.avi'        
        video = cv.CreateVideoWriter(vid, cv.CV_FOURCC('L','A','G','S'), fps, (1920,1080),True)
        #st = time.clock()
        #pdb.set_trace()
        print 'making video .....'
        for i in fimgs:
            bitmap = cv.CreateImageHeader((1920,1080), cv.IPL_DEPTH_8U, 3)                
            cv.SetData(bitmap, i.tostring(),i.dtype.itemsize * 3 * i.shape[1])                
            cv.WriteFrame(video,bitmap)  
        #print time.clock()-st
        print 'there r total '+repr(len(fimgs))+' frames'
        del video
        cPickle.dump(bdjoints,file('bodyjoints'+repr(now.month).zfill(2)+repr(now.day).zfill(2)+repr(now.hour).zfill(2)+repr(now.minute).zfill(2)+'.pkl','wb'))

    def convert2othvid(self,string,imgs):       
        now = datetime.datetime.now()        
        vid = string+repr(now.month).zfill(2)+repr(now.day).zfill(2)+repr(now.hour).zfill(2)+repr(now.minute).zfill(2)+'.avi'        
        video = cv.CreateVideoWriter(vid, cv.CV_FOURCC('L','A','G','S'), fps, (512,424),True)
        #st = time.clock()
        #pdb.set_trace()
        print 'making video .....'
        for i in imgs:
            bitmap = cv.CreateImageHeader((512,424), cv.IPL_DEPTH_8U, 3)                
            cv.SetData(bitmap, i.tostring(),i.dtype.itemsize *3* i.shape[1])                
            cv.WriteFrame(video,bitmap)  
        #print time.clock()-st
        print 'there r total '+repr(len(fimgs))+' frames'
        del video

    def typetext(self,string,pos,color = (255,255,0),fontsize=60,bold=False):
        myfont = pygame.font.SysFont("Arial", fontsize,bold)
        label = myfont.render(string, 1, color)
        self._frame_surface.blit(label, pos)

    def run(self):
        #--------- initial -------       
        global video
        
        cur_frame=0
        rec_right_shoudler=SDTP.ShoulderTops()   #recording the shoudler movements(record data)
        pro_right_shoulder=SDTP.ShoulderRoll()   #detecting the shoulder movements(processing data)
        #-all the number in variable names below indicates:        
        start_shoulder_flag=False #flag to start processing the shoulder when press some key
        
        #-for key pressing
        wait_key_count=3
        # -------- Main Program Loop -----------
        while not self._done:
            
            ST = time.clock()
            bddic={}
            Jdic ={}
            
#            error_code=[1,1] # store the error of patient's behavior (###could write more)
#                            #1=correct; 2=rise the arm too high;
#                            #3=something on the shoulder; 4=not facing camera
#                            #5=too far from camera
            joints_oneframe=[]
#            joints_vector=[]
            
            #--key pressing--
            if(wait_key_count<3):
                wait_key_count+=1
            if(pygame.key.get_focused() and wait_key_count>=3):
                press=pygame.key.get_pressed()
                wait_key_count=0
                if press[27]==1:
                    self._done=True 
                    #print self.cntno
                if press[104]==1: #use 'h' to open/close hand detection
                    if self._handmode==True:
                        self._handmode = False
                    else:
                        self._handmode = True
                if press[49]==1:  #.#1 open/close shoulder detection
                    if start_shoulder_flag==True:
                        start_shoulder_flag=False
                    else: 
                        start_shoulder_flag=True
                if press[50]==1 and start_shoulder_flag: #.#2 initial setting
                    pro_right_shoulder.calibration_flag=True
                    pro_right_shoulder.shoulder_roll_count=0
                    pro_right_shoulder.shoulder_updown_count=0
                if press[114]==1: # use 'r' to open/close video recording
                
                    if self.clipNo ==0:
                        self.dataset = h5py.File(self.dstr+'.h5','w')
                        self.dataset =h5py.File(self.dstr+'.h5', 'r')
                        # img group
                        self.imgs = self.dataset.create_group('imgs')
                        self.cimgs = self.imgs.create_group('cimgs')
                        self.dimgs = self.imgs.create_group('dimgs')
                        self.bdimgs = self.imgs.create_group('bdimgs')
                        # other data
#                        self.data = self.dataset.create_group('data') 
#                        self.jpts = self.data.create_group('jointspts') # jointspts
#                        self.joints = self.data.create_group('joints')  # joints
#                        self.jvct = self.data.create_group('joints_vector')  # joints_vector
                        
                        
                    if self.vid_rcd == False:
                        self.vid_rcd = True
                        self.clipNo += 1
                    else:
                        self.vid_rcd = False            
            #--key pressing over--
                        
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop

                elif event.type == pygame.VIDEORESIZE: # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'], 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
                            
            
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = frame.reshape(1080,1920,4)[:,:,:3]
                
            #--- Cool! We have a body frame, so can get skeletons
            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()
                
            if self._kinect.has_new_body_index_frame():
                bodyidx = self._kinect.get_last_body_index_frame()
                bodyidx=bodyidx.reshape((424,512))

            if self._kinect.has_new_depth_frame():
                dframe,oridframe = self._kinect.get_last_depth_frame()
                dframe=dframe.reshape((424,512))                                

            # --- draw skeletons to _frame_surface
            
                        
              
            if self._bodies is not None:
                
                #self._kinect.testtable()
                closest_ID=-1
                cSS_dist=20 #closest SpineShoulder distance
                
                for i in range(0, self._kinect.max_body_count):                    
                    body = self._bodies.bodies[i]
                    
                    if not body.is_tracked: 
                        #self.typetext('No human be detected ',(100,100))
                        continue
                    if body.joints[20].Position.z<=cSS_dist:
                        closest_ID=i
                        cSS_dist=body.joints[20].Position.z
                        
                if (closest_ID!=-1):
                    body = self._bodies.bodies[closest_ID]
                    joints = body.joints 
                    
                    for ii in xrange(25):
                        Jdic[ii] = joints[ii]
                    
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                    joint_points_depth =self._kinect.body_joints_to_depth_space(joints)
                    
                    
                    if self._handmode: # whether hand mode is on or not
                        
                        hsvimg = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)    
                        tmp = np.abs(hsvimg[:,:,2] - bkimg[:,:,2] )                                           
                        fgimg = np.zeros([1080,1920])                  
                        fgimg[tmp>80] = 1 
                                     
                    
                        if (body.hand_left_state == 2)| (body.hand_left_state == 0): #hand open
                            Lhand,bddic['Loffset'],Lrad = handseg(fgimg,joint_points[6],joint_points[7])                  
                            bddic['Lhand'] = draw_hand(Lhand,frame,bddic['Loffset'],Lrad,joint_points[6],SKELETON_COLORS[i],self._frame_surface)
                            self.typetext('Lhand :'+repr(len(bddic['Lhand'])) +' fingers ',(100,100)) 
                            if  (body.hand_left_state == 2) & ( len(bddic['Lhand'])<=3):
                                self.typetext('Open your left hand more !!',(1000,100),(255,0,0),60,True)
                            else:
                                self.typetext('nice job !!',(1600,100),(0,255,0))
                        elif (body.hand_left_state == 4): # Lasso
                            Lhand,bddic['Loffset'],Lrad = handseg(fgimg,joint_points[6],joint_points[7])                  
                            bddic['Lhand'] = draw_hand(Lhand,frame,bddic['Loffset'],Lrad,joint_points[6],SKELETON_COLORS[i],self._frame_surface)
                            self.typetext('Lhand :'+repr(len(bddic['Lhand'])) +' fingers ',(100,100))
                                
                        elif body.hand_left_state ==3 : # closed
                            self.typetext('Lhand : closed',(100,100))
                        else:
                            self.typetext('Lhand : Not detect',(100,100))
                            
                        self.typetext('Rhand :'+repr(body.hand_right_state) ,(100,200))     
                        if (body.hand_right_state == 2)|(body.hand_right_state == 0):
                            Rhand,bddic['Roffset'],Rrad = handseg(fgimg,joint_points[10],joint_points[11])
                            bddic['Rhand'] = draw_hand(Rhand,frame,bddic['Roffset'],Rrad, joint_points[10],SKELETON_COLORS[i],self._frame_surface) 
                            self.typetext('Rhand :'+repr(len(bddic['Rhand'])) +' fingers ',(100,150))
                            if  (body.hand_right_state == 2) & (len(bddic['Rhand'])<=3):
                                self.typetext('Open your right hand more !!',(1000,150),(255,0,0),60,True)
                            else:
                                self.typetext('nice job !!',(1600,150),(0,255,0))
                            
                        elif (body.hand_right_state == 4):
                            Rhand,bddic['Roffset'],Rrad = handseg(fgimg,joint_points[10],joint_points[11])
                            bddic['Rhand'] = draw_hand(Rhand,frame,bddic['Roffset'],Rrad, joint_points[10],SKELETON_COLORS[i],self._frame_surface) 
                            self.typetext('Rhand :'+repr(len(bddic['Rhand'])) +' fingers ',(100,150))                                                              
                        elif body.hand_right_state ==3 :
                            self.typetext('Rhand : closed',(100,150))
                        else:
                            self.typetext('Rhand : Not detect',(100,150))
                        

                    self.draw_body(joints, joint_points, SKELETON_COLORS[i])
                    
#==============================================================  
                    #### modified 09/18/2016####
                    #--shoulder data recording--                    
                    joints_oneframe.append(joints[4])
                    joints_oneframe.append(joints[8])
                    joints_oneframe.append(joints[20])                    
                    
                    #---find two shoulder tops
                    tops=rec_right_shoudler.findShouderTops(self._kinect,bodyidx,  \
                        joint_points_depth,joints,dframe,closest_ID) 
                    #---append the left & right shoulder tops
                    joints_oneframe.append(tops[2])
                    joints_oneframe.append(tops[3])
                    #--shoulder data recording over--
                    
                    #--shoudler data processing part--
                    if(start_shoulder_flag):
                        #---get the data for processing
                        if len(joints_oneframe)>0:
                            frame=joints_oneframe
                            temp_ssy=frame[2].Position.y
                            temp_ssz=frame[2].Position.z
                            cur_data_1=frame[1].Position.z-temp_ssz
                            if(frame[4]==[]):
                                cur_data_2=-1
                            else:
                                cur_data_2=frame[4].y-temp_ssy
                    
                        pro_right_shoulder.processShoulderOnce(cur_data_1,cur_data_2,cur_frame)
                        
                    bddic['jointspts'] = joint_points
                    bddic['depth_jointspts'] = joint_points_depth
                    bddic['joints'] = Jdic                        
                    bddic['joints_vector'] = joints_oneframe
                    bddic['vidclip'] = self.clipNo

#==============================================================                   
            else:
                self.typetext('No human be detected ',(100,100))
                
            #--find ID and extract skeleton info and draw over--
                    
            cur_frame+=1

            if self.vid_rcd == True:
                self.typetext('Video Recording' ,(1550,20),(255,0,0))
                
                self.cimgs.create_dataset('img_'+repr(self.fno).zfill(4), data = frame)
                self.bdimgs.create_dataset('bd_'+repr(self.fno).zfill(4), data = np.dstack((bodyidx,bodyidx,bodyidx)))
                self.dimgs.create_dataset('d_'+repr(self.fno).zfill(4), data = np.dstack((dframe,dframe,dframe)))
                self.fno += 1
                bdjoints.append(bddic)
            else:
                self.typetext('Not Recording' ,(1550,20),(255,0,0))
            
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            
            if(len(joints_oneframe)>0 and closest_ID>=0):
                # render text
                if(start_shoulder_flag):
                    string_1='Shoulder Rolls: '+ str(pro_right_shoulder.shoulder_roll_count)    # modified 09/18/2016
                    #string_2='Shoulder Up&down :' +str(pro_right_shoulder.shoulder_updown_count)    # modified 09/18/2016
                    #if(pro_right_shoulder.calibration_flag):
                    #    self.typetext('Initail personalization ...' ,(100,720),(128,250,180))
                    #    string_2+='  ini_count: '+str(pro_right_shoulder.move_count)
                #else:
                #    string_1='Shoulder recognition NOT start yet'
                #    string_2='Press 1 to start'

                
                    self.typetext(string_1 ,(100,800),(0,128,255))
                    #self.typetext(string_2 ,(100,850),(0,128,255))
                
                if(rec_right_shoudler.error_code[1]==2):
                    self.typetext('Please put your arm down' ,(500,50),(255,0,0)) 
                elif(rec_right_shoudler.error_code[1]==3):
                    self.typetext('What is on your shoulder?' ,(500,50),(255,0,0)) 
                elif(rec_right_shoudler.error_code[0]==4):
                    self.typetext('Please step back!' ,(500,50),(255,0,0)) 
                elif(rec_right_shoudler.error_code[0]==5):
                    self.typetext('Please facing the camera!' ,(500,50),(255,0,0))
                elif(rec_right_shoudler.error_code[0]==6):
                    self.typetext('Please stand vertically!' ,(500,50),(255,0,0)) 
                
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()
            
                        
            
            # --- Go ahead and update the screen with what we've drawn.
            #pygame.display.flip()

            # --- Limit to 60 frames per second
            self._clock.tick(fps)
            
 
                    
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop
                elif event.type == pygame.VIDEORESIZE: # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'], 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
        # Close our Kinect sensor, close the window and quit.
            print time.clock()-ST
               
            
        self._kinect.close()
        pygame.quit()
        
        try:
            cPickle.dump(bdjoints,file(self.dstr+'.pkl','wb'))
            self.dataset.close()
        except:
            pass


__main__ = "Kinect v2 Body Game"

game = BodyGameRuntime();

game.run();

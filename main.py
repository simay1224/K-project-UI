# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 10:27:23 2016

@author: medialab
"""

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from Kfunc import *
from Kfunc.IO import *
from Kfunc.finger import *
from Kfunc.shlder import *
from Kfunc.skel import *
from Kfunc.model import *
import QKNTshlder_1 as SDTP
import ctypes
import pygame,h5py,datetime
import pdb,time,cv2,cPickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#if sys.hexversion >= 0x03000000:
#    import _thread as thread
#else:
#    import thread
fps = 30

bkimg = np.zeros([1080,1920])
bdjoints = []
Jarray  = {}  # joint array

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
        self.dstr = './output/data'+repr(self.now.month).zfill(2)+repr(self.now.day).zfill(2)+repr(self.now.hour).zfill(2)+repr(self.now.minute).zfill(2)
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
        self.model_draw = False
        self.model_frame = False
        self.clipNo = 0
        #self.cntno = 0
        # Kinect runtime object, we want only color and body frames 
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body|PyKinectV2.FrameSourceTypes_Depth|PyKinectV2.FrameSourceTypes_BodyIndex)    
        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)
        # here we will store skeleton data 
        self._bodies = None
        self.jorder  = [0,1,2,3,4,5,6,8,9,10,20] #joints order we care
        time.sleep(5)


        if self._kinect.has_new_color_frame():
            frame =  self._kinect.get_last_color_frame().reshape([1080,1920,4])[:,:,:3]                   
            bkimg = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
      
            print ('extract bg....')
        else:
            print 'failed to extract.....'
                              


    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()
        


    def run(self):
        #--------- initial -------       
        global video
        
        cur_frame=0
        rec_Rshld=SDTP.ShoulderTops()   #recording the shoudler movements(record data)
        pro_Rshld=SDTP.ShoulderRoll()   #detecting the shoulder movements(processing data)
        Rb = {}
        Rt = {}
        Rk = {}

        for ii in self.jorder:
            Rk[ii]=[]
            Rt[ii]=[]
            Rb[ii]=[]
        
        #-all the number in variable names below indicates:        
        shld_flag=False #flag to start processing the shoulder when press some key
        
        #-for key pressing
        wait_key_count=3
        # -------- Main Program Loop -----------
        while not self._done:
            
            #ST = time.clock()
            bddic={}
            Jdic ={}
            Jpf = []

            

            
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
                if press[109]==1: #use 'm' to open/close human model
                    if self.model_draw==True:
                        self.model_draw = False
                        self.model_frame = False
                    else:
                        self.model_draw = True
                        
                if press[49]==1:  #.#1 open/close shoulder detection
                    print 'I am innnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn'
                    if shld_flag==True:
                        shld_flag=False
                    else: 
                        shld_flag=True
                if press[50]==1 and shld_flag: #.#2 initial setting
                    pro_Rshld.calibration_flag=True
                    pro_Rshld.shoulder_roll_count=0
                    pro_Rshld.shoulder_updown_count=0
                if press[114]==1: # use 'r' to open/close video recording
                
                    if self.clipNo ==0:
                        self.dataset = h5py.File(self.dstr+'.h5','w')
                        self.dataset =h5py.File(self.dstr+'.h5', 'r')
                        # img group
                        self.imgs = self.dataset.create_group('imgs')
                        self.cimgs = self.imgs.create_group('cimgs')
                        self.dimgs = self.imgs.create_group('dimgs')
                        self.bdimgs = self.imgs.create_group('bdimgs')
                        #self.timestamp = self.imgs.create_group('tstamp')
                        # other data
                     
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
                
            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()
                TimeS = datetime.datetime.now()
                
            if self._kinect.has_new_body_index_frame():
                bodyidx = self._kinect.get_last_body_index_frame()
                
                bodyidx=bodyidx.reshape((424,512))

            if self._kinect.has_new_depth_frame():
                dframe,oridframe = self._kinect.get_last_depth_frame()
                dframe=dframe.reshape((424,512))                                
            
            if self._bodies is not None:
                
                #self._kinect.testtable()
                closest_ID=-1
                cSS_dist=20 #closest SpineShoulder distance
                
                for i in range(0, self._kinect.max_body_count):                    
                    body = self._bodies.bodies[i]
                    
                    if not body.is_tracked: 
                        continue
                    if body.joints[20].Position.z<=cSS_dist:
                        closest_ID=i
                        cSS_dist=body.joints[20].Position.z
                        
                if (closest_ID!=-1):
                    body = self._bodies.bodies[closest_ID]
                    joints = body.joints 
                    
                    #reliable initail
                    

                    
                    
                    for ii in xrange(25):
                        Jdic[ii] = joints[ii]

                    
                    Jps = self._kinect.body_joints_to_color_space(joints) #joint points in color domain
                    dJps =self._kinect.body_joints_to_depth_space(joints) #joint points in depth domain
                    
                    #   ====   fingers detection  ====
                    if self._handmode: 
                        #finger detect and draw
                        fextr(frame,bkimg,body,bddic,Jps,SKELETON_COLORS[i],self._frame_surface)
                        
                    # === joint reliability ===
                    for ii in self.jorder:
                        try : 
                            Jarray[ii].append(np.array([Jdic[ii].Position.x,Jdic[ii].Position.y,Jdic[ii].Position.z]))
                        except:                            
                            Jarray[ii] = []
                            Rb[ii] = []
                            Jarray[ii].append(np.array([Jdic[ii].Position.x,Jdic[ii].Position.y,Jdic[ii].Position.z]))                            
                        Rb[ii].append(rel_behav(Jarray[ii]))
                        
                    rt = rel_trk(Jdic) 
                    rk = rel_kin(Jdic)
                    for ii,jj in enumerate(self.jorder):    
                        Rt[jj].append(rt[ii])
                        Rk[jj].append(rk[ii])
                        
                    Rel = rel_rate(Rb,Rk,Rt,self.jorder)
  
                    #print Rk                      
                    
                    #draw skel
                    draw_body(joints, Jps, SKELETON_COLORS[i],self._frame_surface)
                    draw_Rel_joints(Jps,Rel,self._frame_surface)
                    
                    #draw unify human model
                    if self.model_draw:
                        modJoints = human_mod_pts(joints)
                        
                        if not self.model_frame :
                            fig = plt.figure() 
                            ax = fig.add_subplot(111, projection='3d')
                            keys = modJoints.keys()
                            self.model_frame = True
                        else:
                            plt.cla()
                        
                        draw_human_mod_pts(modJoints,ax,keys)
                        
                        #pdb.set_trace()
                    
                    bddic['timestamp'] = TimeS
                    bddic['jointspts'] = Jps
                    bddic['depth_jointspts'] = dJps
                    bddic['joints'] = Jdic                        
                    bddic['vidclip'] = self.clipNo
                    bddic['Rel'] = Rel
                  
            else:
                typetext(self._frame_surface,'No human be detected ',(100,100))
                
            #--find ID and extract skeleton info and draw over--
                    
            cur_frame+=1
            
            if self.vid_rcd == True:
                typetext(self._frame_surface,'Video Recording' ,(1550,20),(255,0,0))
                
                self.cimgs.create_dataset('img_'+repr(self.fno).zfill(4), data = frame)
                self.bdimgs.create_dataset('bd_'+repr(self.fno).zfill(4), data = np.dstack((bodyidx,bodyidx,bodyidx)))
                self.dimgs.create_dataset('d_'+repr(self.fno).zfill(4), data = np.dstack((dframe,dframe,dframe)))
                #self.timestamp.create_dataset('t_'+repr(self.fno).zfill(4),data =TimeS)
                self.fno += 1
                bdjoints.append(bddic)
            else:
                typetext(self._frame_surface,'Not Recording' ,(1550,20),(0,255,0))
            

            #   ====   Shoulder action detection  ====                    
            if (shld_flag and closest_ID!=-1):
                Jpf = rec_Rshld.findShouderTops(self._kinect,bodyidx,dJps,joints,dframe,closest_ID)[2:4]
                if Jpf!=[]:
                    shld_act(joints,Jpf,pro_Rshld,cur_frame)                    
                shld_text(pro_Rshld,rec_Rshld,self._frame_surface)
                    

                
                
                    
                    
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())    
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()
            

            # --- Limit frames per second
            self._clock.tick(fps)
    
        # Close our Kinect sensor, close the window and quit.
            #print time.clock()-ST
               
            
        self._kinect.close()
        pygame.quit()
        
        
        if bdjoints !=[]:
           cPickle.dump(bdjoints,file(self.dstr+'.pkl','wb')) 
        try:
            self.dataset.close()
        except:
            pass


__main__ = "Kinect v2 Body Game"

game = BodyGameRuntime();
game.run();

# -*- coding: utf-8 -*-
"""
Created on Mon Oct 02 18:02:12 2017

@author: medialab
"""

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from Kfunc.IO     import *
from Kfunc.finger import *
from Kfunc.skel   import skel
from Kfunc.model  import Human_mod   as Hmod
from Kfunc.Rel    import reliability as REL
from Kfunc.GPR    import GPR
from Kfunc.DTW    import DTW_matching
import ctypes,os
import pygame,h5py,datetime
import pdb,time,cv2,cPickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.externals import joblib
from collections import defaultdict


#if sys.hexversion >= 0x03000000:
#    import _thread as thread
#else:
#    import thread
fps = 30

bkimg = np.zeros([1080,1920])


# colors for drawing different bodies 
SKELETON_COLORS = [pygame.color.THECOLORS["red"], 
                  pygame.color.THECOLORS["blue"], 
                  pygame.color.THECOLORS["green"], 
                  pygame.color.THECOLORS["orange"], 
                  pygame.color.THECOLORS["purple"], 
                  pygame.color.THECOLORS["yellow"], 
                  pygame.color.THECOLORS["violet"]]
# GPR
limbidx = np.array([4,5,6,8,9,10,20]) 
gp      = joblib.load('GPR_cluster_800_meter_fix_ex4.pkl')
[MIN,MAX] = h5py.File('model_CNN_0521_K2M_rel.h5','r')['minmax'][:]


# DTW


data       = h5py.File('GT_kinect_EX4_40_40_40.h5','r')
gt_data    = {}
gt_data[1] = data['GT_kinect_1'][:]
gt_data[2] = data['GT_kinect_2'][:]
gt_data[3] = data['GT_kinect_3'][:]
gt_data[4] = data['GT_kinect_4'][:]
data.close()
#status string
Sstr = ['from hands down to T-pose','from T-pose to hands close','finish','from hand close to T-pose',\
        'from T-pose to hands close','from T-pose to hands down']
#goal string
#gstr = ['initial','T-pos','finish the exercise','Hand close','T-pose']

#ani img data
ANI = {} 
anidata = h5py.File('399x219_ex4_comp.h5','r')
ANI[0]  = anidata['M0'][:]
ANI[1]  = anidata['M1'][:]
ANI[2]  = anidata['M2'][:]
ANI[3]  = anidata['M3'][:]
ANI[4]  = anidata['M4'][:]
anidata.close()

class BodyGameRuntime(object):
    def __init__(self):
        global bkimg
        pygame.init()

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()        
        
        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1), 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

        pygame.display.set_caption("Kinect Body detection")


        #self.cntno = 0
        # Kinect runtime object, we want only color and body frames 
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body|PyKinectV2.FrameSourceTypes_Depth|PyKinectV2.FrameSourceTypes_BodyIndex)    
        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
#        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)
        self._frame_surface = pygame.Surface((1920, 1080), 0, 32)
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
        
        self.__param_init__()
        
        
    def __param_init__(self,clean = False):
        

        try:
            if self.bdjoints !=[]:
               cPickle.dump(self.bdjoints,file(self.dstr+'.pkl','wb')) 
               print('save pkl ....')
            
            if clean:
                os.remove(self.dstr+'.pkl')
                print('remove pkl ....')
        except:
            pass
        try:
            self.dataset.close()
            print('save h5py ....')
            if clean:
                os.remove(self.dstr+'.h5')
                print('remove h5py ....')
        except:
            pass
            
        self.bdjoints = []
        self.Jarray  = {}  # joint array
        self.now = datetime.datetime.now() 
        self.dstr = './output/data'+repr(self.now.year)+repr(self.now.month).zfill(2)+repr(self.now.day).zfill(2)+\
                                    repr(self.now.hour).zfill(2)+repr(self.now.minute).zfill(2)
        
        self.scale       = 1.0
        self._done       = False
        self._handmode   = False
        self.vid_rcd     = False
        self.model_draw  = False
        self.model_frame = False
        self.clipNo      = 0
        self.fno         = 0        
        
        # dtw parameter initialize
        self.Dtw = {}
        self.Dtw['decTh']       = 2000
        self.Dtw['cnt']         = 0
        self.Dtw['distp_prev']  = 0         
        self.Dtw['distp_cmp']   = np.inf             
        self.Dtw['oidx']        = 0      # initail
        self.Dtw['gt_idx']      = 0 
        self.Dtw['presv_size']  = 0
        self.Dtw['idxlist']     = []   
        self.Dtw['idx_cmp']     = 0
        self.Dtw['fcnt']        = 0
        #        
        self.Dtw['dpfirst']     = {}
        self.Dtw['dist_p']      = {}
        self.Dtw['deflag_mul']  = defaultdict(lambda:(bool(False)))  
        self.Dtw['seqlist']     = np.array([])                
        self.Dtw['dcnt']        = 0 
        self.Dtw['chk_flag']    = False
        self.Dtw['exechk']      = True
        self.Dtw['deflag']      = False   # decreasing flag
        self.Dtw['onedeflag']   = False
        self.Dtw['segini']      = True  
        self.Dtw['evalstr']     = ''
        #
        
        # ani        
        self.ani_cnt   = 0
        self.ani_bound = 0
        self.ani_order = 0
        
                              


    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()
        
    def reset(self,clean=False):
        self.__param_init__(clean)

    def run(self):
        #--------- initial -------       
        global video

            
            
        cur_frame=0
        
        Rb = defaultdict(list)
        Rt = defaultdict(list)
        Rk = defaultdict(list)
        
        #-all the number in variable names below indicates:        

        #-for key pressing
        wait_key_count=3
        # -------- Main Program Loop -----------
        while not self._done:

            # ani setting
            
            self.ani_bound = ANI[self.Dtw['gt_idx']].shape[0]
            if (self.ani_cnt > (self.ani_bound- 1)) | (self.ani_order != self.Dtw['gt_idx']) :
                self.ani_cnt   = 0
                self.ani_order = self.Dtw['gt_idx']
            
            #ST = time.clock()
            bddic={}
            Jdic ={}
          
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
                        print('recording .......')
                        self.vid_rcd = True
                        self.clipNo += 1
                    else:
                        print('stop recording .......')
                        self.vid_rcd = False 
                        
                if press[105]==1: # use 'i' to reset every parameter
                    print('Reseting ............................')
                    self.reset()
                if press[117]==1: # use 'u' to reset every parameter and remove the save data
                    print('Reseting & trmoving the saved file ................')
                    self.reset(True)
                if press[98]==1: # use 'b' to lager the scale
                    if (self.scale < 2):
                        self.scale = self.scale*1.1
                if press[115]==1:# use 's' to smaller the scale
                    if (self.scale > 0.4): 
                        self.scale = self.scale/1.1
                
            #--key pressing over--
                        
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop

                elif event.type == pygame.VIDEORESIZE: # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'], 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
                            
            
            if self._kinect.has_new_color_frame():
                ori_frame = self._kinect.get_last_color_frame()
                frame     = ori_frame.reshape(1080,1920,4) 
                Height    = int(219 * self.scale)
                Width     = int(399 * self.scale)

                frame[(1009-Height):1009,(1899-Width):1899,:3] = cv2.resize(ANI[self.Dtw['gt_idx']][self.ani_cnt,:,:,:], (Width,Height))
                self.ani_cnt +=1
                self.draw_color_frame(frame, self._frame_surface)
                frame = ori_frame.reshape(1080,1920,4)[:,:,:3]
                
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
                    rec_joints = body.joints 
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
                            self.Jarray[ii].append(np.array([Jdic[ii].Position.x,Jdic[ii].Position.y,Jdic[ii].Position.z]))
                        except:                            
                            self.Jarray[ii] = []
                            Rb[ii] = []
                            self.Jarray[ii].append(np.array([Jdic[ii].Position.x,Jdic[ii].Position.y,Jdic[ii].Position.z]))                            
                        Rb[ii].append(REL.rel_behav(self.Jarray[ii]))
                        
                    rt = REL.rel_trk(Jdic) 
                    rk = REL.rel_kin(Jdic)
                    for ii,jj in enumerate(self.jorder):    
                        Rt[jj].append(rt[ii])
                        Rk[jj].append(rk[ii])
                        
                    Rel,Relary = REL.rel_rate(Rb,Rk,Rt,self.jorder)
                  
                    #draw skel
                    skel.draw_body(joints, Jps, SKELETON_COLORS[i],self._frame_surface,8)
#                    skel.draw_Rel_joints(Jps,Rel,self._frame_surface)
                    
                    if self.Dtw['exechk'] :
                        if not Relary == []:
                            # =================  GPR ====================
#                            
                            _, modJary = Hmod.human_mod_pts(joints,True) #modJary is 7*3 array 
                            modJary = modJary.flatten().reshape(-1,21)   #change shape to 1*21 array
                            reconJ = modJary
#                            if all(ii>0.6 for ii in Relary[limbidx]): # all joints are reliable
##                                print('================ All GOOD ================')
#                                reconJ = modJary      # reconJ is 1*21 array                                
#
#                            else: #contains unreliable joints
#
#                                print('==================')
#                                print('=======GPR========')
#                                print('==================')
#                                mask = np.zeros([7,3])
#                                modJary_norm = (modJary-MIN)/(MAX-MIN)                        
#                                reconJ       = (GPR.gp_pred(modJary_norm, gp)*(MAX-MIN)+MIN)  # reconJ is 1*21 array
#                                unrelidx = np.where(Relary[limbidx]<0.6)[0]   # limbidx = [4,5,6,8,9,10,20]
#    
#                                mask[unrelidx,:] = np.array([1,1,1])
##                                if np.sum(np.isnan(reconJ))==21:
##                                    pdb.set_trace()
##                                    _,_ = Hmod.human_mod_pts2(joints,True)
##                                    skel.draw_body(joints, Jps, SKELETON_COLORS[i],self._frame_surface,15)
#                                modJary[:,mask.flatten()==1] = reconJ[:,mask.flatten()==1]
#                                reconJ =   modJary                          
#                                # use unrelidx and reconJ to replace unreliable joints in modJary 
#
#                                #  === GPR recon ===
#
#                                JJ = Hmod.reconJ2joints(rec_joints,reconJ.reshape(7,3))
#                                for ii in [4,5,6,8,9,10]:
#                                    rec_joints[ii].Position.x = JJ[i][0]
#                                    rec_joints[ii].Position.y = JJ[i][1]
#                                    rec_joints[ii].Position.z = JJ[i][2]
# 
#                                tmp_Jps    = self._kinect.body_joints_to_color_space(rec_joints) #joint points in color domain
#                                rec_Jps    = Jps
#                                for ii in unrelidx:
#                                    rec_Jps[ii].x = tmp_Jps[ii].x
#                                    rec_Jps[ii].y = tmp_Jps[ii].y
#                                skel.draw_body(rec_joints, rec_Jps, SKELETON_COLORS[-1],self._frame_surface,15)                            
                            
                            # === DTW matching ===

                            self.Dtw.update(DTW_matching(self.Dtw,reconJ,gt_data))

                            if self.Dtw['idxlist'].count(4) <4:
                                typetext(self._frame_surface,Sstr[self.Dtw['oidx']],(100,10),fontsize=100,bold=True) 
                            elif self.Dtw['oidx']!=4:
#                                print('oidx is %r' %self.Dtw['oidx'])
#                                print('gt_idx is      %r' %self.Dtw['gt_idx'])                                
                                typetext(self._frame_surface,Sstr[self.Dtw['oidx']],(100,10),fontsize=100,bold=True)
                            else:    
                                typetext(self._frame_surface,Sstr[5],(100,10),(255,0,0),fontsize=100,bold=True)
  
                            if self.Dtw['evalstr'] != '':
                                typetext(self._frame_surface,self.Dtw['evalstr'],(100,300),(255,0,0),fontsize=100)
                                self.Dtw['fcnt'] += 1
                                if self.Dtw['fcnt'] >40:
                                    self.Dtw['evalstr'] = ''
                                    self.Dtw['fcnt']  = 0
                            
                            if (body.hand_left_state == 2)| (body.hand_left_state == 0): #Lhand open
                                Lhstatus = 'open'
                            elif body.hand_left_state ==3:
                                Lhstatus = 'closed'
                            elif body.hand_left_state == 4:
                                Lhstatus = 'Lasso'
                            else:
                                Lhstatus = 'Not be detected'                            

                            if (body.hand_right_state == 2)| (body.hand_right_state == 0): #Lhand open
                                Rhstatus = 'open'
                            elif body.hand_right_state ==3:
                                Rhstatus = 'closed'
                            elif body.hand_right_state == 4:
                                Rhstatus = 'Lasso'
                            else:
                                Rhstatus = 'Not be detected'
                            
                            typetext(self._frame_surface,'Lhand : '+Lhstatus ,(100,800),(200,200,255),fontsize=60,bold=True)        
                            typetext(self._frame_surface,'Rhand : '+Rhstatus ,(100,900),(200,200,255),fontsize=60,bold=True) 
                                
                    #draw unify human model
                    if self.model_draw:
                        modJoints = Hmod.human_mod_pts(joints)

                        if not self.model_frame :
                            fig = plt.figure() 
                            ax = fig.add_subplot(111, projection='3d')
                            keys = modJoints.keys()
                            self.model_frame = True
                        else:
                            plt.cla()
                        
                        Hmod.draw_human_mod_pts(modJoints,ax,keys)
                    
                    bddic['timestamp'] = TimeS
                    bddic['jointspts'] = Jps   # joint coordinate in color space (2D) 
                    bddic['depth_jointspts'] = dJps
                    bddic['joints'] = Jdic     # joint coordinate in camera space (3D)                   
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
                self.bdjoints.append(bddic)
            else:
                typetext(self._frame_surface,'Not Recording' ,(1550,20),(0,255,0))
            

                
                
                    
                    
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())    
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
            
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()
            

            # --- Limit frames per second
            self._clock.tick(fps)
    
        # Close our Kinect sensor, close the window and quit.
            #print time.clock()-ST
               
            
        self._kinect.close()
        
        print self.Dtw['idxlist']
        
        if self.bdjoints !=[]:
           cPickle.dump(self.bdjoints,file(self.dstr+'.pkl','wb')) 
        try:
            self.dataset.close()
        except:
            pass
        

__main__ = "Kinect v2 Body Game"

game = BodyGameRuntime();
game.run();

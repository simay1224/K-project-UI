# -*- coding: utf-8 -*-
import ctypes, os, datetime, glob
import pygame, sys, copy
import win32gui, win32con
import imageio

if sys.platform == "win32":
    import h5py
    from .pykinect2 import PyKinectV2
    from .pykinect2.PyKinectV2 import *
    from .pykinect2 import PyKinectRuntime

# https://askubuntu.com/questions/742782/how-to-install-cpickle-on-python-3-4
if sys.version_info >= (3, 0):
    import _pickle as cPickle
else:
    import cPickle

import pdb, time, cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.externals import joblib
from collections import defaultdict

# import class
from ..klib import movie
from .initial_param.kparam      import Kparam
# from dtw         import Dtw
from .analysis    import Analysis
from .evaluation  import Evaluation
from .denoise     import Denoise
from .rel         import Rel
from .dataoutput  import Dataoutput
from .human_model import Human_model
from .skeleton    import Skeleton
from .fextract    import Finger_extract
from .instruction import Exeinst
from .historylog  import Historylog
from .analysis_helper.handstatus  import Hand_status

fps = 30 #was originally 30
limbidx = np.array([4, 5, 6, 8, 9, 10, 20])
x_screen = 0
y_screen = 0
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x_screen,y_screen)

class BodyGameRuntime(object):

    def __init__(self, info, exe_num=3, if_recording=False):
        print("$"*50)
        pygame.init()
        print('py game is INITIALIZED!')
        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()
        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        # self.width = self._infoObject.current_w
        # self.height = self._infoObject.current_h
        self.width = 1920
        self.height = 1080
        # print(self.width, self.height)
        #self._screen = pygame.display.set_mode((self.width, self.height),  pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32) #ORIGINAL ONE
        #non-orginal set up:
        #self._screen = pygame.display.set_mode((0,0), pygame.NOFRAME , 32)
        self._screen = pygame.display.set_mode((0, 0),  pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32) 
        
        #self._screen = pygame.display.set_mode((0,0),  pygame.FULLSCREEN, 32)
        
        #self._screen = pygame.display.set_mode((self.width, self.height),  pygame.HWSURFACE | pygame.DOUBLEBUF  | pygame.RESIZABLE, 32)
        #background color:
        self.background_color = (230,230,230)
        #self._screen.fill(self.background_color)

        self._frame_surface = pygame.Surface((self.width, self.height), 0, 32).convert()  # kinect surface
        self.bk_frame_surface = pygame.Surface((self.width, self.height), 0, 32).convert()  #background surface
        self.bklist = glob.glob(os.path.join('./data/imgs/bkimgs', '*.jpg'))
        self.h_to_w = float(self.height) / self.width
        # here we will store skeleton data
        self._bodies = None
        # User information
        self.info = info
        # Emoji
        self.errimg = pygame.image.load("./data/imgs/emoji/err2.png").convert_alpha()
        self.corimg = pygame.image.load("./data/imgs/emoji/right2.png").convert_alpha()
        self.wellimg = pygame.image.load("./data/imgs/emoji/excellent.png").convert_alpha()
        # time.sleep(5)
        pygame.display.set_caption("LymphCoach")
        try :
            pygame.display.set_icon(pygame.image.load('./data/imgs/others/logo.png'))
        except:
            pass

        self.exeno = exe_num  # exercise number
        self.init_param()

        if self.kp.kinect:
            # kinect runtime object, we want only color and body frames
            self._kinect = PyKinectRuntime.PyKinectRuntime\
                           (PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body |
                            PyKinectV2.FrameSourceTypes_Depth | PyKinectV2.FrameSourceTypes_BodyIndex)
            # Extract bk image of scene
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame().reshape([self.height, self.width, 4])[:, :, :3] # can be None
                if frame is not None:
                    bkimg = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                print ('Extract bg .....')
            else:
                print ('Failed to extract .....')

            self.bkidx = 10
        else:
            self.bkidx = 11

        self.readbackground()
        print('background read')
        self.if_recording = if_recording
        
        #data flow boolean to control data flow. controlled by buttons
        #self.data_flow= False
        self.exercise_initialized = False
        self.paused = False
        self.stopped = False
        self.exercise_start_wait = 0 

        #true when pressed escape 
        self.escaped = False
        print 'finished initalizing'



    # Read global background
    def readbackground(self):
        self.bkimg = cv2.imread(self.bklist[self.bkidx])
        self.bkimg = cv2.resize(self.bkimg, (self.width, self.height))

        if sys.platform == "win32":
            # self.bkimg = np.dstack([cv2.resize(self.bkimg, (self.width, self.height)), np.zeros([self.height, self.width])]).astype(np.uint8)
            self.bkimg = np.dstack([self.bkimg, 255 * np.ones([self.height, self.width])]).astype(np.uint8)
        else:
            self.bkimg = np.dstack([255 * np.ones([self.height, self.width]), self.bkimg[:, :, ::-1]]).astype(np.uint8)

    def init_param(self, clean=False):
        try:
            self.dataset.close()
            print('Save h5py ....')
            if clean:
                os.remove(self.kp.dstr+'.h5')
                print('Remove h5py ....')
        except:
            pass

        self.joints_name = [PyKinectV2.JointType_Head,
                            PyKinectV2.JointType_Neck,
                            PyKinectV2.JointType_SpineShoulder,
                            PyKinectV2.JointType_SpineMid,
                            PyKinectV2.JointType_SpineBase,
                            PyKinectV2.JointType_ShoulderRight,
                            PyKinectV2.JointType_ElbowRight,
                            PyKinectV2.JointType_WristRight,
                            PyKinectV2.JointType_ShoulderLeft,
                            PyKinectV2.JointType_ElbowLeft,
                            PyKinectV2.JointType_WristLeft,
                            PyKinectV2.JointType_HipRight,
                            PyKinectV2.JointType_HipLeft
                            ]
                            
        self.fig = None
        # Predefined param
        self.kp = Kparam(self.exeno, self.info.name)

        # Avator with exeno
        #skip the 5th movie, whuc==ich is reach to the sky
        if self.exeno ==5:
            movie_no =6
        elif self.exeno == 6:
            movie_no =7
        else:
            movie_no = self.exeno

        if self.kp.kinect:
            #self.movie = movie.Movie(self.exeno)
            self.movie = movie.Movie(movie_no)
        else:
            #self.movie = movie.Movie(self.exeno, self.kp.vid_w, self.kp.vid_h)
            self.movie = movie.Movie(movie_no, self.kp.vid_w, self.kp.vid_h)

        self.kp.scale = self.movie.ini_resize(self._infoObject.current_w, self._infoObject.current_h, self.kp.ratio)
        self.kp.ini_scale = self.kp.scale

        # scene type
        if self.kp.scene_type == 2:
            self.ori = (int(self._screen.get_width()*self.kp.video_LB/1920.), int(self._screen.get_height()*self.kp.video2_UB/1080.))
        else:
            self.ori = (int(self._screen.get_width()*self.kp.video_LB/1920.), int(self._screen.get_height()*self.kp.video1_UB/1080.))

        # count for process finish analysis
        #self.pa_count = 0
        # Frame count
        self.fcnt = 0
        # error message for patient
        self.errsums = ''
        self.evalhis = []  # evaluaton history
        # Interval between different ex
        self.cntdown = 900
        # import class
        self.ana = Analysis()
        self.eval = Evaluation()
        # self.denoise = Denoise()
        self.rel = Rel()
        self.io  = Dataoutput() # output text
        self.h_mod = Human_model()
        self.skel = Skeleton()
        self.fextr = Finger_extract()
        self.exeinst = Exeinst() # exercise intruction
        self.log = Historylog()

        #self._bodies =None

    def reset(self, clean=False):
        if self.kp.kinect:
            self.movie.stop(True)
            del self.movie
        #self._bodies = None
        self.init_param(clean)

    def press_event(self, press):
        """ According to the button which is pressed by the user
            doing correspond action
        """
        if press[pygame.K_ESCAPE]:
            self.kp._done = True
            print('inside escape')
            print(self.kp._done)
            if self.kp.kinect:
                self.movie.stop()
            self.escaped = True
            pygame.quit()


        if press[pygame.K_q]:  # to stop the movie
            self.ana._done =True
            #self.kp._done = True
            #if self.kp.kinect:
            #    self.movie.stop()
            #pygame.quit()

        if press[pygame.K_s]:  # to finish the exercise
            self.kp._done = True
            self.exercise_initialized = False
            #if self.kp.kinect:
            #    self.movie.stop()

        if press[pygame.K_w]:  # to pause the movie
            #self.kp._done = True
            if self.kp.kinect:
                self.movie.pause()


        if press[pygame.K_a]:  # to play the movie
            #self.kp._done = True
            if self.kp.kinect:
                self.movie.play()


        if press[pygame.K_h]:  # use 'h' to open, 'ctrl+h' to close finger detection
            if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
                print('Finger detection disable .....')
                self.kp.handmode = False
            else:
                print('Finger detection enable .....')
                self.kp.handmode = True

        # if press[pygame.K_m]:  # use 'm' to open, 'ctrl+m' to close human model
        #     if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
        #         print('Human model disable .....')
        #         plt.close(self.fig)
        #         self.kp.model_draw = False
        #         self.kp.model_frame = False
        #     else:
        #         print('Human model enable .....')
        #         self.kp.model_draw = True''

        if press[pygame.K_r]:  # use 'r' to start video recording
            print('starting to record')
            if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
                print('Stop recording .....')
                self.kp.vid_rcd = False
            else:
                if self.kp.clipNo == 0:
                    self.dataset = h5py.File(self.kp.dstr+'.h5', 'w')
                    self.dataset = h5py.File(self.kp.dstr+'.h5', 'r')
                    # img group
                    self.imgs = self.dataset.create_group('imgs')
                    self.color_joints = self.dataset.create_group('color_joints')
                    self.depth_joints = self.dataset.create_group('depth_joints')
                    self.cimgs = self.imgs.create_group('cimgs')
                    self.dimgs = self.imgs.create_group('dimgs')
                    self.bdimgs = self.imgs.create_group('bdimgs')
                print('recording .....')
                self.kp.vid_rcd = True
                self.kp.clipNo += 1

        # Denoising for skeleton detection of kinect
        if press[pygame.K_g]:  # use 'g' to to open gpr denoise, 'ctrl+g' to close gpr denoise
            if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
                print('Close denoising process .....')
                self.denoise._done = True
            else:
                print('Start denoising process .....')
                self.denoise._done = False

        # dynamic time warping eval (original for ex3 and 4)
        if press[pygame.K_d]:  # use 'd' to to open, 'ctrl+d' to close dtw
            if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
                print('Disable human behavior analyze .....')
                # self.ana._done: if true: display the exercise list
                self.ana._done = True
                self.kp.finish = True
            else:
                print('Enable human behavior analyze .....')
                self.ana._done = False
                self.kp.finish = False

        if press[pygame.K_i]:  # use 'i' to reset every parameter
            print('Reseting ............................')
            self.reset()
        if press[pygame.K_u]:  # use 'u' to reset every parameter and remove the save data
            print('Reseting & removing the saved file ................')
            self.reset(True)

        # if press[pygame.K_b]:  # use 'b' to lager the scale
        #     self.kp.scale = min(self.kp.scale*1.1, self.kp.ini_scale*1.8)
        # if press[pygame.K_s]:  # use 's' to smaller the scale
        #     self.kp.scale = max(self.kp.scale/1.1, 1)

        #if press[pygame.K_w]: # use 'w' to change background image
        #    self.bkidx += 1
        #    if self.bkidx >= len(self.bklist):
        #        self.bkidx -= len(self.bklist)
        #    self.readbackground()

        if press[pygame.K_z]:  # use 'z' to lower the ratio of avatar to color frame
                               # 'ctrl+z' to larger the ratio of avatar to color frame
            if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
                if self.kp.ratio <= 0.6:
                    self.kp.ratio += 0.05
                    if self.kp.kinect:
                        self.kp.scale = self.movie.ini_resize(self._screen.get_width(), self._screen.get_height(), self.kp.ratio)
            else:
                if self.kp.ratio > 0.4:
                    self.kp.ratio -= 0.05
                    if self.kp.kinect:
                        self.kp.scale = self.movie.ini_resize(self._screen.get_width(), self._screen.get_height(), self.kp.ratio)

        # Switch avator and kinect
        if press[pygame.K_0]:  # use '0' to change the scene type
            self.exercise_initialized = False
            print('scene change')
            if self.kp.scene_type == 2:
               self.kp.scene_type = 1
            else:
               self.kp.scene_type += 1

        if press[pygame.K_1]:  # use '1' to change to execise 1
            self.exercise_initialized = False
            self.exeno = 1
            print('====  Doing exercise 1 ====')
            self.reset()
        if press[pygame.K_2]:  # use '2' to change to execise 2
            self.exercise_initialized = False
            self.exeno = 2
            print('====  Doing exercise 2 ====')
            self.reset()
        if press[pygame.K_3]:  # use '3' to change to execise 3
            self.exercise_initialized = False
            self.exeno = 3
            print('====  Doing exercise 3 ====')
            self.reset()
        if press[pygame.K_4]:  # use '4' to change to execise 4
            self.exercise_initialized = False
            self.exeno = 4
            print('====  Doing exercise 4 ====')
            self.reset()
        if press[pygame.K_5]:  # use '5' to change to execise 5
            #we are skipping 5 so exeno =5 would go to exercise 6 in the backend
            self.exercise_initialized = False
            self.exeno = 5

            print('====  Doing exercise 5 ====')
            self.reset()
        if press[pygame.K_6]:  # use '6' to change to execise 6
            self.exercise_initialized = False
            self.exeno = 6
            print('====  Doing exercise 6 ====')
            self.reset()

        #if press[pygame.K_7]:  # use '7' to change to execise 7
         #   self.exeno = 7
          #  print('====  Doing exercise 7 ====')
           # self.reset()

        if press[pygame.K_SPACE]:
            self.exercise_initialized = False
            #if self.exeno == 7:
            if self.exeno == 6:
                self.exeno = 1
            
            else:
                self.exeno += 1
            print('Next exercise ..................')
            self.reset()

        if press[pygame.K_p]:
            pdb.set_trace()

    # ############### run() ############### #


    # ############### separate methods for run() ############### #

    def process_pygame(self, wait_key_cnt):
        # === key pressing ===
        if(wait_key_cnt[0] < 3):
            wait_key_cnt[0] += 1
        if(pygame.key.get_focused() and wait_key_cnt[0] >= 3):
            press = pygame.key.get_pressed()
            #print('press:', press)
            self.press_event(press)
            wait_key_cnt[0] = 0
        if not self.escaped or True:
            # === Main event loop ===
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    self.kp._done = True  # Flag that we are done so we exit this loop
                    if self.kp.kinect:
                        print("is problem here")
                        self.movie.stop()
                        print("no")
                    self.exercise_initialized = False
                    pygame.quit()
                    #exit()
                    
                elif event.type == pygame.VIDEORESIZE:  # window resized
                    print('&^&^&'*200)
                    print("\n\n\nevent.type == pygame.VIDEORESIZE")
                    #self._screen = pygame.display.set_mode((0,0),  pygame.FULLSCREEN, 32)
                    self._screen = pygame.display.set_mode(event.dict['size'],pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
                    #self._screen = pygame.display.set_mode(event.dict['size'],
                    #               pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x = pygame.mouse.get_pos()[0]
                    mouse_y  = pygame.mouse.get_pos()[1]
                    #button 1 pressed
                    print("%"*50)
                    print('\n', mouse_x , mouse_y)
                    ideal_left_button1  = 900
                    ideal_right_button1  = ideal_left_button1 + 200 
                    ideal_left_button2  = ideal_right_button1 + 10
                    ideal_right_button2 = ideal_left_button2 + 200
                    ideal_left_button3  = ideal_right_button2 + 10
                    ideal_right_button3 = ideal_left_button3 + 200

                    ideal_button_top = 40
                    ideal_button_bottom = 80

                    #button functionalities
                    if not  self.ana._done:
                        if self.exercise_initialized: #exercise already started, function pause and stop only
                            if mouse_x >= ideal_left_button2 and mouse_x <= ideal_right_button2 :
                                if mouse_y >= ideal_button_top  and mouse_y <= ideal_button_bottom:
                                    #PAUSE/CONTINUE BUTTON FUNCTIONALITY
                                    if not self.paused:
                                        self.paused = True
                                        self.ana.paused = True
                                    else:
                                        self.paused= False
                                        self.ana.paused = False
                                    self.movie.pause()
                        
                            elif mouse_x >= ideal_left_button3 and mouse_x <= ideal_right_button3:
                                if mouse_y >= ideal_button_top  and mouse_y <= ideal_button_bottom:
                                    #STOP BUTTON FUNCTIONALITY
                                    #self.data_flow= False
                                    self.stopped = True
                                    self.movie.stop()
                                    self.ana._done =True
                                    #self.movie.stop()


                        else: #the exercise did not start yet, function start only
                            #START BUTTON FUNCTIONALITY
                            if mouse_x >= ideal_left_button1  and mouse_x <= ideal_right_button1:
                                if mouse_y >= ideal_button_top  and mouse_y <= ideal_button_bottom:
                                    #self.data_flow= True
                                    self.ana.exercise_initialized = True
                                    self.exercise_initialized = True
                                    self.movie.play()

                            '''
                    if mouse_x >= ideal_left_button1  and mouse_x <= ideal_right_button1:
                        if mouse_y >= ideal_button_top  and mouse_y <= ideal_button_bottom:
                            #self.data_flow= True
                            self.exercise_initialized = True
                            self.movie.play()
                            
                    elif mouse_x >= ideal_left_button2 and mouse_x <= ideal_right_button2 :
                        if mouse_y >= ideal_button_top  and mouse_y <= ideal_button_bottom:
                            self.movie.pause()
                    
                    elif mouse_x >= ideal_left_button3 and mouse_x <= ideal_right_button3:
                        if mouse_y >= ideal_button_top  and mouse_y <= ideal_button_bottom:
                            #self.data_flow= False
                            self.movie.stop()
                            self.ana._done =True
                            #self.movie.stop()
                            '''
                    
                    
                    

    def find_closest_id(self):
        closest_ID = -1
        cdist = np.inf
        for i in range(0, self._kinect.max_body_count):
            body = self._bodies.bodies[i]
            if not body.is_tracked:
                continue
            if body.joints[20].Position.z <= cdist:  # find the closest body
                closest_ID = i
                cdist = body.joints[20].Position.z
        return closest_ID

    def draw_human_model(self, joints):
        # === draw unify human model ===
        if self.kp.model_draw:
            modJoints = self.h_mod.human_mod_pts(joints, limb=False)
            if not self.kp.model_frame:
                self.fig = plt.figure(1)
                ax = self.fig.add_subplot(111, projection='3d')
                self.kp.model_frame = True
            else:
                plt.cla()
            self.h_mod.draw_human_mod_pts(modJoints, ax)

    def save_data(self, bddic, timestamp, jps, djps, jdic, Rel, body):
        # === save data ===
        bddic['timestamp'] = timestamp
        bddic['jointspts'] = jps   # joints' coordinate in color space (2D)
        bddic['depth_jointspts'] = djps  # joints' coordinate in depth space (2D)
        bddic['joints'] = jdic  # joints' coordinate in camera space (3D)
        bddic['vidclip'] = self.kp.clipNo
        bddic['Rel'] = Rel
        bddic['LHS'] = body.hand_left_state
        bddic['RHS'] = body.hand_right_state

    def process_analysis(self):
        print("\n\nprocess analysis:")
        print(self.ana.evalstr)
        #print('@@@@@@@@@@@@@@@'*25)
        print(self.ana.dtw.idxlist)
        #print('----------------'*25)
        #if self.ana.evalstr != '':########!!!!!!!!!!!!
        #print("shld ongoing cycle:", self.ana.shld.ongoing_cycle)
        print("ana ongoing cycle:", self.ana.ongoing_cycle)
        if self.ana.ongoing_cycle == False : # was if self.ana.shld.ongoing_cycle == False or
            if 'well' in (self.ana.evalstr).lower(): #if well exists in immediate feedback
                print("does it say well done?")
                
                self.ana.screen_message = self.ana.evalstr
                print("here screen message is",self.ana.screen_message )
                self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,  self.ana.screen_message, 3, color=self.kp.c_eval_well)
                if len(self.evalhis) < min(self.ana.repcnt, 4):
                    self.evalhis.append(True)
                      
            else:
                print("no it does not")
                self.ana.screen_message = self.ana.evalstr
                print("here screen message is",self.ana.screen_message )
                self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp, self.ana.screen_message, 3, color=self.kp.c_eval_err)
                if len(self.evalhis) < min(self.ana.repcnt, 4):
                    self.evalhis.append(False)

            self.ana.ongoing_cycle = True
            #self.ana.screen_message = ''
            self.fcnt  = 0
            self.ana.evalstr = ''

            if self.exeno == 5:
                self.ana.shld.ongoing_cycle = True

        else:
            print("we are in the cycle")
            #then display the screen message for 2 seconds
            if  self.ana.screen_message == '':
                self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp, None, 3, color=self.kp.c_eval_err)
            else:
                self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp, self.ana.screen_message, 3, color=self.kp.c_eval_err)
        print(self.ana.repcnt)
        print(self.evalhis)
        self.ana.ongoing_cycle = True  #just added this, lets cee

    def process_finish_analysis(self):
        print('process finish analaysis called')
        if not self.kp.finish:
            errs = [self.ana.brth.err, self.ana.hs.err, self.ana.horzp.err, self.ana.pushdp.err,\
                    self.ana.shld.err, self.ana.clsp.err, self.ana.swing.err]  # append err msg here
            self.errsums = '\n- '.join(set(self.ana.brth.errsum+self.ana.hs.errsum+self.ana.horzp.errsum +\
                            self.ana.pushdp.errsum+self.ana.shld.errsum+self.ana.clsp.errsum +\
                            self.ana.swing.errsum))
            dolist = [self.ana.brth.do, self.ana.hs.do, self.ana.horzp.do, self.ana.pushdp.do,\
                      self.ana.shld.do, self.ana.clsp.do, self.ana.swing.do]
            print("in process finish analysis. lets run eval ")
            exelog = self.eval.run(self.exeno, self.ana)
            print("after running eval ")

            self.eval.errmsg(errs, dolist)
            self.eval.cmphist(self.log, self.info, self.exeno, self.kp.now, exelog)
            self.log.writein(self.info, self.exeno, self.kp.now, exelog, errs)
            print('@@@@@@@@@@@@@@@'*50)
            print(self.ana.dtw.idxlist)
            print('----------------'*50)
            self.kp.finish = True
            while len(self.evalhis) < 4:
                print("\nevalhis appended false \n")
                self.evalhis.append(False)

        self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp, \
                            'Exercise ' + str(self.exeno) + ' is done', 2)
        if self.errsums == '':
            self.ana.screen_message = ''
            if len(self.evalhis) != 0:
                if self.ana.exercise_started:
                    if self.ana.repcnt>= 4:
                        self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                                    'Overall evaluation:\nPerfect !!', 3, color=self.kp.c_togo, fsize=80) #font size is 80
                    
                    #elif self.ana.repcnt >  4:
                    #    self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                    #                'Overall evaluation:\nOnly need to do 4 repetitions.', 3, color=self.kp.c_togo, fsize=70) #font size is 80
                    
                    elif self.ana.repcnt < 4:
                        self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                                    'Make sure you do 4 repetitions.', 3, color=self.kp.c_togo, fsize=70) #font size is 80
                else:
                    self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                                    'Overall evaluation:\nNo repetition done', 3, color=self.kp.c_togo, fsize=70) #font size is 80
        else:
            self.ana.screen_message = ''
            self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                                'Overall evaluation:\n- '+self.errsums, 3, color=self.kp.c_togo, fsize=70) # font size was 80

# the main menu after each exercise
        self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                            'Next exercise will start in %s seconds.' % str(self.cntdown/30), 0, (120, 800) ,color=self.kp.c_guide, fsize=50) # the color was color=self.kp.c_togo
        self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                            'Or press "Space" to start next exercise \nOr press ESC to Quit.', 0, (120, 840),color=self.kp.c_guide, fsize=50) # the color was color=self.kp.c_togo

        self.cntdown -= 1
        if self.cntdown == 0:
            if self.exeno == 6:
                self.exeno = 1

            else:
                self.exeno += 1
            print('Next exercise ..................')
            self.exercise_initialized = False
            self.reset()


    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()

        if self.kp.kinect:
            address = self._kinect.surface_as_array(target_surface.get_buffer())
            ctypes.memmove(address, frame.ctypes.data, frame.size)
            del address
        else:
            address = target_surface._pixels_address
            ctypes.memmove(address, frame.ctypes.data, frame.size)

        target_surface.unlock()

    #def text_objects(self, text, color):
    #    smallfont = pygame.font.SysFont(self.kp.s_normal, self.kp.inst_size)
    #    textSurface = smallfont.render(text, True, color)
    #    return textSurface, textSurface.get_rect()

    #draws text to button
    def text_to_button(self, msg, buttonx, buttony, buttonwidth, buttonheight, size = "small"):
        color = (240, 240, 240) # text color= (240, 240, 240)
        text_font = pygame.font.SysFont(self.kp.s_normal, self.kp.inst_size) #self.kp.inst_size
        textSurface = text_font.render(msg, True, color)
        textRect = textSurface.get_rect()
        #textSurf, textRect = self.text_objects(msg,color)
        textRect.center = ((buttonx+(buttonwidth/2)), buttony+(buttonheight/2))
        #print("center is", textRect.center)
        self.bk_frame_surface.blit(textSurface, textRect) #_screen

    def run(self):
        print 'def run'
        # Removing key jitter
        wait_key_cnt = [3]

        # s = pygame.image.tostring(self._screen, 'RGB')
        #self._bodies  =None
        while not self.kp._done:
            print 'p'
            self.process_pygame(wait_key_cnt)
            print 'r'
            #if not self.escaped:
            self.run_body_game()
            print (self.kp._done)

        print(" "*10, "DONE"*100)
        print(self.kp._done)
        # end of the system
        #if not self.escaped:
        if self.kp.kinect:
            self.movie.stop(True)   # close avatar
            self._kinect.close()    # close kinect sensor
        # print(self.dtw.idxlist)  # show the analyzed result
        # save the recording data
        if self.kp.bdjoints != []:
            cPickle.dump(self.kp.bdjoints, file(self.kp.dstr+'.pkl', 'wb'))
        try:
            self.dataset.close()
        except:
            pass
        #self.data_flow =False
        #self._bodies  =None
        print('pygame quit?')
        pygame.quit()  # quit
        print('yes')


    def run_body_game(self):
        bddic = {}
        jdic = {}
        timestamp = 0

        # initialize background frame
        self.draw_color_frame(self.bkimg, self.bk_frame_surface)

        if self.kp.kinect: 
            # was if self.kp.kinect:
            # self.bk_frame_surface.fill(255,50,50)
            # === extract data from kinect ===
            if self._kinect.has_new_color_frame():
                print 'Got new frame!'
                frame = self._kinect.get_last_color_frame() #can be None
                #! change
                if frame is not None:
                    self.draw_color_frame(frame, self._frame_surface)
                    frame = frame.reshape(self.height, self.width, 4)[:, :, :3]
            if self._kinect.has_new_body_frame():
                self._bodies = self._kinect.get_last_body_frame() # can be None
                timestamp = datetime.datetime.now()
            if self._kinect.has_new_body_index_frame():
                bodyidx = self._kinect.get_last_body_index_frame() # can be None
                #! change
                if bodyidx is not None:
                    bodyidx = bodyidx.reshape((424, 512))
            if self._kinect.has_new_depth_frame():
                dframe, oridframe = self._kinect.get_last_depth_frame() # can be None
                #! changed
                if dframe is not None:
                    dframe = dframe.reshape((424, 512))

            # === when user is detected ===
            print('-'*10)
            #print('self bodies is None:')
            #print(self._bodies is None)
            if self._bodies is not None:
                closest_ID = self.find_closest_id()

                if (closest_ID != -1):
                    body = self._bodies.bodies[closest_ID]
                    joints = body.joints
                    for ii in xrange(25):
                        jdic[ii] = joints[ii]
                    jps = self._kinect.body_joints_to_color_space(joints)  # joint points in color domain
                    djps = self._kinect.body_joints_to_depth_space(joints)  # joint points in depth domain
                    # pdb.set_trace()
                    # === fingers detection ===
                    if self.kp.handmode and frame is not None:  # finger detect and draw
                    #! added frame is not none here
                        self.fextr.run(frame, bkimg, body, bddic, jps, pygame.color.THECOLORS["yellow"], self._frame_surface)

                    # === joint reliability ===
                    Rel, Relary = self.rel.run(jdic)
                    # # joint's reliability visulization
                    # self.skel.draw_Rel_joints(jps, Rel, self._frame_surface)

                    # === dtw analyze & denoising process ===
                    if not self.ana._done and self.exercise_initialized and not self.ana.paused:
                        # Modified joint array (change struture from pykinect to np)
                        modJary = self.h_mod.human_mod_pts(joints, False)  # modJary is 11*3 array
                        modJary = modJary.flatten().reshape(-1, 33)  # change shape to 1*33 array

                        reconJ = modJary  # uncomment it when disable the denosing process
                        # if not self.denoise._done:
                        #     rec_joints = body.joints
                        #     if len(Relary) != 0:  # len =0 if first frame
                        #         # === GPR denoising ===
                        #         if all(ii > 0.6 for ii in Relary[limbidx]):  # all joints are reliable
                        #             reconJ = modJary  # reconJ is 1*21 array
                        #         else:  # contains unreliable joints
                        #             reconJ, unrelidx = self.denoise.run(modJary[:, 12:], Relary, self.exeno)
                        #             # draw reconstruction skeleton
                        #             JJ = self.h_mod.reconj2joints(rec_joints, reconJ.reshape(7, 3))
                        #             reconJ = np.hstack([modJary[:, :12], reconJ])
                        #             #  === recon 2D joints in color domain ===
                        #             for ii in [4, 5, 6, 8, 9, 10, 20]:
                        #                 rec_joints[ii].Position.x = JJ[ii][0]
                        #                 rec_joints[ii].Position.y = JJ[ii][1]
                        #                 rec_joints[ii].Position.z = JJ[ii][2]
                        #             tmp_jps = self._kinect.body_joints_to_color_space(rec_joints)  # joints in color domain
                        #             rec_jps = np.zeros([21,2])
                        #             for ii in xrange(21):
                        #                 if ii in unrelidx:
                        #                     rec_jps[ii, 0] = tmp_jps[ii].x
                        #                     rec_jps[ii, 1] = tmp_jps[ii].y
                        #                 else:
                        #                     rec_jps[ii, 0] = jps[ii].x
                        #                     rec_jps[ii, 1] = jps[ii].y
                        #             self.skel.draw_body(rec_joints, rec_jps, SKELETON_COLORS[3], self._frame_surface, 30)
                        #     else:
                        #         reconJ = modJary
                        # else:
                        #     reconJ = modJary

                        # === analyze ===
                        #! change
                        #if dframe is None:
                        #    self.ana.run(self.exeno, reconJ[0], self.bk_frame_surface,\
                        #             self.eval, self.kp, body, [], djps)
                        #else:
                        self.ana.run(self.exeno, reconJ[0], self.bk_frame_surface,\
                                     self.eval, self.kp, body, dframe, djps)

                        # === show hand status ===
                        # self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                        #                     self.ana.hs.htext(body.hand_left_state, body.hand_right_state), 4 ,\
                        #                     (255, 130, 45, 255))

                        #if self.ana.evalstr != '':
                            # How long the evaluation show up
                        #    self.fcnt += 1
                        #    if self.fcnt > 60: # was 60
                        #        self.ana.evalstr = ''
                        #        self.fcnt  = 0
                        
                        print("screen message is")
                        print(self.ana.screen_message)

                        #determine the duration that screen message will be on screen
                        if self.exeno ==6 or self.exeno ==4: 
                            screen_duration = 120
                        else:
                            screen_duration = 90


                        if self.ana.screen_message != '':
                            self.fcnt += 1
                            if self.fcnt > screen_duration : # was 60
                                self.ana.screen_message = ''
                                self.fcnt  = 0
                        #elif not self.ana.ongoing_cycle:
                        #    self.ana.screen_message = ''
                        #    self.fcnt  = 0


                    # draw skel
                    self.skel.draw_body(joints, jps, pygame.color.THECOLORS["yellow"], self._frame_surface, 8)
                    # self.draw_human_model(joints) # ZP thinks it is useless
                    self.save_data(bddic, timestamp, jps, djps, jdic, Rel, body)

                self.kp.framecnt += 1  # frame no
            else:
                self.io.typetext(self._frame_surface, 'kinect does not connect!!---', (20, 100))

        # if self.kp.kinect == False:
        else:
            if not self.ana._done and self.exercise_initialized and not self.ana.paused:
                # === analyze ===
                # reconJ, body, dframe, djps: all from kinect
                self.ana.run(self.exeno, None, self.bk_frame_surface, self.eval, self.kp, None, None, None)
            self.kp.framecnt += 1  # frame no
            self.io.typetext(self._frame_surface, 'kinect does not connect!! !!', (20, 100))

        # draw text
        self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                                        self.exeinst.str['name'][self.exeno], 1)# 1 is location

        #draw buttons
        if not self.ana._done:
            if self.exercise_initialized: #exercise alread started, display pause and stop only
                #button1 = start
                #pygame.draw.rect(self.bk_frame_surface , self.kp.c_button_play  , pygame.Rect(self.kp.button_left1, self.kp.button_top, self.kp.button_w , self.kp.button_h ))     
                #button2 = pause
                pygame.draw.rect(self.bk_frame_surface , self.kp.c_button_pause , pygame.Rect(self.kp.button_left2, self.kp.button_top, self.kp.button_w  , self.kp.button_h) )
                #button3 = stop
                pygame.draw.rect(self.bk_frame_surface , self.kp.c_button_stop  , pygame.Rect(self.kp.button_left3  , self.kp.button_top, self.kp.button_w  , self.kp.button_h) )
            
                #draw text on buttons
                #self.text_to_button("start", self.kp.button_left1, self.kp.button_top, self.kp.button_w , self.kp.button_h ) #900, 40
                if self.paused:
                    self.text_to_button("continue",  self.kp.button_left2, self.kp.button_top, self.kp.button_w  , self.kp.button_h) #1110, 40
                else:
                    self.text_to_button("pause",  self.kp.button_left2, self.kp.button_top, self.kp.button_w  , self.kp.button_h) #1110, 40
                self.text_to_button("stop",  self.kp.button_left3, self.kp.button_top, self.kp.button_w  , self.kp.button_h) #1320, 40
            
            else:#exercise did not start yet, display start only
                #button1 = start
                pygame.draw.rect(self.bk_frame_surface , self.kp.c_button_play  , pygame.Rect(self.kp.button_left1, self.kp.button_top, self.kp.button_w , self.kp.button_h ))     
                #button2 = pause
                #pygame.draw.rect(self.bk_frame_surface , self.kp.c_button_pause , pygame.Rect(self.kp.button_left2, self.kp.button_top, self.kp.button_w  , self.kp.button_h) )
                #button3 = stop
                #pygame.draw.rect(self.bk_frame_surface , self.kp.c_button_stop  , pygame.Rect(self.kp.button_left3  , self.kp.button_top, self.kp.button_w  , self.kp.button_h) )
            
                #draw text on buttons
                
                self.text_to_button("start", self.kp.button_left1, self.kp.button_top, self.kp.button_w , self.kp.button_h ) #900, 40
                #self.text_to_button("pause",  self.kp.button_left2, self.kp.button_top, self.kp.button_w  , self.kp.button_h) #1110, 40
                #self.text_to_button("stop",  self.kp.button_left3, self.kp.button_top, self.kp.button_w  , self.kp.button_h) #1320, 40

                #draw tips
                #self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                #                        self.exeinst.str['notes'][self.exeno], 3, fsize = 70 )
                #print(self.exeinst.str['notes'][self.exeno])

        if not self.ana._done:
            #if exercise did not start after 30 seconds, quit the window
            #if not self.exercise_initialized and self.exercise_start_wait == 30*3:
            #    self.kp._done = True  # Flag that we are done so we exit this loop
            #    if self.kp.kinect:
            #        self.movie.stop()
            #    pygame.quit()

            if not self.ana.paused and self.exercise_initialized:
            #if self.pa_count %50 == 0:
                #self.ana.evalstr = ''
                #self.process_analysis()
                self.process_analysis()
        else:
            #self.process_analysis()
            if 'well' in (self.ana.evalstr).lower(): #one last check for last repetition
                print("there was well")
                if len(self.evalhis) < min(self.ana.repcnt, 4):
                    self.evalhis.append(True)
            else:
                print("there was no well")
                if len(self.evalhis) < min(self.ana.repcnt, 4):
                    self.evalhis.append(False)
            self.process_finish_analysis()

        # drawing surfaces
        if self.kp.vid_rcd:  # video recoding text
            print 'Recording ', self.kp.fno
            self.io.typetext(self._frame_surface, 'Good!', (1580, 20), (255, 0, 0))
            # pdb.set_trace()
            if 'frame' in locals():
                self.cimgs.create_dataset('img_'+repr(self.kp.fno).zfill(4), data = frame)
                print('frame size', frame.shape)
                #imageio.mimwrite('0output_filename.mp4', frame , fps = 30)
            else:
                print 'Color frames unfound... frame number:', self.kp.fno
            #! change
            #uncomment original ones
            if bodyidx is not None:
                print('+=+'*50)
                self.bdimgs.create_dataset('bd_' + repr(self.kp.fno).zfill(4), data=np.dstack((bodyidx, bodyidx, bodyidx)))
                #imageio.mimwrite('0bodyind.mp4', np.dstack((bodyidx, bodyidx, bodyidx)) , fps = 30)
                print('body idx size', np.dstack((bodyidx, bodyidx, bodyidx)).shape)
            if dframe is not None:
                print('+=+'*50)
                self.dimgs.create_dataset('d_' + repr(self.kp.fno).zfill(4), data=np.dstack((dframe, dframe, dframe)))
                #imageio.mimwrite('0dimg.mp4', np.dstack((dframe, dframe, dframe)) , fps = 30)
                print('dframe size', np.dstack((dframe, dframe, dframe)).shape)
            if 'joints' in locals():
                # pdb.set_trace() 
                print('+=+'*50)
                colorspace_joint = [[jps[i].x, jps[i].y] for i in self.joints_name]
                depthspace_joint = [[djps[i].x, djps[i].y] for i in self.joints_name]
                self.color_joints.create_dataset('c_joints_'+repr(self.kp.fno).zfill(4), data=colorspace_joint)
                self.depth_joints.create_dataset('d_joints_'+repr(self.kp.fno).zfill(4), data=depthspace_joint)
                #imageio.mimwrite('0output_filename.mp4', np.dstack((dframe, dframe, dframe)) , fps = 30)
                #imageio.mimwrite('0output_filename.mp4', np.dstack((dframe, dframe, dframe)) , fps = 30)
                print('colorspace_joint', len(colorspace_joint[0]))
                print('depthspace_joint', len(depthspace_joint[1]))
            else:
                print 'Joints unfound! frame number:', self.kp.fno
            self.kp.fno += 1
            self.kp.bdjoints.append(bddic)

        # self.exeinst.blit_text(self.bk_frame_surface, self.exeno, self.kp, strtype='exe', region=1)
        # self.exeinst.blit_text(self.bk_frame_surface, self.exeno, self.kp, strtype='note', region=2, color=self.kp.c_tips)

        # draw background
        bksurface_to_draw = pygame.transform.scale(self.bk_frame_surface, (self._screen.get_width(), self._screen.get_height()))
        self._screen.blit(bksurface_to_draw, (0, 0))

        # if display window size change
        # the scale is based on a 1920 * 1080 monitor
        w_scale = self._screen.get_width()/1920.
        h_scale = self._screen.get_height()/1080.
        scale = h_scale
        if h_scale > w_scale:
            scale = w_scale

        # draw avatar
        if not self.ana._done:
            # if self.kp.kinect:
            self.movie.draw(self._screen, self.kp.scale, self.kp.pre_scale, self.kp.scene_type)
            self.kp.pre_scale = self.kp.scale
            # if scale != self.kp.scale:
            #     self.kp.pre_scale = self.kp.scale
            #     self.kp.scale = scale
        else:
            self.exeinst.show_list(self.bk_frame_surface, self.exeno)
            bksurface_to_draw = pygame.transform.scale(self.bk_frame_surface, (self._screen.get_width(), self._screen.get_height()))
            self._screen.blit(bksurface_to_draw, (0, 0))

        # emoji
        emoji_size = min(int(self._screen.get_width()*120./self.width), int(self._screen.get_height()*120./self.height))
        # emoji_err = pygame.transform.scale(self.errimg, (int(emoji_size*0.8), int(emoji_size*0.8)))
        emoji_err = pygame.transform.scale(self.errimg, (emoji_size, emoji_size/2))  # drop the height by 2
        emoji_cor = pygame.transform.scale(self.corimg, (emoji_size, emoji_size/2))  # drop the height by 2
        emoji_well = pygame.transform.scale(self.wellimg, (emoji_size*2, emoji_size*2))


        #pos_h = 940. / 1080 * self._infoObject.current_h - 70 
        pos_h = 940. / 1080 * self._infoObject.current_h - 70 + emoji_size/2 # minus makes it up, plus makes it down
        for eidx, res in enumerate(self.evalhis):
            pos_w = 120 + eidx*(emoji_size + 20)
            
            if res:
                self._screen.blit(emoji_cor, (pos_w, pos_h))
            else:
                self._screen.blit(emoji_err, (pos_w, pos_h))
        # if len(self.evalhis) == 4 and (not False in self.evalhis) and self.ana._done and self.errsums == '':
        #     self._screen.blit(emoji_well, (420, 580))

        # scene type
        if self.kp.scene_type == 2:
            self.ori = (int(self.kp.video_LB*w_scale), int(self.kp.video2_UB*h_scale))
        else:
            self.ori = (int(self.kp.video_LB*w_scale), int(self.kp.video1_UB*h_scale))

        surface_to_draw = pygame.transform.scale(self._frame_surface, (int(self.kp.vid_w*scale), int(self.kp.vid_h*scale)))
        self._screen.blit(surface_to_draw, self.ori)

        # update
        surface_to_draw = None
        bksurface_to_draw = None
        pygame.display.update()
        #maximize teh window
        #hwnd = win32gui.GetForegroundWindow()
        #win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

        #if exercise did not start after 30 seconds, quit the window
        #if not self.exercise_initialized and self.exercise_start_wait == 30*3:
        #    self.kp._done = True  # Flag that we are done so we exit this loop
            #if self.kp.kinect:
            #    self.movie.stop()
            #pygame.quit()
        # limit frames per second
        self._clock.tick(fps)
        #print("DONE WITH CLOCK")
        #self.exercise_start_wait += 1
        #print(self.exercise_start_wait)

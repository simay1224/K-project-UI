# -*- coding: utf-8 -*-
from .pykinect2 import PyKinectV2
from .pykinect2.PyKinectV2 import *
from .pykinect2 import PyKinectRuntime
import ctypes, os, datetime
import pygame, h5py, sys, copy
import pdb, time, cv2, cPickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.externals import joblib
from collections import defaultdict

# import class
import movie
# from dtw         import Dtw
from analysis import Analysis
from evaluation import Evaluation
from denoise     import Denoise
from initial_param.kparam      import Kparam
from rel         import Rel
from dataoutput  import Dataoutput
from human_model import Human_model
from skeleton    import Skeleton
from fextract    import Finger_extract
from instruction import Exeinst
from handstatus import Hand_status

fps = 30
bkimg = np.zeros([1080, 1920])
username = 'Andy_'  # user name

# colors for drawing different bodies
SKELETON_COLORS = [pygame.color.THECOLORS["red"],
                   pygame.color.THECOLORS["blue"],
                   pygame.color.THECOLORS["green"],
                   pygame.color.THECOLORS["orange"],
                   pygame.color.THECOLORS["purple"],
                   pygame.color.THECOLORS["yellow"],
                   pygame.color.THECOLORS["violet"]]
# GPR
limbidx = np.array([4, 5, 6, 8, 9, 10, 20])

class BodyGameRuntime(object):

    def __init__(self):
        global bkimg
        pygame.init()
        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()
        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1),
                                                pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)

        pygame.display.set_caption("In-Home Exercise Intervention System")
        try :
            pygame.display.set_icon(pygame.image.load('./data/icon.png'))
        except:
            pass

        # Kinect runtime object, we want only color and body frames
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color |
                                                       PyKinectV2.FrameSourceTypes_Body |
                                                       PyKinectV2.FrameSourceTypes_Depth |
                                                       PyKinectV2.FrameSourceTypes_BodyIndex)
        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self.default_h = self._infoObject.current_h
        self.default_w = self._infoObject.current_w
        self.h = self.default_h/2
        self.w = self.default_w/2

        self._frame_surface = pygame.Surface((self.default_w, self.default_h), 0, 32).convert()
        self.bk_frame_surface = pygame.Surface((self.default_w, self.default_h), 0, 32).convert()
        self.h_to_w = float(self.default_h) / self.default_w
        # here we will store skeleton data
        self._bodies = None
        # self.scene_type = 2
        
        time.sleep(5)

        if self._kinect.has_new_color_frame():
            frame = self._kinect.get_last_color_frame().reshape([1080, 1920, 4])[:, :, :3]
            bkimg = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            print ('Extract bg .....')
        else:
            print 'Failed to extract .....'

        self.exeno = 1  # exercise number
        self.__param_init__()

    def __param_init__(self, clean=False):
        try:
            self.dataset.close()
            print('Save h5py ....')
            if clean:
                os.remove(self.kp.dstr+'.h5')
                print('Remove h5py ....')
        except:
            pass
        self.fig = None
        self.kp = Kparam(self.exeno, username)
        self.movie = movie.Movie(self.exeno)
        self.kp.scale = self.movie.ini_resize(self._screen.get_width(), self._screen.get_height(), self.kp.ratio)
        self.kp.ini_scale = self.kp.scale
        self.ori = (int(self._screen.get_width()*(1-self.kp.ratio)), int(self._screen.get_height()*self.kp.ratio))  # origin of the color frame
        self.fcnt = 0
        # import class
        self.ana = Analysis()
        self.eval = Evaluation()
        self.denoise = Denoise()
        self.rel = Rel()
        self.io  = Dataoutput()
        self.h_mod = Human_model()
        self.skel = Skeleton()
        self.fextr = Finger_extract()
        self.exeinst = Exeinst()

    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def reset(self, clean=False, change=False):
        self.movie.stop(True)
        del self.movie
        self.__param_init__(clean)

    def press_event(self, press):
        """ According to the button which is pressed by the user
            doing correspond action
        """
        if press[pygame.K_ESCAPE]:
            self.kp._done = True
            self.movie.stop()

        if press[pygame.K_h]:  # use 'h' to open, 'ctrl+h' to close finger detection
            if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
                print('Finger detection disable .....')
                self.kp.handmode = False
            else:
                print('Finger detection enable .....')
                self.kp.handmode = True

        if press[pygame.K_m]:  # use 'm' to open, 'ctrl+m' to close human model
            if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
                print('Human model disable .....')
                plt.close(self.fig)
                self.kp.model_draw = False
                self.kp.model_frame = False
            else:
                print('Human model enable .....')
                self.kp.model_draw = True

        if press[pygame.K_r]:  # use 'r' to start video recording
            if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
                print('Stop recording .....')
                self.kp.vid_rcd = False
            else:
                if self.kp.clipNo == 0:
                    self.dataset = h5py.File(self.kp.dstr+'.h5', 'w')
                    self.dataset = h5py.File(self.kp.dstr+'.h5', 'r')
                    # img group
                    self.imgs = self.dataset.create_group('imgs')
    #                        self.cimgs = self.imgs.create_group('cimgs')
                    self.dimgs = self.imgs.create_group('dimgs')
                    self.bdimgs = self.imgs.create_group('bdimgs')
                print('recording .....')
                self.kp.vid_rcd = True
                self.kp.clipNo += 1

        if press[pygame.K_g]:  # use 'g' to to open, 'ctrl+g' to close gpr denoise
            if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
                print('Close denoising process .....')
                self.denoise._done = True
            else:
                print('Start denoising process .....')
                self.denoise._done = False

        if press[pygame.K_d]:  # use 'd' to to open, 'ctrl+d' to close dtw
            if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
                print('Disable human behavior analyze .....')
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

        if press[pygame.K_z]:  # use 'z' to lower the ratio of avatar to color frame
                               # 'ctrl+z' to larger the ratio of avatar to color frame
            if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
                if self.kp.ratio < 0.8:
                    self.kp.ratio += 0.05  
                    self.kp.scale = self.movie.ini_resize(self._screen.get_width(), self._screen.get_height(), self.kp.ratio)                  
            else:    
                if self.kp.ratio > 0.2:
                    self.kp.ratio -= 0.05
                    self.kp.scale = self.movie.ini_resize(self._screen.get_width(), self._screen.get_height(), self.kp.ratio)

        if press[pygame.K_0]:  # use '0' to change the scene type
            print('scene change')
            if self.kp.scene_type == 2:
               self.kp.scene_type = 1
            else:
               self.kp.scene_type += 1

        if press[pygame.K_1]:  # use '1' to change to execise 1
            self.exeno = 1
            print('====  Doing exercise 1 ====')
            self.reset(change=True)
        if press[pygame.K_2]:  # use '2' to change to execise 2
            self.exeno = 2
            print('====  Doing exercise 2 ====')
            self.reset(change=True)
        if press[pygame.K_3]:  # use '3' to change to execise 3
            self.exeno = 3
            print('====  Doing exercise 3 ====')
            self.reset(change=True)
        if press[pygame.K_4]:  # use '4' to change to execise 4
            self.exeno = 4
            print('====  Doing exercise 4 ====')
            self.reset(change=True)
        if press[pygame.K_5]:  # use '5' to change to execise 5
            self.exeno = 5
            print('====  Doing exercise 5 ====')
            self.reset(change=True)
        if press[pygame.K_6]:  # use '6' to change to execise 6
            self.exeno = 6
            print('====  Doing exercise 6 ====')
            self.reset(change=True)
        if press[pygame.K_7]:  # use '7' to change to execise 7
            self.exeno = 7
            print('====  Doing exercise 7 ====')
            self.reset(change=True)

        if press[pygame.K_p]:
            pdb.set_trace()

    def run(self):
        wait_key_cnt = 3
        while not self.kp._done:
            bddic = {}
            jdic  = {}

            # === key pressing ===
            if(wait_key_cnt < 3):
                wait_key_cnt += 1
            if(pygame.key.get_focused() and wait_key_cnt >= 3):
                press = pygame.key.get_pressed()
                self.press_event(press)
                wait_key_cnt = 0

            # === Main event loop ===
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    self._done = True  # Flag that we are done so we exit this loop
                    self.movie.stop()
                elif event.type == pygame.VIDEORESIZE:  # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'],
                                   pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)

            # initail background frame 
            self.draw_color_frame(np.zeros(1920*1080*4).astype(np.uint8), self.bk_frame_surface)
            # === extract data from kinect ===
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = frame.reshape(1080, 1920, 4)[:, :, :3]
            if self._kinect.has_new_body_frame():
                self._bodies = self._kinect.get_last_body_frame()
                timestamp = datetime.datetime.now()
            if self._kinect.has_new_body_index_frame():
                bodyidx = self._kinect.get_last_body_index_frame()
                bodyidx = bodyidx.reshape((424, 512))
            if self._kinect.has_new_depth_frame():
                dframe, oridframe = self._kinect.get_last_depth_frame()
                dframe = dframe.reshape((424, 512))

            # === when user is detected ===
            if self._bodies is not None:
                closest_ID = -1
                cdist      = np.inf
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked:
                        continue
                    if body.joints[20].Position.z <= cdist:  # find the closest body
                        closest_ID = i
                        cdist = body.joints[20].Position.z
                if (closest_ID != -1):
                    body   = self._bodies.bodies[closest_ID]
                    joints = body.joints
                    rec_joints = body.joints
                    for ii in xrange(25):
                        jdic[ii] = joints[ii]
                    jps  = self._kinect.body_joints_to_color_space(joints)  # joint points in color domain
                    djps = self._kinect.body_joints_to_depth_space(joints)  # joint points in depth domain

                    # === fingers detection ===
                    if self.kp.handmode:  # finger detect and draw
                        self.fextr.run(frame, bkimg, body, bddic, jps, SKELETON_COLORS[i], self._frame_surface)

                    # === joint reliability ===
                    Rel, Relary = self.rel.run(jdic)
                    # joint's reliability visulization
                    # self.skel.draw_Rel_joints(jps, Rel, self._frame_surface)

                    # === dtw analyze & denoising process ===
                    if not self.ana._done:
                        # if self.ana.exer[self.exeno].limbjoints:
                        #     modJary = self.h_mod.human_mod_pts(joints)  # modJary is 7*3 array
                        #     modJary = modJary.flatten().reshape(-1, 21)  # change shape to 1*21 array
                        # else:
                        modJary = self.h_mod.human_mod_pts(joints, False)  # modJary is 11*3 array
                        modJary = modJary.flatten().reshape(-1, 33)  # change shape to 1*33 array                            
                        if not self.denoise._done:
                            if not len(Relary) == 0:
                                # === GPR denoising ===
                                if all(ii > 0.6 for ii in Relary[limbidx]):  # all joints are reliable
                                    reconJ = modJary  # reconJ is 1*21 array
                                else:  # contains unreliable joints
                                    # if self.ana.exer[self.exeno].limbjoints:
                                    #     reconJ, unrelidx = self.denoise.run(modJary, Relary)
                                    #     JJ = self.h_mod.reconj2joints(rec_joints, reconJ.reshape(7, 3))
                                    # else:
                                    reconJ, unrelidx = self.denoise.run(modJary[:, 12:], Relary)
                                    JJ = self.h_mod.reconj2joints(rec_joints, reconJ.reshape(7, 3))
                                    reconJ = np.hstack([modJary[:, :12], reconJ]) 
                                    #  === recon 2D joints in color domain ===
                                    for ii in [4, 5, 6, 8, 9, 10, 20]:
                                        rec_joints[ii].Position.x = JJ[ii][0]
                                        rec_joints[ii].Position.y = JJ[ii][1]
                                        rec_joints[ii].Position.z = JJ[ii][2]
                                    tmp_jps = self._kinect.body_joints_to_color_space(rec_joints)  # joints in color domain
                                    rec_jps = np.zeros([21,2])
                                    for ii in xrange(21):
                                        if ii in unrelidx:
                                            rec_jps[ii, 0] = tmp_jps[ii].x
                                            rec_jps[ii, 1] = tmp_jps[ii].y
                                        else:
                                            rec_jps[ii, 0] = jps[ii].x
                                            rec_jps[ii, 1] = jps[ii].y                                            
                                    self.skel.draw_body(rec_joints, rec_jps, SKELETON_COLORS[3], self._frame_surface, 30)
                            else:
                                reconJ = modJary
                        else:
                            reconJ = modJary

                        # === analyze ===
                        self.ana.run(self.exeno, reconJ[0], self.bk_frame_surface,\
                                     self.eval, self.kp, body, dframe, djps)                        

                        # === show hand status === 
                        # self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                        #                     self.ana.hs.htext(body.hand_left_state, body.hand_right_state), 4 ,\
                        #                     (255, 130, 45, 255))

                        if self.ana.evalstr != '':
                            if 'well' in (self.ana.evalstr).lower():
                                self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp, self.ana.evalstr, 2, (0, 255, 0, 255))
                            else:
                                self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp, self.ana.evalstr, 2, (255, 0, 0, 255))

                            self.fcnt += 1
                            if self.fcnt > 30 :
                                self.ana.evalstr = ''
                                self.fcnt  = 0
                    else:
                        self.eval.blit_text(self.bk_frame_surface, self.exeno, self.kp,\
                                            'Exercise '+str(self.exeno)+' is done', 1)
                        if not self.kp.finish:
                            errs = [self.ana.brth.err, self.ana.hs.err, self.ana.dtw.err,\
                                    self.ana.shld.err, self.ana.clsp.err, self.ana.swing.err]  # append err msg here
                            dolist = [self.ana.brth.do, self.ana.hs.do, self.ana.dtw.do,\
                                      self.ana.shld.do, self.ana.clsp.do, self.ana.swing.do]
                            self.eval.run(self.exeno, self.ana.brth, self.ana.hs)
                            self.eval.errmsg(errs, dolist) 
                            print self.ana.dtw.idxlist
                            self.kp.finish = True
                    # draw skel
                    self.skel.draw_body(joints, jps, SKELETON_COLORS[i], self._frame_surface, 8)

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
                    # === save data ===
                    bddic['timestamp'] = timestamp
                    bddic['jointspts'] = jps   # joints' coordinate in color space (2D)
                    bddic['depth_jointspts'] = djps  # joints' coordinate in depth space (2D)
                    bddic['joints'] = jdic  # joints' coordinate in camera space (3D)
                    bddic['vidclip'] = self.kp.clipNo
                    bddic['Rel'] = Rel
                    bddic['LHS'] = body.hand_left_state
                    bddic['RHS'] = body.hand_right_state

                self.kp.framecnt += 1  # frame no
            else:
                self.io.typetext(self._frame_surface, 'Kinect does not connect!!', (20, 100))


            # === text infomation on the surface ===
            if self.kp.vid_rcd:  # video recoding text
                self.io.typetext(self._frame_surface, 'Video Recording', (1580, 20), (255, 0, 0))
#                self.cimgs.create_dataset('img_'+repr(self.kp.fno).zfill(4), data = frame)
                self.bdimgs.create_dataset('bd_' + repr(self.kp.fno).zfill(4), data=np.dstack((bodyidx, bodyidx, bodyidx)))
                self.dimgs.create_dataset('d_' + repr(self.kp.fno).zfill(4), data=np.dstack((dframe, dframe, dframe)))
                self.kp.fno += 1
                self.kp.bdjoints.append(bddic)
            else:
                pass
                self.io.typetext(self._frame_surface, 'Not Recording', (1580, 20), (0, 255, 0))  

            
            self.exeinst.blit_text(self.bk_frame_surface, self.exeno, self.kp, strtype='exe', region=1) 
            self.exeinst.blit_text(self.bk_frame_surface, self.exeno, self.kp, strtype='note', region=2, color=(255, 0, 0, 0))
            # draw back ground
            bksurface_to_draw = pygame.transform.scale(self.bk_frame_surface, (self._screen.get_width(), self._screen.get_height()))
            self._screen.blit(bksurface_to_draw, (0, 0))

            if self.kp.scene_type == 1:
                self.ori = (0, 0) 
            else:
                self.ori = (int(self._screen.get_width()*self.kp.ratio), int(self._screen.get_height()*self.kp.ratio))

            h_scale = 1.*self._screen.get_height()/self.h
            w_scale = 1.*self._screen.get_width()/self.w
            # scale = 1
            if h_scale > w_scale:
                scale = w_scale
            else:
                scale = h_scale
            self.w = self.w *scale
            self.h = self.h *scale  
 

            self.kp.scale = self.kp.scale * scale
            self.movie.draw(self._screen, self.w, self.h, self.kp.scale, self.kp.pre_scale, self.kp.scene_type)
            self.kp.pre_scale = self.kp.scale

            
            surface_to_draw = pygame.transform.scale(self._frame_surface, (int(self.w*(1-self.kp.ratio)), int(self.h*(1-self.kp.ratio))))     
            self._screen.blit(surface_to_draw, self.ori)


            # update
            surface_to_draw = None
            bksurface_to_draw = None
            pygame.display.update()
            # limit frames per second
            self._clock.tick(fps)
        # user end the programe
        self.movie.stop(True)   # close avatar
        self._kinect.close()    # close Kinect sensor
        # print self.dtw.idxlist  # show the analyzed result
        # save the recording data

        if self.kp.bdjoints != []:
            cPickle.dump(self.kp.bdjoints, file(self.kp.dstr+'.pkl', 'wb'))
        try:
            self.dataset.close()
        except:
            pass
        pygame.quit()  # quit


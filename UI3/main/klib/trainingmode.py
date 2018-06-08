# -*- coding: utf-8 -*-
import ctypes, os, datetime, glob
import pygame, sys, copy
import pdb, time, cv2

if sys.platform == "win32":
    import h5py
    from .pykinect2 import PyKinectV2
    from .pykinect2.PyKinectV2 import *
    from .pykinect2 import PyKinectRuntime

if sys.version_info >= (3, 0):
    import _pickle as cPickle
else:
    import cPickle
    
import numpy as np
# import class
from ..klib import movie
from .initial_param.kparam      import Kparam
from ..klib.dataoutput  import Dataoutput
from ..klib.skeleton    import Skeleton

fps = 30
bkimg = np.zeros([1080, 1920])
# username = 'Andy_'  # user name

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
        pygame.init()
        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()
        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1),
                                                pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)

        pygame.display.set_caption("Lymph Coach - Training mode")
        try :
            pygame.display.set_icon(pygame.image.load('./data/imgs/others/icon.png'))
        except:
            pass

        if sys.platform == "win32":
            # Kinect runtime object, we want only color and body frames
            self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color |
                                                           PyKinectV2.FrameSourceTypes_Body
                                                           )
        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self.default_h = self._infoObject.current_h
        self.default_w = self._infoObject.current_w
        self.h = self.default_h/2
        self.w = self.default_w/2

        self._frame_surface = pygame.Surface((self.default_w, self.default_h), 0, 32).convert()
        self.bk_frame_surface = pygame.Surface((self.default_w, self.default_h), 0, 32).convert()

        self.bkidx = 11
        self.bklist = glob.glob(os.path.join('./data/imgs/bkimgs', '*.jpg'))
        self.readbackground()
        self.h_to_w = float(self.default_h) / self.default_w
        # here we will store skeleton data
        self._bodies = None
        time.sleep(5)

        self.exeno = 1  # exercise number
        self.__param_init__()

    # Read global background
    def readbackground(self):
        self.bkimg = cv2.imread(self.bklist[self.bkidx])
        self.bkimg = cv2.resize(self.bkimg, (self._infoObject.current_w, self._infoObject.current_h))

        if sys.platform == "win32":
            self.bkimg = np.dstack([cv2.resize(self.bkimg, (1920, 1080)), np.zeros([1080, 1920])]).astype(np.uint8)
        else:
            self.bkimg = np.dstack([255 * np.ones([self._infoObject.current_h, self._infoObject.current_w]), self.bkimg[:, :, ::-1]]).astype(np.uint8)

    def __param_init__(self, clean=False):

        self.kp = Kparam(self.exeno)

        if self.kp.kinect:
            self.movie = movie.Movie(self.exeno)
        else:
            self.movie = movie.Movie(self.exeno, False, 480, 272)

        self.kp.scale = self.movie.ini_resize(self._screen.get_width(), self._screen.get_height(), self.kp.ratio)
        self.kp.ini_scale = self.kp.scale
        self.ori = (int(self._screen.get_width()*self.kp.video_LB/1920.), int(self._screen.get_height()*0.5))  # origin of the color frame
        self.cntdown = 900
        self.io  = Dataoutput()
        self.skel = Skeleton()

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


    def reset(self, clean=False, change=False):
        if self.kp.kinect:
            self.movie.stop(True)
            del self.movie
        self.__param_init__(clean)

    def press_event(self, press):
        """ According to the button which is pressed by the user
            doing correspond action
        """
        if press[pygame.K_ESCAPE]:
            self.kp._done = True
            if self.kp.kinect:
                self.movie.stop()

        if press[pygame.K_q]:
            self.kp._done = True
            if self.kp.kinect:
                self.movie.stop()

        if press[pygame.K_i]:  # use 'i' to reset every parameter
            print('Reseting ............................')
            self.reset()

        if press[pygame.K_w]: # use 'w' to change background image
            self.bkidx += 1
            if self.bkidx >= len(self.bklist):
                self.bkidx -= len(self.bklist)
            self.readbackground()

        # if press[pygame.K_z]:  # use 'z' to lower the ratio of avatar to color frame
        #                        # 'ctrl+z' to larger the ratio of avatar to color frame
        #     if press[pygame.K_LCTRL] or press[pygame.K_RCTRL]:
        #         if self.kp.ratio <= 0.6:
        #             self.kp.ratio += 0.05
        #             self.kp.scale = self.movie.ini_resize(self._screen.get_width(), self._screen.get_height(), self.kp.ratio)
        #     else:
        #         if self.kp.ratio > 0.4:
        #             self.kp.ratio -= 0.05
        #             self.kp.scale = self.movie.ini_resize(self._screen.get_width(), self._screen.get_height(), self.kp.ratio)

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
        if press[pygame.K_SPACE]:
            if self.exeno == 7:
                self.exeno = 1
            else:
                self.exeno += 1
            print('Next exercise ..................')
            self.reset()

        if press[pygame.K_p]:
            pdb.set_trace()

    def run(self):
        wait_key_cnt = 3
        while not self.kp._done:
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
                    if self.kp.kinect:
                        self.movie.stop()
                elif event.type == pygame.VIDEORESIZE:  # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'],
                                   pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)

            # initail background frame
            self.draw_color_frame(self.bkimg, self.bk_frame_surface)

            if self.kp.kinect:
                # === extract data from kinect ===
                if self._kinect.has_new_color_frame():
                    frame = self._kinect.get_last_color_frame()
                    self.draw_color_frame(frame, self._frame_surface)
                if self._kinect.has_new_body_frame():
                    self._bodies = self._kinect.get_last_body_frame()

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
                        jps  = self._kinect.body_joints_to_color_space(joints)  # joint points in color domain

                        # draw skel
                        self.skel.draw_body(joints, jps, SKELETON_COLORS[i], self._frame_surface, 8)

                        # self.cntdown -= 1
                        # if self.cntdown == 0:
                        #     if self.exeno == 7:
                        #         self.exeno = 1
                        #     else:
                        #         self.exeno += 1
                        #     print('Next exercise ..................')
                        #     self.reset()
                else:
                    self.io.typetext(self._frame_surface, 'Kinect does not connect!!', (20, 100))
            else:
                self.io.typetext(self._frame_surface, 'Kinect does not connect!!', (20, 100))

            # draw back ground
            bksurface_to_draw = pygame.transform.scale(self.bk_frame_surface, (self._screen.get_width(), self._screen.get_height()))
            self._screen.blit(bksurface_to_draw, (0, 0))

            # if display window size change
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

            # draw avatar

            self.movie.draw(self._screen, self.kp.scale, self.kp.pre_scale, tmode=True)
            self.kp.pre_scale = self.kp.scale
            surface_to_draw = pygame.transform.scale(self._frame_surface, (int(self.w*self.kp.vid_w_t/1920.), int(self.h*self.kp.vid_h_t/1080.)))
            self.ori = (int(self._screen.get_width()/2-int(self.kp.vid_w_t/4.*self.kp.scale)), int(self._screen.get_height()*self.kp.video2_UB/1080.))
            self._screen.blit(surface_to_draw, self.ori)

            # update
            surface_to_draw = None
            bksurface_to_draw = None
            pygame.display.update()
            # limit frames per second
            self._clock.tick(fps)
        # user end the programe
        if self.kp.kinect:
            self.movie.stop(True)   # close avatar
            self._kinect.close()    # close Kinect sensor

        pygame.quit()  # quit

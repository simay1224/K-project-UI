

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from Kfunc.IO     import *
from Kfunc.finger import *
from Kfunc.skel   import skel
from Kfunc.model  import Human_mod   as Hmod
from Kfunc.Rel    import reliability as REL
from Kfunc.GPR    import GPR
from Kfunc.DTW    import DTW_matching2
import ctypes, os
import pygame, h5py, datetime,sys
import pdb, time, cv2, cPickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.externals import joblib
from collections import defaultdict


#if sys.hexversion >= 0x03000000:
#    import _thread as thread
#else:
#    import thread
fps = 60





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
        self._frame_surface = pygame.Surface((1920, 1080), 0, 32)#.convert()
        # here we will store skeleton data 
        self._bodies = None
        self._done   = False
        # Video
        pygame.mixer.quit()
        self.movie = pygame.movie.Movie(r'test-mpeg.mpg')


    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()
        

    def run(self):
     

        # -------- Main Program Loop -----------
        while not self._done:

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
            
                                  
                    
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())    
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
            
            self._screen.blit(surface_to_draw, (0,0))
            self.movie.set_display(self._frame_surface)
            self.movie.play()  
            self._screen.blit(self._frame_surface,(0,0)) 
            surface_to_draw = None
            pygame.display.update()

            self._clock.tick(fps)
    
        # Close our Kinect sensor, close the window and quit.
            #print time.clock()-ST
               
            
        self._kinect.close()
        


__main__ = "Kinect v2 Body Game"

game = BodyGameRuntime();
game.run();

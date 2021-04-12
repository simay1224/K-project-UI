import pygame
import numpy as np
from .initial_param.kparam import Kparam

class Movie(object):
    """A Movie playing class with pygame package
    """

    def __init__(self, filename, width = 0, height = 0):
            self.kp = Kparam()

            if self.kp.kinect:
                pygame.mixer.quit()
                #we have to skip the video 5
                #if filename ==5:
                 #   filename ==6
                #elif filename == 6:
                 #   filename ==7
                #self._movie = pygame.movie.Movie('./data/video/ex'+str(filename)+'.mpg')
                #if filename ==1:
                #    print('^'*100)
                #    print('filename is 1')
                #    self._movie = pygame.movie.Movie('./data/video/ex'+str(filename)+'.mp4')
                #else:
                self._movie = pygame.movie.Movie('./data/video/ex'+str(filename)+'.mpg')

                self.w, self.h = [size for size in self._movie.get_size()]
                print('width and height is', self.w, self.h)
                self.mscreen = pygame.Surface((self.kp.vid_w/2, self.kp.vid_h/2)).convert()
                self._movie.set_display(self.mscreen, pygame.Rect(0, 0, self.kp.vid_w/2, self.kp.vid_h/2))
                #self._movie.play()
            else:
                self.w, self.h = width, height
                self._movie = np.zeros((self.w, self.h, 3))
                self.mscreen = pygame.Surface((self.kp.vid_w/2, self.kp.vid_h/2)).convert()

    def stop(self, delete=False):
        if not self.kp.kinect:
            return

        self._movie.stop()
        if delete:
            del self._movie
            pygame.mixer.init()

    def pause(self):
        if not self.kp.kinect:
            return
        self._movie.pause()

    def play(self):
        if not self.kp.kinect:
            return
        self._movie.play()


    def rewind(self):
        if not self.kp.kinect:
            return
        "replay the movie"
        self._movie.rewind()

    def ini_resize(self, screen_w, screen_h, ratio=0.5):
        "movie initial resize"
        if screen_w*ratio/self.w >=  screen_h*ratio/self.h:
            return screen_h*ratio/self.h
        else:
            return screen_w*ratio/self.w

    def position(self, screen_w, screen_h, scale=1, Type=1):
        """ generate movie's position.
            According to the keyboard feedback may become larger or smaller.
            Type : 1 => upper-left corner, 2 => lower-right corner
        """
        if Type == 1:
            return [int(screen_w*self.kp.video_LB/1920.), int(screen_h*self.kp.video2_UB/1080.)]
        elif Type == 2:
            return [int(screen_w*self.kp.video_LB/1920.), int(screen_h*self.kp.video1_UB/1080.)]

    def draw(self, surface, scale=1, pre_scale=1, Type=1, tmode=False):
        "Draw current frame to the surface"

        if not tmode:
            if scale != pre_scale:
                self.mscreen = pygame.transform.scale(self.mscreen, (int(self.kp.vid_w/2.*scale), int(self.kp.vid_h/2.*scale)))
                if self.kp.kinect:
                    self._movie.set_display(self.mscreen, pygame.Rect(0, 0, int(self.kp.vid_w/2.*scale), int(self.kp.vid_h/2.*scale)))
            surface.blit(self.mscreen, self.position(surface.get_width(), surface.get_height(), scale, Type))
        else:
            if scale != pre_scale:
                self.mscreen = pygame.transform.scale(self.mscreen, (int(self.kp.vid_w_t/2.*scale), int(self.kp.vid_h_t/2.*scale)))
                if self.kp.kinect:
                    self._movie.set_display(self.mscreen, pygame.Rect(0, 0, int(self.kp.vid_w_t/2.*scale), int(self.kp.vid_h_t/2.*scale)))
            # surface.blit(self.mscreen, (surface.get_width()/2-int(self.kp.vid_w/4.*scale), int(surface.get_height()*self.kp.video1_UB/1080.)))
            surface.blit(self.mscreen, (surface.get_width()/2-int(self.kp.vid_w_t/4.*scale), int(surface.get_height()*50/1080.)))

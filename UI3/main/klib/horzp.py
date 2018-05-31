import numpy as np
from math import acos
from scipy.signal import argrelextrema
from initial_param.kinect_para import Kinect_para
from scipy.ndimage.filters import gaussian_filter1d as gf
import inflect, pdb

class Horzp(object):
    """ Exercise 4 : horizontal pumping
    """
    def __init__(self):
        self._done = True
        self.state = 'T-pose'
        self.flag = False
        # default parameters
        self.cnt     = 0
        self.do      = False
        self.err     = []
        self.errsum  = []
        self.evalstr = ''
        self.eval    = ''

    def run(self, joints, dmap, djps):
        
        dist = abs(joints[18]-joints[27])
        if dist > 700:
            self.state = 'T-pose'
            if self.flag:
                self.flag = False
                self.cnt += 1    
        elif dist < 300:
            self.flag = True
            self.state = 'chest'
  
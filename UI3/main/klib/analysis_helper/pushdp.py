from ..initial_param.kinect_para import Kinect_para

import numpy as np
from math import acos
from scipy.signal import argrelextrema
from scipy.ndimage.filters import gaussian_filter1d as gf
import inflect, pdb

class Pushdp(object):
    """ Exercise 4 : horizontal pumping
    """
    def __init__(self):
        self.flag         = False
        self.cflag        = False
        self.tflag        = True
        self.Ltangle      = [0, 0, 0, 0]  # Armpit angle in T-pose
        self.Lcangle      = [0, 0, 0, 0]  # Armpit angle in arm close
        self.Rtangle      = [0, 0, 0, 0]  # Armpit angle in T-pose
        self.Rcangle      = [0, 0, 0, 0]  # Armpit angle in arm close
        self.Max_wrist_y  = -10**6
        self.Min_wrist_y  = 10**6
        self.cnvt         = inflect.engine()
        # default parameters
        self.cnt     = 0
        self.do      = False
        self.err     = []
        self.errsum  = []
        self.evalstr = ''
        self.eval    = ''

        self.ongoing_cycle= True

    def joint_angle(self, joints, idx=[4, 5, 6], y_vec=np.array([0, 1, 0]) ,offset=0):
        """ finding the angle between 3 joints.
            default joints are left shld, elbow, wrist.
        """
        if joints.shape[0] == 33:
            offset = 4
        if idx[0] == 8:  # right arm
            offset += 3
        #  sholder -> Elbow
        vec1 = np.array([joints[(offset+1)*3]-joints[(offset*3)],
                        joints[(offset+1)*3+1]-joints[(offset*3)+1],
                        joints[(offset+1)*3+2]-joints[(offset*3)+2]])
        # Elbow - Wrist
        vec2 = np.array([joints[(offset+1)*3]-joints[(offset+2)*3],
                        joints[(offset+1)*3+1]-joints[(offset+2)*3+1],
                        joints[(offset+1)*3+2]-joints[(offset+2)*3+2]])
        costheta_ampit = vec1.dot(-1*y_vec)/sum(vec1**2)**.5/sum(y_vec**2)**.5
        costheta_elbow = vec2.dot(-1*y_vec)/sum(vec2**2)**.5/sum(y_vec**2)**.5
        costheta_sew = vec1.dot(vec2)/sum(vec1**2)**.5/sum(vec2**2)**.5
        return np.array([acos(costheta_ampit), acos(costheta_elbow), acos(costheta_sew)])*180/np.pi

    def run(self, joints, stus):
        if self.cnt >= 4:
            return

        wrist_y = joints[19]
        self.ongoing_cycle= True
        if stus == 'up':
            if self.cflag:
                self.cflag = False
                if self.cnt > 0:
                    if self.Lcangle[self.cnt] > 100 or self.Rcangle[self.cnt] > 100: # was 50 , 50
                        self.err.append('At the '+self.cnvt.ordinal(self.cnt+1)+ ' time try, arms are not pulled low enough.')
                        self.errsum.append('Arms are not pulled low enough.')
            if self.Max_wrist_y < wrist_y:
                self.Max_wrist_y = wrist_y
                if self.cnt < 4:
                    self.Ltangle[self.cnt] = np.mean(self.joint_angle(joints)[::2])
                    self.Rtangle[self.cnt] = np.mean(self.joint_angle(joints, idx=[8, 9, 10])[::2])
            if self.flag:
                if self.eval == '':
                    self.evalstr = 'Subsequence done: Well done.'
                else:
                    self.evalstr = 'Subsequence done.\n'+self.eval
                    self.eval = ''
                self.flag = False
                self.Min_wrist_y = 10**6
                self.tflag = True
                self.ongoing_cycle= False
                self.cnt += 1
        elif stus == 'vshape':
            if self.tflag:
                self.tflag = False
                if self.Ltangle[self.cnt] < 85 or self.Rtangle[self.cnt] < 85: #was 160, 160
                    self.err.append('At the '+self.cnvt.ordinal(self.cnt+1)+ ' time try, please keep your arms straight.')
                    self.errsum.append('Please keep your arms straight.')
            if self.Min_wrist_y > wrist_y:
                self.Min_wrist_y = wrist_y
                if self.cnt < 4:
                    self.Lcangle[self.cnt] = self.joint_angle(joints)[2]
                    self.Rcangle[self.cnt] = self.joint_angle(joints, idx=[8, 9, 10])[2]
            if not self.flag:
                if self.eval == '':
                    self.evalstr = 'Subsequence done: Well done.'
                else:
                    self.evalstr = 'Subsequence done.\n'+self.eval
                    self.eval = ''
                self.flag = True
                self.cflag = True
                self.Max_wrist_y = -10**6

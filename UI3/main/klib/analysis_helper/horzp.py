from ..initial_param.kinect_para import Kinect_para

import numpy as np
from math import acos
from scipy.signal import argrelextrema
from scipy.ndimage.filters import gaussian_filter1d as gf
import inflect

class Horzp(object):
    """ Exercise 4 : horizontal pumping
    """
    def __init__(self):
        self.state = ''
        self.flag = False
        self.cflag        = False
        self.tflag        = True
        self.Ltangle      = [0, 0, 0, 0]  # Armpit angle in T-pose
        self.Lcangle      = [0, 0, 0, 0]  # Armpit angle in arm close
        self.Rtangle      = [0, 0, 0, 0]  # Armpit angle in T-pose
        self.Rcangle      = [0, 0, 0, 0]  # Armpit angle in arm close
        self.Max_dist     = 700
        self.Min_dist     = 300
        self.cnvt         = inflect.engine()
        # default parameters
        self.cnt     = 0
        self.do      = False
        self.err     = []
        self.errsum  = []
        self.evalstr = ''
        self.eval    = ''
        #boolean for ongoing cycle
        self.ongoing_cycle= True

    def joint_angle(self, joints, idx=[4, 5, 6], y_vec=np.array([0, -1, 0]) ,offset=0):
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
        costheta_ampit = vec1.dot(-1*y_vec)/sum(vec1**2)**.5/sum(y_vec**2)**.5
        return acos(costheta_ampit)*180/np.pi

    def run(self, joints):
        if self.cnt >= 4:
            return
        dist = abs(joints[18]-joints[27]) # difference between x coordinates of two wrists
        self.ongoing_cycle= True
        #print('*()*'*80)
        #print("dist is ",dist)
        if dist > 700: # was originally 700
            if self.cflag:
                self.cflag = False
                if self.cnt > 0:
                    if self.Lcangle[self.cnt] < 56 or self.Rcangle[self.cnt] < 56: # was 80, then tried 56
                        self.evalstr = 'Please keep your arms horizontally.\n'
                        self.eval = 'Please keep your arms horizontally.\n'
                        self.err.append('At the '+self.cnvt.ordinal(self.cnt+1)+ ' time try, arms are not horizontal.')
                        self.errsum.append('Arms are not horizontal.')
            if self.Max_dist < dist:
                self.Max_dist = dist
                if self.cnt < 4:
                    self.Ltangle[self.cnt] = self.joint_angle(joints)
                    self.Rtangle[self.cnt] = self.joint_angle(joints, idx=[8, 9, 10])
            self.state = 'T-pose'
            if self.flag:
                if self.eval == '':
                    self.evalstr = 'Subsequence done: Well done.'
                else:
                    self.evalstr = 'Subsequence done.\n'+self.eval
                    self.eval = ''
                self.flag = False
                self.Min_dist = 300
                self.tflag = True
                self.cnt += 1
                self.ongoing_cycle= False
        elif dist < 350: #was originally 300
            if self.tflag:
                self.tflag = False
                if self.Ltangle[self.cnt] < 56 or self.Rtangle[self.cnt] < 56: # was originally 80, then tried 56
                    self.evalstr = 'Please keep your arms horizontally.\n'
                    self.eval = 'Please keep your arms horizontally.\n'
                    self.err.append('At the '+self.cnvt.ordinal(self.cnt+1)+ ' time try, arms are not horizontal.')
                    self.errsum.append('Arms are not horizontal.')
            if self.Min_dist > dist:
                self.Min_dist = dist
                if self.cnt < 4:
                    self.Lcangle[self.cnt] = self.joint_angle(joints)
                    self.Rcangle[self.cnt] = self.joint_angle(joints, idx=[8, 9, 10])
            if not self.flag:
                if self.eval == '':
                    self.evalstr = 'Subsequence done: Well done.'
                else:
                    self.evalstr = 'Subsequence done.\n'+self.eval
                    self.eval = ''
                self.flag = True
                self.cflag = True
                self.state = 'chest'
                self.Max_dist = 700
        print("state is", self.state)
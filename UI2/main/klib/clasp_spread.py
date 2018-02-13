import numpy as np
from scipy.ndimage.filters import gaussian_filter1d as gf
import inflect
from initial_param.kinect_para import Kinect_para

class Clasp_spread(object):
    """
    """
    def __init__(self):
        self.cnt         = 0
        self.handsdown   = True   # True : hands down, False : hands up
        self.bstraight   = False  # check if body straight
        self.clasp_cnt   = 0
        self.spread_cnt  = 0
        self.spread_time = 0
        self.hold        = 18
        self.elbowstus   = {}
        self.first       = True
        self.cnvt        = inflect.engine()  # converting numerals into ordinals
        self.kpm         = Kinect_para()
        self.elbowstus['clasp'] = False
        self.elbowstus['spread'] = False
        self.err     = []
        self.evalstr = ''
        self.do      = False

    def state_update(self, joints):
        """ update accoding to each frame data
        """
        if joints[kpm.LElbow_y] < joints[kpm.SpineShld_y]-20 and joints[kpm.RElbow_y]<joints[kpm.SpineShld_y]-20:
            self.clasp_cnt += 1
            self.spread_cnt = 0
        elif joints[kpm.LElbow_y]>joints[kpm.SpineShld_y]-20 and joints[kpm.RElbow_y]>joints[kpm.SpineShld_y]-20:
            self.clasp_cnt += 1
            self.spread_cnt = 0
        if self.clasp_cnt > self.hold and not self.handsdown:
            self.handsdown = True
            self.elbowstus['clasp'] == False
        if self.spread_cnt > self.hold and self.handsdown:
            self.handsdown = False
            self.first = False
            self.do    = True    
            self.spread_time = 0
            self.elbowstus['spread'] == False  

    def bodystraight(self, kpm, joints, th=12):
        """ check whether body is straight or not
        """
        torso_z = np.mean(joints[kpm.SpineBase_z, kpm.SpineMid_z])
        if torso_z-joints[kpm.Neck_z] > th and torso_z-joints[kpm.Head_z] > th:
           self.evalstr = 'please stand straight'
           return False
        return True 

    def clasp(self, joints, kpm, spread_th=30, elbow_th=75):
        """ hands clasp state
        """        
        if self.clasp_cnt == self.hold:
            self.elbowstus['clasp'] = False
            if not self.first:
                if not self.elbowstus['spread']:
                    if self.spread_time == 0:
                        self.evalstr = 'elbows spread incorrect !! => elbows should behind your head !!'
                        self.err.append('The '+self.cnvt.ordinal(self.cnt)+ 'time spread is not good. Elbows should behind your head')
                    elif self.spread_time < spread_th:
                        self.evalstr = 'elbows spread incorrect !! => too fast !!'
                        self.err.append('The '+self.cnvt.ordinal(self.cnt)+ 'time spread is not good. Doing too fast !!')
                    self.cnt += 1
                    self.elbowstus['spread'] = True
                else:
                    self.evalstr = 'Well done'
        if np.abs(joints[kpm.LElbow_x]-joints[kpm.RElbow_x]) < 75:
            self.elbowstus['clasp'] = True

    def spread(self, joints, kpm, spread_th=30):
        """ hands spread state
        """
        if self.spread_cnt == self.hold:
            self.elbowstus['spread'] = False
            if not self.elbowstus['clasp']:
                self.evalstr = 'elbows clasp incorrect : elbows do not clasp'
                self.err.append('The '+self.cnvt.ordinal(self.cnt)+ 'time clasp is not good. Not clasp !!')
                self.elbowstus['clasp'] = True
            else:
                self.evalstr = 'Well done'
        if (joints[kpm.LElbow_z]+joints[kpm.RElbow_z])/2 > joints[kpm.Head_z]:
            self.spread_time += 1
        if self.spread_time >= spread_th:
            self.elbowstus['spread'] = True

    def run(self, joints):
        """ Joint : denoised unified joint
        """
        if self.handsdown:
            self.clasp(joints, self.kpm)
        else:
            self.spread(joints, self.kpm)
            self.bstraight = self.bodystraight(joints, self.kpm)
        self.state_update(joints)

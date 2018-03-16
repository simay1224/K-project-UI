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
        self.clasp_cnt   = 0
        self.spread_cnt  = 0
        self.spread_time = 0
        self.hold        = 5
        self.first       = True
        self.cnvt        = inflect.engine()  # converting numerals into ordinals
        self.kpm         = Kinect_para()
        self.elbowstus   = {}
        self.elbowstus['clasp'] = False
        self.elbowstus['spread'] = False
        # save in log
        self.holdtime = []
        self.claspsuc = 0
        # default parameters
        self.cnt     = 0
        self.do      = False
        self.err     = []
        self.evalstr = ''
        self.eval    = ''

    def state_update(self, joints, kpm):
        """ update accoding to each frame data
        """
        if joints[kpm.LElbow_y] < joints[kpm.SpineShld_y]-20 and joints[kpm.RElbow_y] < joints[kpm.SpineShld_y]-20:
            self.clasp_cnt += 1
            self.spread_cnt = 0
        elif joints[kpm.LElbow_y] > joints[kpm.SpineShld_y]-20 and joints[kpm.RElbow_y] > joints[kpm.SpineShld_y]-20:
            self.spread_cnt += 1
            self.clasp_cnt = 0
        if self.clasp_cnt >= self.hold and not self.handsdown:
            self.handsdown = True
            self.elbowstus['clasp'] == False
        if self.spread_cnt >= self.hold and self.handsdown:
            self.handsdown = False
            self.first = False
            self.do    = True    
            self.spread_time = 0
            # self.elbowstus['spread'] == False  

    def bodystraight(self, joints, kpm, th=12):
        """ check whether body is straight or not
        """
        torso_z = np.mean([joints[kpm.SpineBase_z], joints[kpm.SpineMid_z]])
        if torso_z-joints[kpm.Neck_z] > th and torso_z-joints[kpm.Head_z] > th:
        #    self.evalstr = 'please stand straight.'
           return False
        return True 

    def clasp(self, joints, kpm, spread_th=60, elbow_th=75):
        """ hands clasp state
        """ 
        if self.clasp_cnt == self.hold:
            self.elbowstus['clasp'] = False
            if not self.first:
                self.holdtime.append(self.spread_time/30.)
                self.cnt += 1
                if not self.elbowstus['spread']:
                    if self.spread_time < spread_th:
                        self.evalstr = 'Repitition done : Elbows should put behind your head long enough!!'
                        self.err.append('The '+self.cnvt.ordinal(self.cnt)+ \
                                        ' time spread is not good. elbows should behind your head long enough!!')
                    self.elbowstus['spread'] = True
                else:
                    self.evalstr = 'Repitition done: Spread well done'
                   

        if np.abs(joints[kpm.LElbow_x]-joints[kpm.RElbow_x]) < 75:
            self.elbowstus['clasp'] = True

    def spread(self, joints, kpm, spread_th=30):
        """ hands spread state
        """
        if self.spread_cnt == self.hold:
            self.elbowstus['spread'] = False
            if not self.elbowstus['clasp']:
                self.evalstr = 'Subsequence done: When raising the hands, elbows should close to each other.'
                self.err.append('The '+self.cnvt.ordinal(self.cnt)+ ' time clasp is not good. Not clasp !!')
                self.elbowstus['clasp'] = True
            else:                    
                self.evalstr = 'Subsequence done: Clasp well done'
                self.claspsuc += 1
        if (joints[kpm.LElbow_z]+joints[kpm.RElbow_z])/2 > joints[kpm.Head_z]:
            self.spread_time += 1
        if self.spread_time >= spread_th:
            self.elbowstus['spread'] = True

    def run(self, joints):
        """ Joint : denoised unified joint
        """
        if self.handsdown:
            # print 'hands down'
            self.clasp(joints, self.kpm)
        else:
            # print 'hands up'
            self.spread(joints, self.kpm)
            # self.bodystraight(joints, self.kpm)
        self.state_update(joints, self.kpm)

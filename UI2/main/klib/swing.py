import numpy as np
from math import acos
from scipy.signal import argrelextrema
from initial_param.kinect_para import Kinect_para
from scipy.ndimage.filters import gaussian_filter1d as gf
import inflect,pdb

class Swing(object):
    """
    """
    def __init__(self):
        # self.up      = False
        self.angle_mean = []
        self.angel_le   = []
        self.angel_re   = []
        self.bend_max   = []
        self.bend_min   = []
        self.cnvt       = inflect.engine()  # converting numerals into ordinals
        self.cnt_max_flag = False
        self.cnt_min_flag = False
        self.cnt_max = 0 
        self.cnt_min = 0
        self.max_ary = np.array([0, 0])
        self.min_ary = np.array([0, np.inf])
        self.max_len = 0
        self.min_len = 0
        self.bend_th = 8
        self.kpm     = Kinect_para()
        self.cnt     = 0
        self.evalstr = ''
        self.err     = []
        self.do      = False

    def vec_angle(self, vec1, vec2=np.array([1, 0, 0])):
        costheta = vec1.dot(vec2)/sum(vec1**2)**0.5/sum(vec2**2)**0.5
        return acos(costheta)*180/np.pi

    def body_angle(self, joints):
        angles = []
        for i in range(3):
            vec = joints[(i+1)*3:(i+2)*3] - joints[i*3:(i+1)*3]
            angles.append(self.vec_angle(vec))
        self.angle_mean.append(np.mean(angles))
        self.angel_le.append(self.vec_angle(joints[self.kpm.LElbow_x:self.kpm.LElbow_z+1] - joints[self.kpm.LShld_x:self.kpm.LShld_z+1],\
                                            joints[self.kpm.LElbow_x:self.kpm.LElbow_z+1] - joints[self.kpm.LWrist_x:self.kpm.LWrist_z+1]))
        self.angel_re.append(self.vec_angle(joints[self.kpm.RElbow_x:self.kpm.RElbow_z+1] - joints[self.kpm.RShld_x:self.kpm.RShld_z+1],\
                                            joints[self.kpm.RElbow_x:self.kpm.RElbow_z+1] - joints[self.kpm.RWrist_x:self.kpm.RWrist_z+1]))

    def local_minmax(self, seq, th, minmax, rng=30):
        angle_bending = gf(self.angle_mean, 15)
        pts = argrelextrema(angle_bending, minmax, order=rng)[0]
        if len(pts) != 0:

            if pts[-1] - seq[-1][0] >= rng and minmax(angle_bending[pts[-1]], th):
                seq = np.vstack((seq, np.array([pts[-1], angle_bending[pts[-1]]])))
            elif 0 < pts[-1]-seq[-1][0] < rng and minmax(angle_bending[pts[-1]], seq[-1][1]):
                seq[-1] = np.array([pts[-1], angle_bending[pts[-1]]])


        return np.atleast_2d(seq)

    def bending(self, joints, rng=30):   
        self.max_ary = self.local_minmax(self.max_ary, 90+self.bend_th, np.greater, rng)
        self.min_ary = self.local_minmax(self.min_ary, 90-self.bend_th, np.less, rng)
        if self.max_ary.shape[0] > self.max_len:
            self.cnt_max_flag = True
        if self.cnt_max_flag:
            self.cnt_max += 1
        if self.cnt_max == rng:
            self.cnt_max = 0
            self.cnt_max_flag = False
            self.evalstr = 'well done\n Next : bend to right\n'
            print ' ========  left  ========='
            self.cnt += 1
            # print ('bend to left  ' +str(self.max_ary[-1, 0])+'\n')
        if self.min_ary.shape[0] > self.max_len:
            self.cnt_min_flag = True
        if self.cnt_min_flag:
            self.cnt_min += 1
        if self.cnt_min == rng:
            self.cnt_min = 0
            self.cnt_min_flag = False
            self.evalstr = 'well done\n Next : bend to left\n'
            print ' ========  right  ========='
            self.cnt += 1
            # print 'bend to right ' +str(self.min_ary[-1, 0])+'\n'
        self.max_len = self.max_ary.shape[0]
        self.min_len = self.min_ary.shape[0]


    def detect_angle(self, angle, lr, rng=15, th=130):
        if len(angle) < rng:
            res = np.mean(angle)
        else:
            res = np.mean(angle[-rng:])
        # print res
        if res < th:
            if not 'Make your '+ lr +' arm straight.' in self.evalstr:
                self.evalstr += 'Make your '+ lr +' arm straight.\n'
            self.err.append(lr+' arm is not straight in '+self.cnvt.ordinal(int(np.ceil(self.cnt/2)))+' time bending.')

    def run(self, joints):
        self.body_angle(joints)
        self.bending(joints)
        self.detect_angle(self.angel_le, 'left')
        self.detect_angle(self.angel_re, 'right')

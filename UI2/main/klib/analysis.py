import numpy as np
from exercise import *
from dtw2 import Dynamic_time_warping
from breathstus import Breath_status
from handstatus import Hand_status
from shld_state import Shld_state
from clasp_spread import Clasp_spread
from initial_param.kinect_para import Kinect_para
from math import acos
import pdb

class Analysis(object):
    """ Analyze the exercise sequence 
    """
    def __init__(self):
        self.exer = {}
        self.exer[1] = Exer1()
        self.exer[2] = Exer2()
        self.exer[3] = Exer3()
        self.exer[4] = Exer4()
        self.exer[5] = Exer5()
        self.exer[6] = Exer6()
        self.exer[7] = Exer7()
        #
        self.dtw = Dynamic_time_warping()
        self.brth = Breath_status()
        self.hs = Hand_status()
        self.shld = Shld_state()
        self.clsp = Clasp_spread()
        self.kpm  = Kinect_para()
        #
        self.cnt = 0
        self.offset = 0
        self.do_once = False
        self._done = False
        self.offset = 0
        self.holdstate = True
        self.holdlist = np.array([])
        self.evalstr = ''

    def getcoord(self, data, order=[1, 4, 8, 20]):
        foo = []
        for i in order:
            if i == 1:
                foo = np.array([data[i].x, data[i].y])
            else:
                foo = np.vstack([foo, np.array([data[i].x, data[i].y])])
        return foo

    def joint_angle(self, joints, idx=[4, 5, 6]):
        """ finding the angle between 3 joints.
            default joints are left shld, elbow, wrist.
        """
        if joints.shape == 33:
            self.offset = 4

        vec1 = np.array([joints[self.offset+1*3+0]-joints[self.offset*3+0],\
                         joints[self.offset+1*3+1]-joints[self.offset*3+1],\
                         joints[self.offset+1*3+2]-joints[self.offset*3+2]])

        vec2 = np.array([joints[self.offset+1*3+0]-joints[self.offset+2*3+0],\
                         joints[self.offset+1*3+1]-joints[self.offset+2*3+1],\
                         joints[self.offset+1*3+2]-joints[self.offset+2*3+2]])

        costheta = vec1.dot(vec2)/sum(vec1**2)**.5/sum(vec2**2)**.5
        return acos(costheta)*180/np.pi

    def handpos(self, exer, joints, kpm, th=160, period=10, offeset=0):
        if joints.shape[0] == 21:
            offeset = 12
        exer.angle.append(self.joint_angle(joints))
        if len(exer.angle) < period:
            mean_angle = np.mean(exer.angle)
        else:
            mean_angle = np.mean(exer.angle[-10:])
        if mean_angle >= th:
            if joints[kpm.SpineMid_y-offeset] > joints[kpm.LWrist_y-offeset]\
                and joints[kpm.LElbow_y-offeset] > joints[kpm.LWrist_y-offeset]:
                return 'down'
            elif joints[kpm.LWrist_y-offeset] > joints[kpm.Head_y-offeset]: 
                return 'up'
            elif abs(joints[kpm.LWrist_y-offeset] - joints[kpm.LElbow_y-offeset]) < 20 and\
                 abs(joints[kpm.LWrist_y-offeset] - joints[kpm.LShld_y-offeset]) < 20:
                return 'horizontal'
        else:
            return 'belly'

    def run(self, exeno, reconJ, surface, evalinst, kp, body, dmap=[], djps=[]):
        if exeno == 1:
            
            if self.exer[1].cntdown <= 0:
                if self.offset == 0:
                    self.offset = kp.framecnt
                if len(self.holdlist) == 0:  # hand in the holding state or not
                    self.holdlist = reconJ
                else:
                    self.holdlist = np.vstack([self.holdlist, reconJ]) 
                    if np.sum(np.abs(self.holdlist[0]-self.holdlist[-1])[self.exer[1].jweight != 0]) > 400:
                        self.holdstate = False
                if self.holdstate: 
                    evalinst.blit_text(surface, exeno, kp, 'Starting breath in/out', 1, (255, 0, 0, 255))
                    bdry = self.getcoord(djps)
                    self.brth.breathextract(bdry, dmap)
                else:
                    if not self.do_once:
                        self.brth.breath_analyze(self.offset)
                        self.do_once = True
                        self._done = True
                        print('================= exe END ======================')            
            else:
                evalinst.blit_text(surface, self.exer[1].no, kp, 'Detection will starting after '\
                                   +str(np.round(self.exer[1].cntdown/30., 2))+' second', 1)
                self.exer[1].cntdown -= 1       
        elif exeno == 2:
            if self.exer[2].order[self.dtw.oidx] == [2]:
                if len(self.holdlist) == 0:  # hand in the holding state or not
                    self.holdlist = reconJ
                else:
                    self.holdlist = np.vstack([self.holdlist, reconJ]) 
                    if np.sum(np.abs(self.holdlist[0]-self.holdlist[-1])[self.exer[2].jweight != 0]) > 1000:
                        self.holdstate = False
                if self.holdstate:
                    evalinst.blit_text(surface, exeno, kp, 'Starting breath in (hand close) and breath out (hand open)', 1)
                    self.hs.hstus_proc(body.hand_left_state, body.hand_right_state)
                    bdry = self.getcoord(djps)
                    self.brth.breathextract(bdry, dmap)
                else:
                    if not self.do_once:
                        self.brth.breath_analyze()
                        hopen, hclose = self.hs.hstus_ana()
                        self.brth.brth_hand_sync(hopen, hclose) 
                        self.do_once = True                       
                    self.dtw.matching(reconJ, self.exer[2])
                    print('================= exe END ======================')
                    self._done = True
            else:
                self.dtw.matching(reconJ, self.exer[2])  
        elif exeno == 3:
            if not self.exer[3].order[self.dtw.oidx] == 'end':
                self.dtw.matching(reconJ, self.exer[3])
                if self.evalstr == '':
                    self.evalstr = self.dtw.evalstr
                    self.dtw.evalstr = ''
                if self.dtw.idxlist.count(3) > 4:
                    evalinst.blit_text(surface, exeno, kp,\
                                      'Only need to do 4 times', 3)
                    self.dtw.err.append('Only need to do 4 times')
                elif self.dtw.idxlist.count(3) > 0:
                   evalinst.blit_text(surface, exeno, kp,\
                                      str(4-min(self.dtw.idxlist.count(3), self.dtw.idxlist.count(4)))\
                                      + ' to go !!', 3, (55,173,245,255))          
            else:
                print('================= exe END ======================')
                self._done = True                
        elif exeno == 4:
            if not self.exer[4].order[self.dtw.oidx] == 'end':
                self.dtw.matching(reconJ, self.exer[4])
                if self.evalstr == '':
                    self.evalstr = self.dtw.evalstr
                    self.dtw.evalstr = ''
                if self.dtw.idxlist.count(3) > 4:
                    evalinst.blit_text(surface, exeno, kp,\
                                      'Only need to do 4 times', 3)
                    self.dtw.err.append('Only need to do 4 times')
                elif self.dtw.idxlist.count(3) > 0:
                   evalinst.blit_text(surface, exeno, kp,\
                                      str(4-min(self.dtw.idxlist.count(3), self.dtw.idxlist.count(4)))\
                                      + ' to go !!', 3, (55,173,245,255))
            else:
                print('================= exe END ======================')
                self._done = True
 
        elif exeno == 5:
            pass

        elif exeno == 6:
            if self.exer[6].cntdown <= 0:
                evalinst.blit_text(surface, exeno, kp, 'Start rotating your shoulders', 1)
                stus = self.handpos(self.exer[6], reconJ, self.kpm)
                if stus == 'belly':
                    self.shld.run(dmap, djps)
                    if self.evalstr == '':
                        self.evalstr = self.shld.evalstr
                        self.shld.evalstr = ''
                    self.exer[6].hraise = True
                elif stus == 'down':
                    print 'down'
                    if self.exer[6].hraise:
                        self._done = True
                if self.shld.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 times', 3)
                    self.shld.err.append('Only need to do 4 times')
                else:
                   evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.shld.cnt)),\
                                      3, (55,173,245,255)) 
            else:
                evalinst.blit_text(surface, self.exer[6].no, kp,\
                                  ('Detection will starting after %.2f second' % (self.exer[6].cntdown/30.)), 1)
                                   
                self.exer[6].cntdown -= 1
        elif exeno == 7:
            if self.exer[7].cntdown <= 0:
                evalinst.blit_text(surface, exeno, kp, 'Start to clasp and spread', 1)
                stus = self.handpos(self.exer[7], reconJ, self.kpm)
                if stus == 'down':
                    if self.clsp.do:
                        print self.cnt
                        if self.cnt > 90:
                            self._done = True
                        self.cnt += 1
                else:
                    self.cnt = 0
                    self.clsp.run(reconJ)
                    if self.evalstr == '':
                        self.evalstr = self.clsp.evalstr
                        self.clsp.evalstr = ''
                    
                if self.clsp.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 times', 3)
                    self.clsp.err.append('Only need to do 4 times')
                else:
                    evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.clsp.cnt)),\
                                        3, (55,173,245,255))
            else:
                evalinst.blit_text(surface, self.exer[7].no, kp,\
                                  ('Detection will starting after %.2f second' % (self.exer[7].cntdown/30.)), 1)
                self.exer[7].cntdown -= 1


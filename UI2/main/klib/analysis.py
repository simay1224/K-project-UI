import numpy as np
from exercise import *
from dtw2 import Dynamic_time_warping
from breathstus import Breath_status
from handstatus import Hand_status
from shld_state import Shld_state
from clasp_spread import Clasp_spread
from swing import Swing
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
        self.swing = Swing()
        self.kpm  = Kinect_para()
        #
        self.cnt = 0
        self.do_once = False
        self._done = False
        # self.offset = 0
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

    def joint_angle(self, joints, idx=[4, 5, 6], offset=0):
        """ finding the angle between 3 joints.
            default joints are left shld, elbow, wrist.
        """
        if joints.shape[0] == 33:
            offset = 4
        # Elbow - sholder
        vec1 = np.array([joints[(offset+1)*3+0]-joints[(offset*3)+0],\
                         joints[(offset+1)*3+1]-joints[(offset*3)+1],\
                         joints[(offset+1)*3+2]-joints[(offset*3)+2]])
        # Elbow - Wrist
        vec2 = np.array([joints[(offset+1)*3+0]-joints[(offset+2)*3+0],\
                         joints[(offset+1)*3+1]-joints[(offset+2)*3+1],\
                         joints[(offset+1)*3+2]-joints[(offset+2)*3+2]])

        costheta = vec1.dot(vec2)/sum(vec1**2)**.5/sum(vec2**2)**.5
        return acos(costheta)*180/np.pi

    def handpos(self, exer, joints, th=150, period=10, offeset=0):
        if joints.shape[0] == 21:
            offeset = 12
        exer.angle.append(self.joint_angle(joints))
        if len(exer.angle) < period:
            mean_angle = np.mean(exer.angle)
        else:
            mean_angle = np.mean(exer.angle[-10:])
        if mean_angle >= th:
            if joints[self.kpm.SpineMid_y-offeset] > joints[self.kpm.LWrist_y-offeset]\
                and joints[self.kpm.LElbow_y-offeset] > joints[self.kpm.LWrist_y-offeset]:
                return 'down'
            elif joints[self.kpm.LWrist_y-offeset] > joints[self.kpm.Head_y-offeset]:
                return 'up'
            elif abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset]) < 20 and\
                 abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LShld_y-offeset]) < 20:
                return 'horizontal'
        else:
            if joints[self.kpm.LWrist_y-offeset] > joints[self.kpm.Head_y-offeset]:
                return 'upnotstraight'
            else:
                if joints[self.kpm.LWrist_y-offeset] > joints[self.kpm.SpineBase_y-offeset]\
                   and joints[self.kpm.LElbow_y-offeset] > joints[self.kpm.LWrist_y-offeset]:
                   return 'belly'

    def run(self, exeno, reconJ, surface, evalinst, kp, body, dmap=[], djps=[]):
        if exeno == 1:
            if self.exer[1].cntdown <= 0:
                stus = self.handpos(self.exer[1], reconJ)
                if len(self.holdlist) == 0:  # hand in the holding state or not
                    self.holdlist = reconJ
                else:
                    self.holdlist = np.vstack([self.holdlist, reconJ])
                bdry = self.getcoord(djps)
                self.brth.run(bdry, dmap)
                if stus == 'down':
                    if self.brth.do:
                        if not self.do_once:
                            self.brth.breath_analyze()
                            self.do_once = True
                            self._done = True
                            print('================= exer END ======================')
                # === eval string update ===
                if self.evalstr == '':
                    self.evalstr = self.brth.evalstr
                    self.brth.evalstr = ''
                # === eval information ===
                if self.brth.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 times', 3)
                    evalinst.blit_text(surface, exeno, kp, 'Put down your hands', 1, (213, 23, 216, 255))
                    self.brth.err.append('Only need to do 4 times')
                elif self.brth.cnt == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Put down your hands', 1, (213, 23, 216, 255))
                else:
                    if self.brth.brth_out_flag:
                        evalinst.blit_text(surface, exeno, kp, 'Breathe out', 1, (255, 128, 0, 255))
                    else:
                        evalinst.blit_text(surface, exeno, kp, 'Breathe in', 1, (255, 128, 0, 255))
                    evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.brth.cnt)),\
                                       3, (55,173,245,255))            
            else:
                evalinst.blit_text(surface, self.exer[1].no, kp,\
                                   'Detection will starting after %.2f second' % (self.exer[1].cntdown/30.), 1)    
                self.exer[1].cntdown -= 1
       
        elif exeno == 2:
            stus = self.handpos(self.exer[2], reconJ)
            if stus == 'up':
                if len(self.holdlist) == 0:  # hand in the holding state or not
                    self.holdlist = reconJ
                else:
                    self.holdlist = np.vstack([self.holdlist, reconJ]) 
                self.hs.hstus_proc(body.hand_left_state, body.hand_right_state)
                bdry = self.getcoord(djps)
                self.brth.run(bdry, dmap)
                # === eval string update ===
                if self.evalstr == '':
                    self.evalstr = self.brth.evalstr
                    self.brth.evalstr = ''
                # === eval information ===
                if self.brth.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 times', 3)
                    evalinst.blit_text(surface, exeno, kp, 'Put down your hands', 1, (213, 23, 216, 255))
                    self.brth.err.append('Only need to do 4 times')
                elif self.brth.cnt == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Put down your hands', 1, (213, 23, 216, 255))
                else:
                    if self.brth.brth_out_flag:
                        evalinst.blit_text(surface, exeno, kp, 'Breathe in and close hand.', 1, (255, 128, 0, 255))
                    else:
                        evalinst.blit_text(surface, exeno, kp, 'Breathe out and open hand.', 1, (255, 128, 0, 255))
                    evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.brth.cnt)),\
                                        3, (55,173,245,255))
            elif stus == 'down':
                if self.brth.do:
                    if not self.do_once:
                        self.brth.breath_analyze()
                        hopen, hclose = self.hs.hstus_ana()
                        self.brth.brth_hand_sync(hopen, hclose) 
                        self.do_once = True
                        self._done = True
                        print('================= exer END ======================')
                else:
                    evalinst.blit_text(surface, exeno, kp, 'Please raise yours hands.', 1, (255, 128, 0, 255))

        elif exeno == 3:
            if not self.exer[3].order[self.dtw.oidx] == 'end':
                self.dtw.matching(reconJ, self.exer[3])
                # === eval string update ===
                if self.evalstr == '':
                    self.evalstr = self.dtw.evalstr
                    self.dtw.evalstr = ''
                # === eval information ===
                if self.dtw.idxlist.count(3) > 4:
                    evalinst.blit_text(surface, exeno, kp,\
                                      'Only need to do 4 times', 3)
                    self.dtw.err.append('Only need to do 4 times')
                    evalinst.blit_text(surface, exeno, kp, 'Put down your hands.', 1, (213, 23, 216, 255)) 
                elif self.dtw.idxlist.count(3) == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Put your hands down', 1, color=(213, 23, 216, 255))
                else:
                    evalinst.blit_text(surface, exeno, kp,\
                                      str(4-min(self.dtw.idxlist.count(3), self.dtw.idxlist.count(4)))\
                                      + ' to go !!', 3, (55,173,245,255))          
            else:
                self._done = True
                print('================= exer END ======================')
                
                
        elif exeno == 4:
            if not self.exer[4].order[self.dtw.oidx] == 'end':
                self.dtw.matching(reconJ, self.exer[4])
                # === eval string update ===
                if self.evalstr == '':
                    self.evalstr = self.dtw.evalstr
                    self.dtw.evalstr = ''
                # === eval information ===
                if self.dtw.idxlist.count(3) > 4:
                    evalinst.blit_text(surface, exeno, kp,'Only need to do 4 times', 3)
                    evalinst.blit_text(surface, exeno, kp, 'Put your hands down', 1, color=(213, 23, 216, 255))
                    self.dtw.err.append('Only need to do 4 times')
                elif self.dtw.idxlist.count(3) == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Put your hands down', 1, color=(213, 23, 216, 255))    
                else:
                   evalinst.blit_text(surface, exeno, kp,\
                                      str(4-min(self.dtw.idxlist.count(3), self.dtw.idxlist.count(4)))\
                                      + ' to go !!', 3, (55,173,245,255))
            else:
                self._done = True
                print('================= exer END ======================')
                
        elif exeno == 5:
            stus = self.handpos(self.exer[5], reconJ)
            if stus == 'up':
                self.swing.do = True
                self.swing.run(reconJ)
            elif stus == 'down':
                if self.swing.do:
                    if self.cnt > 90:
                        self._done = True
                        print('================= exer END ======================')
                    self.cnt += 1
            # === eval string update ===
            if self.evalstr == '':
                self.evalstr = self.swing.evalstr
                self.swing.evalstr = ''            
            # === eval information ===
            if self.swing.cnt/2 > 4:
                evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 times', 3)
                evalinst.blit_text(surface, exeno, kp, 'Put your hands down', 1, color=(213, 23, 216, 255))
                self.swing.err.append('Only need to do 4 times')
            elif self.swing.cnt/2 == 4:
                evalinst.blit_text(surface, exeno, kp, 'Put your hands down', 1, color=(213, 23, 216, 255))
            else:
                if self.swing.bend_left:
                    evalinst.blit_text(surface, exeno, kp, 'Bending to your left', 1, color=(255, 128, 0, 255))
                else:
                    evalinst.blit_text(surface, exeno, kp, 'Bending to your right', 1, color=(255, 128, 0, 255))                
                evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.swing.cnt/2)),\
                                    3, (55,173,245,255))             

        elif exeno == 6:
            if self.exer[6].cntdown <= 0:
                stus = self.handpos(self.exer[6], reconJ)
                if stus == 'belly':
                    self.shld.run(dmap, djps)
                    self.exer[6].hraise = True
                elif stus == 'down':
                    if self.exer[6].hraise:
                        self._done = True
                        print('================= exer END ======================')
                # === eval string update ===
                if self.evalstr == '':
                    self.evalstr = self.shld.evalstr
                    self.shld.evalstr = ''
                # === eval information ===
                if self.shld.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 times', 3)
                    evalinst.blit_text(surface, exeno, kp, 'Put your hands down', 1, color=(213, 23, 216, 255))
                    self.shld.err.append('Only need to do 4 times')
                elif self.shld.cnt == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Put your hands down', 1, color=(213, 23, 216, 255))
                else:
                    evalinst.blit_text(surface, exeno, kp, 'Start rotating your shoulders', 1)
                    evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.shld.cnt)),\
                                      3, (55,173,245,255)) 
            else:
                evalinst.blit_text(surface, self.exer[6].no, kp,\
                                  ('Detection will starting after %.2f second' % (self.exer[6].cntdown/30.)), 1) 
                self.exer[6].cntdown -= 1

        elif exeno == 7:
            if self.exer[7].cntdown <= 0:
                stus = self.handpos(self.exer[7], reconJ)
                if stus == 'down':
                    if self.clsp.do:
                        if self.cnt > 90:
                            self._done = True
                            print('================= exer END ======================')
                        self.cnt += 1
                else:
                    self.cnt = 0
                    self.clsp.run(reconJ)
                # === eval string update ===
                if self.evalstr == '':
                    self.evalstr = self.clsp.evalstr
                    self.clsp.evalstr = ''
                # === eval information ===    
                if self.clsp.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 times', 3)
                    evalinst.blit_text(surface, exeno, kp, 'Put your hands down', 1, color=(213, 23, 216, 255))
                    self.clsp.err.append('Only need to do 4 times')
                elif self.shld.cnt == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Put your hands down', 1, color=(213, 23, 216, 255))
                else:
                    evalinst.blit_text(surface, exeno, kp, 'Start to clasp and spread', 1)
                    evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.clsp.cnt)),\
                                        3, (55,173,245,255))
            else:
                evalinst.blit_text(surface, self.exer[7].no, kp,\
                                  ('Detection will starting after %.2f second' % (self.exer[7].cntdown/30.)), 1)
                self.exer[7].cntdown -= 1


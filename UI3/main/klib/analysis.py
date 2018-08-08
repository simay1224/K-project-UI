import numpy as np
from .exercise import *
from .analysis_helper.dtw2 import Dynamic_time_warping
from .analysis_helper.breathstus import Breath_status
from .analysis_helper.handstatus import Hand_status
from .analysis_helper.shld_state import Shld_state
from .analysis_helper.clasp_spread import Clasp_spread
from .analysis_helper.horzp import Horzp
from .analysis_helper.pushdp import Pushdp
from .analysis_helper.swing import Swing
from .initial_param.kinect_para import Kinect_para
from .initial_param.kparam      import Kparam
from math import acos
import inflect
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
        self.kpm = Kinect_para()
        self.horzp = Horzp()
        self.pushdp = Pushdp()
        #
        self.cnvt = inflect.engine()  # converting numerals into ordinals
        self.cnt = 0
        self.repcnt = 0  # repetition counts
        self.do_once = False
        self._done = False
        self.jointslist = np.array([])
        self.evalstr = ''
        # default color
        self.kp = Kparam()
        self.c_togo     = self.kp.c_togo
        self.c_handdown = self.kp.c_guide
        self.c_normal   = self.kp.c_eval_well
        self.c_err      = self.kp.c_eval_err

    def getcoord(self, data, order=[1, 4, 8, 20]):
        """ get the coordinate of the chest region
            return : [[spinmid_x, spinmid_y],
                      [Lshlder_x, Lshlder_y],
                      [Rshlder_x, Rshlder_y],
                      [Sshlder_x, Sshlder_y]]  datatype: np.array
        """
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
        # 11 joints are useful, each has 3 coordinates
        if joints.shape[0] == 33:
            offset = 4
        # Elbow - sholder
        vec1 = np.array([joints[(offset+1)*3+0]-joints[(offset*3)+0],
                         joints[(offset+1)*3+1]-joints[(offset*3)+1],
                         joints[(offset+1)*3+2]-joints[(offset*3)+2]])
        # Elbow - Wrist
        vec2 = np.array([joints[(offset+1)*3+0]-joints[(offset+2)*3+0],
                         joints[(offset+1)*3+1]-joints[(offset+2)*3+1],
                         joints[(offset+1)*3+2]-joints[(offset+2)*3+2]])

        costheta = vec1.dot(vec2)/sum(vec1**2)**.5/sum(vec2**2)**.5
        return acos(costheta)*180/np.pi

    def handpos(self, exer, joints, th=160, period=10, offeset=0):
        """ According to the relative position between arms and other joints
            decide the arms' status
        """
        if joints.shape[0] == 21:
            offeset = 12
        exer.angle.append(self.joint_angle(joints))
        if len(exer.angle) < period:
            mean_angle = np.mean(exer.angle)
        else:
            mean_angle = np.mean(exer.angle[-10:])
        if mean_angle >= th:
            if (joints[self.kpm.SpineMid_y-offeset] > joints[self.kpm.LWrist_y-offeset] and
                (joints[self.kpm.LElbow_y-offeset] - joints[self.kpm.LWrist_y-offeset]) > 80 and
                (joints[self.kpm.LShld_y-offeset] - joints[self.kpm.LWrist_y-offeset]) > 100):
                return 'down'
            elif joints[self.kpm.LWrist_y-offeset] > joints[self.kpm.Head_y-offeset]:
                return 'up'
            elif (abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset]) < 20 and
                  abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LShld_y-offeset]) < 20):
                return 'horizontal'
        else:
            if joints[self.kpm.LWrist_y-offeset] > joints[self.kpm.Head_y-offeset]:
                return 'upnotstraight'
            else:
                if (abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset]) < 30 and
                    abs(joints[self.kpm.LElbow_y-offeset] - joints[self.kpm.LShld_y-offeset]) < 20):
                    return 'horizontal_bend'
                if (abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset]) > 80 and
                    abs(joints[self.kpm.LShld_y-offeset] - joints[self.kpm.LElbow_y-offeset]) > 80 and
                    abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LShld_y-offeset]) < 20):
                    return 'vshape'
                if (joints[self.kpm.LWrist_y-offeset] > joints[self.kpm.SpineBase_y-offeset] and
                    joints[self.kpm.LElbow_y-offeset] > joints[self.kpm.LWrist_y-offeset]):
                    return 'belly'

    def bodystraight(self, joints, th=30):
        """ check whether body is straight or not
        """
        torso_z = np.mean([joints[self.kpm.SpineBase_z], joints[self.kpm.SpineMid_z]])
        if torso_z-joints[self.kpm.Neck_z] > th and torso_z-joints[self.kpm.Head_z] > th:
            if 'Well done.' in self.evalstr:
                self.evalstr = self.evalstr.replace('Well done.', '')
            self.evalstr += 'please stand straight.'

    def run(self, exeno, reconJ, surface, evalinst, kp, body, dmap=[], djps=[]):
        """ analysis main function
        """

        if not self.kp.kinect:
            stus = "up"
            self.evalstr = "not possible"
            self._done = True
            kp.finish = True
            self.brth.cnt = 6


        if self.kp.kinect and self.exer[exeno].limbjoints:
            reconJ21 = reconJ[12:]

        if exeno == 1:
            if self.exer[1].cntdown <= 0:
                if self.kp.kinect:
                    stus = self.handpos(self.exer[1], reconJ21)
                if stus != 'down':
                    if len(self.jointslist) == 0:  # store joints information
                        self.jointslist = reconJ21
                    else:
                        self.jointslist = np.vstack([self.jointslist, reconJ21])
                    bdry = self.getcoord(djps)
                    self.brth.run(bdry, dmap)
                    if 'stand' not in self.evalstr:
                        self.bodystraight(reconJ)
                elif stus == 'down':
                    if self.brth.do:
                        if not self.do_once:
                            self.brth.breath_analyze()
                            self.do_once = True
                            self._done = True
                            if self.brth.cnt < 4:
                                self.brth.err.append('Make sure you do 4 repetitions.')
                                self.brth.errsum.append('Make sure you do 4 repetitions.')
                            print('================= exer END ======================')
                # self.eval_common(surface, exeno, kp)
                # === eval string update ===
                if self.evalstr == '':
                    self.evalstr = self.brth.evalstr
                    self.brth.evalstr = ''
                # === eval information ===
                if self.brth.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2 ,color=self.c_err)
                    self.brth.err.append('Only need to do 4 repetitions')
                    self.brth.errsum.append('Only need to do 4 repetitions')
                elif self.brth.cnt == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_handdown)
                else:
                    if self.brth.brth_out_flag:
                        evalinst.blit_text(surface, exeno, kp, 'Breathe out', 2, color=self.c_normal)
                    else:
                        evalinst.blit_text(surface, exeno, kp, 'Breathe in', 2, color=self.c_normal)
                    evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.brth.cnt)),
                                       4, color=self.c_togo)
                self.repcnt = self.brth.cnt
            else:
                evalinst.blit_text(surface, self.exer[1].no, kp,
                                   'Starting after %.2f second' % (self.exer[1].cntdown/30.), 2)
                self.exer[1].cntdown -= 1

        elif exeno == 2:
            if self.kp.kinect:
                stus = self.handpos(self.exer[2], reconJ21)
            if stus == 'up' or stus == 'upnotstraight':
                if self.kp.kinect:
                    if len(self.jointslist) == 0:  # store joints information
                        self.jointslist = reconJ21
                    else:
                        self.jointslist = np.vstack([self.jointslist, reconJ21])
                    self.hs.hstus_proc(body.hand_left_state, body.hand_right_state)
                    bdry = self.getcoord(djps)
                    self.brth.run(bdry, dmap)
                    if 'stand' not in self.evalstr:
                        self.bodystraight(reconJ)
                # === eval string update ===
                if self.evalstr == '':
                    self.evalstr = self.brth.evalstr
                    self.brth.evalstr = ''
                # === eval information ===
                if self.brth.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, True, color=self.c_err)
                    self.brth.err.append('Only need to do 4 repetitions.')
                    self.brth.errsum.append('Only need to do 4 repetitions.')
                elif self.brth.cnt == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, True, color=self.c_handdown)
                else:
                    if stus == 'upnotstraight':
                        evalinst.blit_text(surface, exeno, kp, 'Please make sure that your arms are straight.', 2, True, color=self.c_err)
                        self.brth.err.append('Please make sure that your arms are straight at %s repetition.'
                                              % self.cnvt.ordinal(self.brth.cnt+1))
                        self.brth.errsum.append('Please make sure that your arms are straight when breathing.')
                    else:
                        if not self.brth.brth_out_flag:
                            evalinst.blit_text(surface, exeno, kp, 'Breathe in and close your hands.', 2, True, color=self.c_normal)
                        else:
                            evalinst.blit_text(surface, exeno, kp, 'Breathe out and open your hands.', 2, True, color=self.c_normal)
                    evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.brth.cnt)), 4, color=self.c_togo)
                self.repcnt = self.brth.cnt
            elif stus == 'down':
                if self.brth.do:
                    if not self.do_once:
                        self.brth.breath_analyze()
                        hopen, hclose = self.hs.hstus_ana()
                        self.brth.brth_hand_sync(hopen, hclose)
                        self.do_once = True
                        self._done = True
                        if self.brth.cnt < 4:
                            self.brth.err.append('Make sure you do 4 repetitions.')
                            self.brth.errsum.append('Make sure you do 4 repetitions.')
                        print('================= exer END ======================')
                else:
                    evalinst.blit_text(surface, exeno, kp, 'Please raise yours arms.', 2, color=self.c_normal)

        elif exeno == 3:
            if self.kp.kinect:
                stus = self.handpos(self.exer[3], reconJ)
            if stus == 'up':
                self.pushdp.do = True
            elif stus == 'down':
                if self.pushdp.do:
                    self._done = True
                    if self.pushdp.cnt  < 4:
                        self.pushdp.err.append('Make sure you do 4 repetitions.')
                        self.pushdp.errsum.append('Make sure you do 4 repetitions.')
                    print('================= exer END ======================')
                else:
                    evalinst.blit_text(surface, exeno, kp, 'Please raise yours arms.', 2, color=self.c_normal)
            if self.pushdp.do:
                if self.kp.kinect:
                    self.pushdp.run(reconJ, stus)
                if 'stand' not in self.evalstr:
                    if self.kp.kinect:
                        self.bodystraight(reconJ)
                if self.evalstr == '':
                    self.evalstr = self.pushdp.evalstr
                    self.pushdp.evalstr = ''
                if self.pushdp.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_err)
                    self.pushdp.err.append('Only need to do 4 repetitions.')
                    self.pushdp.errsum.append('Only need to do 4 repetitions.')
                elif self.pushdp.cnt == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_handdown)
                else:
                    if stus == 'up':
                        evalinst.blit_text(surface, exeno, kp, 'Push down you arms', 2, color=self.c_normal)
                    elif stus == 'upnotstraight':
                        evalinst.blit_text(surface, exeno, kp, 'Please straighten your arms', 2, color=self.c_err)
                    elif stus == 'vshape':
                        evalinst.blit_text(surface, exeno, kp, 'Raise up your arms', 2, color=self.c_normal)
                    evalinst.blit_text(surface, exeno, kp, '%s to go !!' %str(4-self.pushdp.cnt),
                                        4, color=self.c_togo)
                self.repcnt = self.pushdp.cnt

        elif exeno == 4:
            if self.kp.kinect:
                stus = self.handpos(self.exer[4], reconJ)
            if stus == 'horizontal' or stus == 'horizontal_bend':  # T-pose
                if self.kp.kinect:
                    self.horzp.do = True
                    self.horzp.run(reconJ)
                    if 'stand' not in self.evalstr:
                        self.bodystraight(reconJ)
            elif stus == 'down':
                if self.horzp.do:
                    self._done = True
                    if self.horzp.cnt  < 4:
                        self.horzp.err.append('Make sure you do 4 repetitions.')
                        self.horzp.errsum.append('Make sure you do 4 repetitions.')
                    print('================= exer END ======================')
                else:
                    evalinst.blit_text(surface, exeno, kp, 'Please raise yours arms.', 2, color=self.c_normal)
            if self.horzp.do:
                if self.evalstr == '':
                    self.evalstr = self.horzp.evalstr
                    self.horzp.evalstr = ''
                if self.horzp.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_err)
                    self.horzp.err.append('Only need to do 4 repetitions.')
                    self.horzp.errsum.append('Only need to do 4 repetitions.')
                elif self.horzp.cnt == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_handdown)
                else:
                    if stus == None and self.repcnt < 4 :
                        evalinst.blit_text(surface, exeno, kp, 'Please keep your arms horizontally.', 2, color=self.c_err)
                        # self.horzp.evalstr = 'Please keep your arms horizontally.'
                        # self.horzp.eval = 'Please keep your arms horizontally.'
                        self.horzp.err.append('The '+self.cnvt.ordinal(self.repcnt+1)+ ' time try, please keep your arms horizontally.')
                        self.horzp.errsum.append('Please keep your arms horizontally.')
                    elif self.horzp.state == 'T-pose':
                        evalinst.blit_text(surface, exeno, kp, 'Please close your arms to your chest', 2, color=self.c_normal)
                    elif self.horzp.state == 'chest':
                        evalinst.blit_text(surface, exeno, kp, 'Please open your arms to T-pose', 2, color=self.c_normal)
                    evalinst.blit_text(surface, exeno, kp, '%s to go !!' %str(4-self.horzp.cnt),
                                        4, color=self.c_togo)
                self.repcnt = self.horzp.cnt

        elif exeno == 5:
            if self.kp.kinect:
                stus = self.handpos(self.exer[5], reconJ)
            if stus == 'up':
                if self.kp.kinect:
                    self.swing.do = True
                    self.swing.run(reconJ)
                    if 'stand' not in self.evalstr:
                        self.bodystraight(reconJ)
            elif stus == 'down':
                if self.swing.do:
                    if self.cnt > 90:
                        self._done = True
                        if (self.swing.cnt >>1) < 4:
                            self.swing.err.append('Make sure you do 4 repetitions.')
                            self.swing.errsum.append('Make sure you do 4 repetitions.')
                        print('================= exer END ======================')
                    self.cnt += 1
            # === eval string update ===
            if self.evalstr == '':
                self.evalstr = self.swing.evalstr
                self.swing.evalstr = ''
            # === eval information ===
            if self.swing.cnt/2 > 4:
                evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_err)
                self.swing.err.append('Only need to do 4 repetitions')
                self.swing.errsum.append('Only need to do 4 repetitions.')
            elif self.swing.cnt/2 == 4:
                evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_handdown)
            else:
                if self.swing.bend_left:
                    evalinst.blit_text(surface, exeno, kp, 'Please bend to your left', 2, color=self.c_normal)
                else:
                    evalinst.blit_text(surface, exeno, kp, 'Please bend to your right', 2, color=self.c_normal)
                evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.swing.cnt/2)), 4, color=self.c_togo)
            self.repcnt = self.swing.cnt/2

        elif exeno == 6:
            if self.exer[6].cntdown <= 0:
                if self.kp.kinect:
                    stus = self.handpos(self.exer[6], reconJ)
                if stus == 'belly':
                    self.cnt = 0
                    if self.kp.kinect:
                        self.shld.run(dmap, djps)
                    # self.exer[6].hraise = True
                elif stus == 'down':
                    if self.shld.do:
                        if self.cnt > 60:
                            self._done = True
                            if self.shld.cnt < 4:
                                self.shld.err.append('Make sure you do 4 repetitions.')
                                self.shld.errsum.append('Make sure you do 4 repetitions.')
                            print('================= exer END ======================')
                        self.cnt += 1
                # === eval string update ===
                if self.evalstr == '':
                    self.evalstr = self.shld.evalstr
                    self.shld.evalstr = ''
                # === eval information ===
                if self.shld.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_err)
                    self.shld.err.append('Only need to do 4 repetitions')
                    self.shld.errsum.append('Only need to do 4 repetitions')
                elif self.shld.cnt == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_handdown)
                else:
                    evalinst.blit_text(surface, exeno, kp, 'Start rotating your shoulders', 2, color=self.c_normal)
                    evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.shld.cnt)), 4, color=self.c_togo)
                self.repcnt = self.shld.cnt
            else:
                evalinst.blit_text(surface, self.exer[6].no, kp,
                                  ('Starting after %.2f second' % (self.exer[6].cntdown/30.)), 2,
                                  color=self.c_normal)
                self.exer[6].cntdown -= 1

        elif exeno == 7:
            if self.exer[7].cntdown <= 0:
                if self.kp.kinect:
                    stus = self.handpos(self.exer[7], reconJ)
                if stus == 'down':
                    if self.clsp.do:
                        if self.cnt > 90:
                            self._done = True
                            if self.clsp.cnt < 4:
                                self.clsp.err.append('Make sure you do 4 repetitions.')
                                self.clsp.errsum.append('Make sure you do 4 repetitions.')
                            print('================= exer END ======================')
                        self.cnt += 1
                else:
                    self.cnt = 0
                    if self.kp.kinect:
                        self.clsp.run(reconJ)
                # === eval string update ===
                if self.evalstr == '':
                    self.evalstr = self.clsp.evalstr
                    self.clsp.evalstr = ''
                # === eval information ===
                if self.clsp.cnt > 4:
                    evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_err)
                    self.clsp.err.append('Only need to do 4 repetitions')
                    self.clsp.errsum.append('Only need to do 4 repetitions')
                elif self.clsp.cnt == 4:
                    evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_handdown)
                else:
                    if self.clsp.mode == 'clasp':
                        evalinst.blit_text(surface, exeno, kp, 'Start to clasp', 2, color=self.c_normal)
                    else:   #ana.clasp.mode == 'spread'
                        evalinst.blit_text(surface, exeno, kp, 'Start to spread', 2, color=self.c_normal)
                    evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.clsp.cnt)), 4, color=self.c_togo)
                self.repcnt = self.clsp.cnt
            else:
                evalinst.blit_text(surface, self.exer[7].no, kp,
                                  ('Starting after %.2f second' % (self.exer[7].cntdown/30.)), 2,
                                  color=self.c_normal)
                self.exer[7].cntdown -= 1

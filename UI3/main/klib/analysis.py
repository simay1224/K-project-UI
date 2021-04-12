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
        #self.exer[5] = Exer5()
        #self.exer[6] = Exer6()
        #self.exer[7] = Exer7()

        #hiding the exercise 5
        self.exer[5] = Exer5()
        self.exer[6] = Exer6()

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
        self.evalstr = ''  #will be immediate feedback or each frame
        # default color
        self.kp = Kparam()
        self.c_togo     = self.kp.c_togo
        self.c_handdown = self.kp.c_guide
        self.c_normal   = self.kp.c_eval_well
        self.c_err      = self.kp.c_eval_err
        self.c_stop     = self.kp.c_stop
        #
        self.ongoing_cycle = True
        self.screen_message = ''
        # boolean that becomes True when the cue is dettected in each exercise and analysis start to run
        self.exercise_started = False 
        # boolean that becomes True when the start button is pressed and data starts to be interpreted
        self.exercise_initialized = False
        self.paused = False
        #
        self.stus_lst = []
        self.wr_shld= []
        self.wr_elb = []

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

    def handpos(self, exer, joints, th=140, period=10, offeset=0): #th is originally 160, 70 % of it is 112, 60% is 96
        """ 
            According to the relative position between arms and other joints
            decide the arms' status
        """
        if joints.shape[0] == 21:
            offeset = 12
        exer.angle.append(self.joint_angle(joints))
        if len(exer.angle) < period:
            mean_angle = np.mean(exer.angle)
        else:
            mean_angle = np.mean(exer.angle[-10:])
            #print("differences")
            #print(joints[self.kpm.LElbow_y-offeset] - joints[self.kpm.LWrist_y-offeset])
            #print(joints[self.kpm.LShld_y-offeset] - joints[self.kpm.LWrist_y-offeset])
        if mean_angle >= th:
            #print('\n\n')
            #self.stus_lst.append('wrist - elbow:')
            #self.screen_message = ''
            #self.screen_message += str(abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset])) + ' '+ str(abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LShld_y-offeset]))
            self.wr_elb.append(abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset])) #20 ish
            #self.stus_lst.append('wrist - spine shoulder:')
            self.wr_shld.append( abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LShld_y-offeset])) #spine: 40 ish
            #self.screen_message += '\n'+str(abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset])) + ''+ str(abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.SpineShld_y-offeset]))
            #(abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset]) < 20 and
            #      abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.SpineShld_y-offeset]) < 20)
            if (joints[self.kpm.SpineMid_y-offeset] > joints[self.kpm.LWrist_y-offeset] and
                (joints[self.kpm.LElbow_y-offeset] - joints[self.kpm.LWrist_y-offeset]) > 80 and
                (joints[self.kpm.LShld_y-offeset] - joints[self.kpm.LWrist_y-offeset]) > 100):
                 # was 80 and 100
                return 'down'
            elif joints[self.kpm.LWrist_y-offeset] > joints[self.kpm.Head_y-offeset]:
                return 'up'
            #original
            #elif (abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset]) < 20 and
            #      abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LShld_y-offeset]) < 20): 
                  # was 20 and 20
                #return 'horizontal'
            elif (abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset]) < 50 and
                  abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LShld_y-offeset]) < 50): 
                return 'horizontal'
        else:
            if joints[self.kpm.LWrist_y-offeset] > joints[self.kpm.Head_y-offeset]: 
                print('up not straight', joints[self.kpm.LWrist_y-offeset], joints[self.kpm.Head_y-offeset])
                return 'upnotstraight'
            else:
                if (abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset]) < 50  and
                    abs(joints[self.kpm.LElbow_y-offeset] - joints[self.kpm.LShld_y-offeset]) < 50):
                    # was 30 and 20
                    return 'horizontal_bend'
                if (abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LElbow_y-offeset]) > 80 and
                    abs(joints[self.kpm.LShld_y-offeset] - joints[self.kpm.LElbow_y-offeset]) > 80 and
                    abs(joints[self.kpm.LWrist_y-offeset] - joints[self.kpm.LShld_y-offeset]) < 20):
                    # was 80, 80, and 20
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
            if self.exercise_initialized :
                if not self.paused:
                    if self.exer[1].cntdown <= 0:
                        if self.kp.kinect:
                            stus = self.handpos(self.exer[1], reconJ21) # originally there was no threshold
                        print(stus)
                        if stus != 'down': # was stus != 'down'
                            #if stus == 'belly':
                            #    self.cnt = 0
                            if len(self.jointslist) == 0:  # store joints information
                                self.jointslist = reconJ21
                            else:
                                self.jointslist = np.vstack([self.jointslist, reconJ21])
                            bdry = self.getcoord(djps)
                            self.brth.run(bdry, dmap)
                            self.exercise_started = True
                            if 'stand' not in self.evalstr:
                                self.bodystraight(reconJ)
                        elif stus == 'down':
                            if self.brth.do:
                                if not self.do_once:
                                    self.brth.breath_analyze()
                                    print('###'*100)
                                    self.do_once = True
                                    #if self.cnt > 5:
                                    self._done = True
                                    if self.brth.cnt < 4:
                                        self.brth.err.append('Make sure you do 4 repetitions.')
                                        self.brth.errsum.append('Make sure you do 4 repetitions.')
                                    print('================= exer END ======================')
                                    #self.cnt += 1
                        # self.eval_common(surface, exeno, kp)
                        # === eval string update ===
                        #if self.evalstr == '':
                        #    self.evalstr = self.brth.evalstr
                        #    self.brth.evalstr = ''
                        self.evalstr = self.brth.evalstr  #evalstr gets updated immediately
                        #if 'well' in self.evalstr.lower(): #if it says well done, display immediately
                        #    evalinst.blit_text(surface, exeno, kp, 'Repetetion well done', 2 ,color=self.c_stop)

                        if self.screen_message == '': #and self.shld.ongoing_cycle:
                            #if 'done' in self.brth.evalstr.lower(): #added now
                            self.screen_message = self.brth.evalstr  # screen message gets the display message
                        self.brth.evalstr = ''
                        # update ongoing cycle
                        self.ongoing_cycle = self.brth.ongoing_cycle
                        # === eval information ===
                        if self.brth.cnt > 4:
                            # evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                            evalinst.blit_text(surface, exeno, kp, 'Done! Please push down your arms', 2 ,color=self.c_stop) # was c_err
                            #self.brth.err.append('Only need to do 4 repetitions')
                            #self.brth.errsum.append('Only need to do 4 repetitions')
                        elif self.brth.cnt == 4:
                            evalinst.blit_text(surface, exeno, kp, 'Done! Please push down your arms', 2, color=self.c_stop)
                        else:
                            if self.brth.brth_out_flag:
                                if self.screen_message == '':
                                    self.screen_message = 'Breathe out and relax'
                                #evalinst.blit_text(surface, exeno, kp, 'Breathe out', 2, color=self.c_normal)
                            else:
                                if self.screen_message == '':
                                    print("ctndwn is", self.exer[1].cntdown )
                                    self.screen_message = 'Breathe in while opening your chest'
                                #evalinst.blit_text(surface, exeno, kp, 'Breathe in', 2, color=self.c_normal)
                            evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.brth.cnt)),
                                            4, color=self.c_togo)
                        self.repcnt = self.brth.cnt
                    else:
                        #evalinst.blit_text(surface, self.exer[1].no, kp,
                        #                'Starting after %.2f second' % (self.exer[1].cntdown/30.), 2)
                        self.exer[1].cntdown -= 1
                else:
                   evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Continue to continue', 2) 
            else:
                evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Start to begin', 2)

        elif exeno == 2:
            if self.exercise_initialized:
                if not self.paused:
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
                            self.exercise_started = True
                            if 'stand' not in self.evalstr:
                                self.bodystraight(reconJ)
                        # === eval string update ===
                        #if self.evalstr == '':
                        #    self.evalstr = self.brth.evalstr
                        #    self.brth.evalstr = ''
                        self.evalstr = self.brth.evalstr  #evalstr gets updated immediately
                        if self.screen_message == '': #and self.shld.ongoing_cycle:
                            self.screen_message = self.brth.evalstr # screen message gets the display message
                        self.brth.evalstr = ''
                        # update ongoing cycle
                        self.ongoing_cycle = self.brth.ongoing_cycle
                        # === eval information ===
                        if self.brth.cnt > 4:
                            # evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                            evalinst.blit_text(surface, exeno, kp, 'Done! Please push down your arms', 2, True, color=self.c_stop)
                            #self.brth.err.append('Only need to do 4 repetitions.')
                            #self.brth.errsum.append('Only need to do 4 repetitions.')
                        elif self.brth.cnt == 4:
                            evalinst.blit_text(surface, exeno, kp, 'Done! Please push down your arms', 2, True, color=self.c_stop)
                        else:
                            if stus == 'upnotstraight':
                                if self.screen_message == '':
                                    self.screen_message = 'Please make sure that your arms are straight.'
                                #evalinst.blit_text(surface, exeno, kp, 'Please make sure that your arms are straight.', 2, True, color=self.c_err)
                                self.brth.err.append('Please make sure that your arms are straight at %s repetition.'
                                                    % self.cnvt.ordinal(self.brth.cnt+1))
                                self.brth.errsum.append('Please make sure that your arms are straight when breathing.')
                            else:
                                if not self.brth.brth_out_flag:
                                    if self.screen_message == '':
                                        self.screen_message = 'Make a fist while breathing in'
                                    #evalinst.blit_text(surface, exeno, kp, 'Breathe in and close your hands.', 2, True, color=self.c_normal)
                                else:
                                    if self.screen_message == '':
                                        self.screen_message = 'Open your hands while breathing out, relax your muscles'
                                    #evalinst.blit_text(surface, exeno, kp, 'Breathe out and open your hands.', 2, True, color=self.c_normal)
                            evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.brth.cnt)), 4, color=self.c_togo)
                        self.repcnt = self.brth.cnt
                    elif stus == 'down':
                        if self.brth.do:
                            if not self.do_once:
                                self.brth.breath_analyze()
                                hopen, hclose = self.hs.hstus_ana()
                                if len(hopen) == 0 or len(hclose)==0:
                                    pass
                                else:
                                    self.brth.brth_hand_sync(hopen, hclose)
                                self.do_once = True
                                self._done = True
                                if self.brth.cnt < 4:
                                    self.brth.err.append('Make sure you do 4 repetitions.')
                                    self.brth.errsum.append('Make sure you do 4 repetitions.')
                                print('================= exer END ======================')
                        else:
                            #pass
                            if self.cnt >=90:
                                evalinst.blit_text(surface, exeno, kp, 'Please raise your arms.', 2, color=self.c_normal)
                            self.cnt +=1
                else:#if paused
                    evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Continue to continue', 2)
            else:
                evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Start to begin', 2)
        elif exeno == 3:
            if self.exercise_initialized:
                print(self.cnt)
                if not self.paused:
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
                            print("self count is" ,self.cnt)
                            if self.cnt >=90:
                                evalinst.blit_text(surface, exeno, kp, 'Please raise yours arms.', 2, color=self.c_normal)
                            self.cnt +=1
                    if self.pushdp.do:
                        if self.kp.kinect:
                            self.pushdp.run(reconJ, stus)
                            self.exercise_started = True
                        if 'stand' not in self.evalstr:
                            if self.kp.kinect:
                                self.bodystraight(reconJ)
                        #if self.evalstr == '':
                        #    self.evalstr = self.pushdp.evalstr
                        #    self.pushdp.evalstr = ''
                        self.evalstr = self.pushdp.evalstr  #evalstr gets updated immediately
                        if self.screen_message == '': #and self.shld.ongoing_cycle:
                            self.screen_message = self.pushdp.evalstr # screen message gets the display message
                        self.pushdp.evalstr = ''
                        # === cycle control boolean update ===
                        self.ongoing_cycle = self.pushdp.ongoing_cycle
                        if self.pushdp.cnt > 4:
                            # evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                            evalinst.blit_text(surface, exeno, kp, 'Done! Please push down your arms', 2, color=self.c_stop)
                            #self.pushdp.err.append('Only need to do 4 repetitions.')
                            #self.pushdp.errsum.append('Only need to do 4 repetitions.')
                        elif self.pushdp.cnt == 4:
                            evalinst.blit_text(surface, exeno, kp, 'Done! Please push down your arms', 2, color=self.c_stop)
                        else:
                            if stus == 'up':
                                if self.screen_message == '':
                                    self.screen_message = 'Push down you arms'
                                #evalinst.blit_text(surface, exeno, kp, 'Push down you arms', 2, color=self.c_normal)
                            elif stus == 'upnotstraight':
                                if self.screen_message == '':
                                    self.screen_message = 'Please straighten your arms'
                                #evalinst.blit_text(surface, exeno, kp, 'Please straighten your arms', 2, color=self.c_err)
                            elif stus == 'vshape':
                                if self.screen_message == '':
                                    self.screen_message = 'Raise up your arms'
                                #evalinst.blit_text(surface, exeno, kp, 'Raise up your arms', 2, color=self.c_normal)
                            #
                            evalinst.blit_text(surface, exeno, kp, '%s to go !!' %str(4-self.pushdp.cnt),
                                                4, color=self.c_togo)
                        self.repcnt = self.pushdp.cnt
                else:#if paused 
                    evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Continue to continue', 2)
            else:
                evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Start to begin', 2)
        elif exeno == 4:
            if self.exercise_initialized:
                if not self.paused:
                    if self.kp.kinect:
                        stus = self.handpos(self.exer[4], reconJ)
                    #to check
                    self.stus_lst.append(stus)
                    if stus == 'horizontal' or stus == 'horizontal_bend':  # T-pose
                        if self.screen_message == '':
                            self.screen_message = 'Great, your arms are horizontal!'
                        if self.kp.kinect:
                            self.horzp.do = True
                            self.horzp.run(reconJ)
                            #to check
                            #self.stus_lst.append(self.horzp.state)
                            self.exercise_started = True
                            if 'stand' not in self.evalstr:
                                self.bodystraight(reconJ)
                    elif stus == 'down':
                        if self.horzp.do:
                            self._done = True
                            if self.horzp.cnt  < 4:
                                self.horzp.err.append('Make sure you do 4 repetitions.')
                                self.horzp.errsum.append('Make sure you do 4 repetitions.')
                            print(self.stus_lst)
                            print(self.wr_elb)
                            print(self.wr_shld)
                            print('================= exer END ======================')
                        #else:
                            #stuck op in the screen
                        #    self.permenanent_msg = 'Start with your arms horizontal.'
                        #    evalinst.blit_text(surface, exeno, kp, self.permenanent_msg , 2, color=self.c_err)
                            #evalinst.blit_text(surface, exeno, kp, 'Please raise yours arms.', 2, color=self.c_normal)
                    if self.horzp.do:
                        self.evalstr = self.horzp.evalstr  #evalstr gets updated immediately
                        if self.screen_message == '': #and self.shld.ongoing_cycle:
                            self.screen_message = self.horzp.evalstr # screen message gets the display message
                        self.horzp.evalstr = ''
                        # === cycle control boolean update ===
                        self.ongoing_cycle = self.horzp.ongoing_cycle
                        #if self.evalstr == '':
                        #    self.evalstr = self.horzp.evalstr
                        #    self.horzp.evalstr = ''
                        if self.horzp.cnt > 4:
                            # evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                            evalinst.blit_text(surface, exeno, kp, 'Done! Please push down your arms', 2, color=self.c_stop)
                            #self.horzp.err.append('Only need to do 4 repetitions.')
                            #self.horzp.errsum.append('Only need to do 4 repetitions.')
                        elif self.horzp.cnt == 4:
                            evalinst.blit_text(surface, exeno, kp, 'Done! Please push down your arms', 2, color=self.c_stop)
                        else:
                            #remove this condition
                            if stus == 'horizontal' or stus == 'horizontal_bend':  # T-pose
                                if self.screen_message == '':
                                    self.screen_message = 'Great, your arms are horizontal!'
                            #if stus == None and self.repcnt < 4 : #first check horizontal
                                #pass
                            #elif stus != 'horizontal' and stus != 'horizontal_bend':
                            else:
                                if self.screen_message == '':
                                    self.screen_message = 'Please keep your arms horizontally.'
                                
                                #feels stuck ehre
                                
                                #    evalinst.blit_text(surface, exeno, kp, self.screen_message, 2, color=self.c_err)

                                #pass
                                # self.horzp.evalstr = 'Please keep your arms horizontally.'
                                # self.horzp.eval = 'Please keep your arms horizontally.'
                                #self.horzp.err.append('The '+self.cnvt.ordinal(self.repcnt+1)+ ' time try, please keep your arms horizontally.')
                                #self.horzp.errsum.append('Please keep your arms horizontally.')
                            if self.horzp.state == 'T-pose':
                                if self.screen_message == '':
                                    self.screen_message = 'Please close your arms to your chest'
                                #else:
                                #    if self.screen_message == '':
                                #   self.screen_message = 'Please keep your arms horizontally.'
                                    #if 'great,' in self.screen_message.lower() and 'please' not in self.screen_message.lower() :
                                    #   self.screen_message += '\n\n Please close your arms to your chest' 
                                    #else:
                                    #    self.screen_message += '\n\n And please close your arms to your chest' 
                                    #evalinst.blit_text(surface, exeno, kp, self.screen_message, 2, color=self.c_normal) # was region 2
                            elif self.horzp.state == 'chest':
                                if self.screen_message == '':
                                    self.screen_message = 'Please open your arms to T-pose'
                                #else:
                                #    if 'great,' in self.screen_message.lower() and 'please' not in self.screen_message.lower():
                                #       self.screen_message += '\n\n Please open your arms to T-pose' 
                                #    else:
                                #        self.screen_message += '\n\n And please open your arms to T-pose'
                                    #self.screen_message += 'Please open your arms to T-pose'
                                    #evalinst.blit_text(surface, exeno, kp, self.screen_message, 2, color=self.c_normal) # # was region 2

                            #stuck op in the screen
                            #self.permenanent_msg = 'Start with your arms horizontal.'
                            #evalinst.blit_text(surface, exeno, kp, self.permenanent_msg , 2, color=self.c_err)
                            
                            #down screen 
                            evalinst.blit_text(surface, exeno, kp, '%s to go !!' %str(4-self.horzp.cnt),
                                                4, color=self.c_togo)
                        self.repcnt = self.horzp.cnt
                
                    else:# if the exercise never started
                        if self.cnt >=75:
                            #stuck op in the screen
                            self.start_msg = 'Start with your arms horizontal.'
                            evalinst.blit_text(surface, exeno, kp, self.start_msg , 2, color=self.c_err)
                        self.cnt+=1
                else: # if paused
                    evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Continue to continue', 2)
            else:
                evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Start to begin', 2)
        #COMMENTING OUT THE REACH TO SKY 
            '''
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
                # evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
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
            '''
        #elif exeno == 6:
        elif exeno == 5:
            if self.exercise_initialized:
                if not self.paused:
                    if self.exer[5].cntdown <= 0:
                        if self.kp.kinect:
                            stus = self.handpos(self.exer[5], reconJ)
                        if stus == 'belly':
                            self.cnt = 0
                            if self.kp.kinect:
                                self.shld.run(dmap, djps)
                                self.exercise_started = True
                            # self.exer[6].hraise = True
                        elif stus == 'down':
                            if self.shld.do:
                                if self.cnt > 120:#this was 60, so it was 2 seconds(30 frame per second), now it is 4 seconds
                                    self._done = True
                                    if self.shld.cnt < 4:
                                        self.shld.err.append('Make sure you do 4 repetitions.')
                                        self.shld.errsum.append('Make sure you do 4 repetitions.')
                                    print('================= exer END ======================')
                                self.cnt += 1
                        # === eval string update ===
                        #if self.evalstr == '':
                        #if self.shld.ongoing_cycle : 
                        self.evalstr = self.shld.evalstr  #evalstr gets updated immediately
                        if self.screen_message == '': #and self.shld.ongoing_cycle:
                            self.screen_message = self.shld.evalstr # screen message gets the display message
                        self.shld.evalstr = ''
                        # === cycle control boolean update ===
                        self.ongoing_cycle = self.shld.ongoing_cycle

                        # === eval information ===
                        if self.shld.cnt > 4:
                            # evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                            evalinst.blit_text(surface, exeno, kp, 'Done! Please push down your arms', 2, color=self.c_stop)
                            #self.shld.err.append('Only need to do 4 repetitions')
                            #self.shld.errsum.append('Only need to do 4 repetitions')
                            self._done = True
                        elif self.shld.cnt == 4:
                            evalinst.blit_text(surface, exeno, kp, 'Please push down your arms', 2, color=self.c_stop)
                            self._done = True

                        else:
                            evalinst.blit_text(surface, exeno, kp, 'Rotate your shoulders ', 2, color=self.c_normal)
                            evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.shld.cnt)), 4, color=self.c_togo)
                        self.repcnt = self.shld.cnt
                        print("\nrepcnt:",self.repcnt)
                        print(self.shld.twoslist)
                    else:
                        #evalinst.blit_text(surface, self.exer[5].no, kp,
                        #                ('Starting after %.2f second' % (self.exer[5].cntdown/30.)), 2,
                        #                color=self.c_normal)
                        self.exer[5].cntdown -= 1
                else:#if paused
                    evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Continue to continue', 2)
            else:
                evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Start to begin', 2)

        #elif exeno == 7:
        elif exeno == 6:
            if self.exercise_initialized:
                if not self.paused:
                    #self.ongoing_cycle = False
                    if self.exer[6].cntdown <= 0:
                        if self.kp.kinect:
                            stus = self.handpos(self.exer[6], reconJ)
                            print (stus)
                        if stus == 'down':
                            if self.clsp.do:
                                if self.cnt > 90: # was 90
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
                                self.exercise_started = True
                        # === eval string update ===
                        #if self.evalstr == '':
                        #    self.evalstr = self.clsp.evalstr
                        #    self.clsp.evalstr = ''

                        self.evalstr = self.clsp.evalstr # immdiate
                        if self.screen_message == '': #and self.shld.ongoing_cycle:
                            self.screen_message =  self.clsp.evalstr # screen message gets the display message
                        self.clsp.evalstr = ''
                        # === cycle control boolean update ===
                        self.ongoing_cycle = self.clsp.ongoing_cycle
                        print("cycle control boolean update, ", self.ongoing_cycle )

                        # === eval information ===
                        if self.clsp.cnt > 4:
                            # evalinst.blit_text(surface, exeno, kp, 'Only need to do 4 repetitions', 3, color=self.c_err)
                            evalinst.blit_text(surface, exeno, kp, 'Done! Please push down your arms', 2, color=self.c_stop)
                            #self.clsp.err.append('Only need to do 4 repetitions')
                            #self.clsp.errsum.append('Only need to do 4 repetitions')
                        elif self.clsp.cnt == 4:
                            evalinst.blit_text(surface, exeno, kp, 'Done! Please push down your arms', 2, color=self.c_stop)
                        else:
                            if self.clsp.mode == 'clasp':
                                evalinst.blit_text(surface, exeno, kp, 'Start to clasp, close elbows together', 2, color=self.c_normal)
                            else:   #ana.clasp.mode == 'spread'
                                evalinst.blit_text(surface, exeno, kp, 'Start to spread, pinch shoulders, and open chest', 2, color=self.c_normal) # start to spread
                            evalinst.blit_text(surface, exeno, kp, ('%s to go !!' % (4-self.clsp.cnt)), 4, color=self.c_togo)
                        self.repcnt = self.clsp.cnt
                    else:
                        #evalinst.blit_text(surface, self.exer[6].no, kp,
                        #                ('Starting after %.2f second' % (self.exer[6].cntdown/30.)), 2,
                        #                color=self.c_normal)
                        self.exer[6].cntdown -= 1
                else:#if paused
                    evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Continue to continue', 2)
            else:
                evalinst.blit_text(surface, self.exer[1].no, kp,
                                    'Click Start to begin', 2)

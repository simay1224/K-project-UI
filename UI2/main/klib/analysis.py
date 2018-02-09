import numpy as np
from exercise import Exer1, Exer2, Exer3, Exer4
from dtw2 import Dynamic_time_warping
from breathstus import Breath_status
from handstatus import Hand_status

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
        #
        self.dtw = Dynamic_time_warping()
        self.brth = Breath_status()
        self.hs = Hand_status()
        #
        self.do_once = False
        self._done = False
        self.offset = 0
        self.holdstate = True
        self.holdlist = np.array([])

    def run(self, exeno, reconJ, surface, evalinst, kp, body, dmap=[], bdry=[]):
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
                    evalinst.blit_text(surface, exeno, kp.ratio, kp.scene_type, 'Starting breath in/out', 1, (255, 0, 0, 255))
                    self.brth.breathextract(bdry, dmap)
                else:
                    if not self.do_once:
                        self.brth.breath_analyze(self.offset)
                        self.do_once = True
                        self._done = True
                        print('================= exe END ======================')            
            else:
                evalinst.blit_text(surface, self.exer[1].no, kp.ratio, kp.scene_type, 'will Starting at '\
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
                    evalinst.blit_text(surface, exeno, kp.ratio, kp.scene_type, 'Starting breath in (hand close) and breath out (hand open)', 1)
                    self.hs.hstus_proc(body.hand_left_state, body.hand_right_state)
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
                if self.dtw.idxlist.count(3) > 4:
                    evalinst.blit_text(surface, exeno, kp.ratio, kp.scene_type,\
                                      'Only need to do 4 times', 3)
                    self.dtw.err.append('Only need to do 4 times')
                elif self.dtw.idxlist.count(3) > 0:
                   evalinst.blit_text(surface, exeno, kp.ratio, kp.scene_type,\
                                      str(4-min(self.dtw.idxlist.count(3), self.dtw.idxlist.count(4)))\
                                      + ' to go !!', 3, (55,173,245,255))                
            else:
                print('================= exe END ======================')
                self._done = True                
        elif exeno == 4:
            if not self.exer[4].order[self.dtw.oidx] == 'end':
                self.dtw.matching(reconJ, self.exer[4])
                if self.dtw.idxlist.count(3) > 4:
                    evalinst.blit_text(surface, exeno, kp.ratio, kp.scene_type,\
                                      'Only need to do 4 times', 3)
                    self.dtw.err.append('Only need to do 4 times')
                elif self.dtw.idxlist.count(3) > 0:
                   evalinst.blit_text(surface, exeno, kp.ratio, kp.scene_type,\
                                      str(4-min(self.dtw.idxlist.count(3), self.dtw.idxlist.count(4)))\
                                      + ' to go !!', 3, (55,173,245,255))
            else:
                print('================= exe END ======================')
                self._done = True 
        elif exeno == 5:
            pass
        elif exeno == 6:
            pass
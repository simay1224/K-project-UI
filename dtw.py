# -*- coding: utf-8 -*-

from scipy.spatial.distance import _validate_vector
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy.linalg import norm
from collections import defaultdict
from w_fastdtw import fastdtw
import numpy as np
from scipy.signal import argrelextrema
import pdb


class Dtw(object):
    """ Dynamic time warping 
    """
    def __init__(self):
        """ initailize the order and weight for each exercise
            initailize dtw parameters
        """
        # dtw parameters initialization
        self.decTh       = 2000
        self.cnt         = 0
        self.distp_prev  = 0         
        self.distp_cmp   = np.inf             
        self.oidx        = 0  # initail
        self.gt_idx      = 0 
        self.Ani_idx     = 0
        self.presv_size  = 0
        self.idxlist     = []   
        self.idx_cmp     = 0
        self.fcnt        = 0
        self.finishcnt   = 0
        # updatable parameters       
        self.dpfirst     = {}
        self.dist_p      = {}
        self.deflag_mul  = defaultdict(lambda:(bool(False)))  
        self.seqlist     = np.array([])                
        self.dcnt        = 0 
        self.chk_flag    = False
        self.exechk      = True
        self.deflag      = False   # decreasing flag
        self.onedeflag   = False
        self.segini      = True  
        self.evalstr     = ''
        # exercise order
        self.order = defaultdict(dict)
        # exercise 3
        self.order[3][0] = [1]
        self.order[3][1] = [3]
        self.order[3][2] = 'end'
        self.order[3][3] = [4]
        self.order[3][4] = [2, 3]
        self.order[3][5] = 'end'
        # exercise 4
        self.order[4][0] = [1]
        self.order[4][1] = [3]
        self.order[4][2] = 'end'
        self.order[4][3] = [4]
        self.order[4][4] = [2, 3]
        self.order[4][5] = 'end'
        # animation order
        self.aniorder = defaultdict(dict)
        # exercise 3
        self.aniorder[3][0] = 1
        self.aniorder[3][1] = 3
        self.aniorder[3][2] = 2
        self.aniorder[3][3] = 4
        self.aniorder[3][4] = 3
        # exercise 4
        self.aniorder[4][0] = 1
        self.aniorder[4][1] = 3
        self.aniorder[4][2] = 2
        self.aniorder[4][3] = 4
        self.aniorder[4][4] = 3
        # weight
        self.Jweight = {}
        self.Jweight[3] = np.array([0., 0., 0., 9., 9., 9., 9., 9., 9.,
                                    0., 0., 0., 9., 9., 9., 9., 9., 9.,
                                    0., 0., 0.])
        self.Jweight[4] = np.array([0., 0., 0., 3., 3., 3., 9., 9., 9.,
                                    0., 0., 0., 3., 3., 3., 9., 9., 9.,
                                    0., 0., 0.])
        for ii in self.Jweight.keys():
                self.Jweight[ii] = self.Jweight[ii]/sum(self.Jweight[ii])*1.5

    def wt_euclidean(self, u, v, w):
        """ normal euclidean dist with the weighting
        """
        u = _validate_vector(u)
        v = _validate_vector(v)
        dist = norm(w*(u-v))
        return dist

    def clip(self, seqlist, exeno):

        tgrad = 0
        for ii in [3, 4, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17]:
            tgrad += (np.gradient(gf(seqlist[:, ii], 1))**2)*self.Jweight[exeno][ii]
        tgrad = tgrad**0.5
        lcalminm = argrelextrema(tgrad, np.less, order=5)[0]
        foo = np.where(((tgrad < 1)*1) == 0)[0]
        if (len(foo) == 0) | (len(lcalminm) == []):
            return []
        else:
            lb = max(foo[0], 50)
            minm = []
            for ii in lcalminm[lcalminm > lb]:
                if tgrad[ii] < 1:
                    minm.append(ii)
            # if len(minm) > 1:
            #     pdb.set_trace()
            return minm

    def seg_update(self, endidx):
        """ update the dictionary content then reset the parameters 
        """
        self.seqlist    = self.seqlist[endidx+1:, :]  # update the seqlist
        self.presv_size = self.seqlist.shape[0]
        self.oidx       = self.gt_idx
        self.deflag_mul = defaultdict(lambda: (bool(False)))
        self.cnt        = 0       
        self.dpfirst    = {}
        self.dist_p     = {}
        self.deflag     = False
        self.onedeflag  = False
        self.segini     = True


    def matching(self, reconJ, gt_data, exeno):
        if not self.order[exeno][self.oidx] == 'end':
            if self.segini:  # new segement/movement start
                self.segini = False
                self.Ani_idx = self.aniorder[exeno][self.Ani_idx]
                if len(self.order[exeno][self.oidx]) == 1:
                    self.gt_idx = self.order[exeno][self.oidx][0]
                    self.idxlist.append(self.gt_idx)
            if len(self.seqlist) == 0:  # build sequence list
                self.seqlist = reconJ
                self.seqlist = self.seqlist.reshape(-1, 21)
            else:
                self.seqlist = np.vstack([self.seqlist, reconJ])
                self.seqlist = gf(self.seqlist, 3, axis=0)
            if not self.deflag:  # Not yet decreasing
                if np.mod(self.seqlist.shape[0]-self.presv_size-1, 10) == 0:
                    # check every 10 frames
                    if len(self.order[exeno][self.oidx]) > 1:
                        if self.seqlist.shape[0] > 1:
                            result = self.clip(self.seqlist, exeno)
                            if result != []:
                                endidx = result[0]
                                if self.seqlist[endidx, 7] < 150:
                                    minidx = 2
                                else:
                                    minidx = 3
                                self.gt_idx = minidx
                                self.idxlist.append(self.gt_idx)
                                self.seg_update(endidx)
                    else:
                        test_data_p = self.seqlist + np.atleast_2d((gt_data[self.gt_idx][0, :]-self.seqlist[0, :]))
                        self.dist_p, _ = fastdtw(gt_data[self.gt_idx], test_data_p, self.Jweight[exeno], dist=self.wt_euclidean)
                        if (self.seqlist.shape[0] == 1+self.presv_size):  # new movement initail setting
                            self.dpfirst, _ = fastdtw(gt_data[self.gt_idx], test_data_p[:2], self.Jweight[exeno], dist=self.wt_euclidean)
                            print('dpfirst is : %f' % self.dpfirst)
                        else:
                            print('de diff is :%f' % (self.dpfirst - self.dist_p))
                            if (self.dpfirst - self.dist_p) > self.decTh:
                                print('=========')
                                print('deflag on')
                                print('=========')
                                self.deflag = True
                                self.distp_prev = self.dist_p
            else:  # already start decreasing
                test_data_p = self.seqlist + np.atleast_2d((gt_data[self.gt_idx][0, :] - self.seqlist[0, :]))
                self.dist_p, path_p = fastdtw(gt_data[self.gt_idx], test_data_p, self.Jweight[exeno], dist=self.wt_euclidean)
                if self.chk_flag:  # in check global min status
                    self.cnt += 1
                    if self.dist_p < self.distp_cmp:  # find smaller value
                        self.cnt = 1
                        self.distp_cmp = self.dist_p
                        self.idx_cmp = self.seqlist.shape[0]
                        print(' ==== reset ====')
                    elif self.cnt == 20:
                        self.evalstr = 'Well done'
                        self.chk_flag = False
                        tgrad = 0
                        for ii in xrange(self.seqlist.shape[1]):  # maybe can include Jweight
                            tgrad += (np.gradient(gf(self.seqlist[:, ii], 1))**2)*self.Jweight[exeno][ii]
                        tgrad = tgrad**0.5
                        endidx = np.argmin(tgrad[self.idx_cmp-10:self.idx_cmp+19])+(self.idx_cmp-10)
                        self.seg_update(endidx)
                        # self.seqlist = self.seqlist[endidx+1:, :]  # update the seqlist
                        # self.presv_size = self.seqlist.shape[0]
                        # self.cnt = 0
                        # self.oidx = self.gt_idx
                        # self.dpfirst = {}
                        # self.dist_p = {}
                        # self.deflag = False
                        # self.deflag_mul = defaultdict(lambda: (bool(False)))
                        # self.onedeflag = False
                        # self.segini = True
                else:
                    if (self.dist_p - self.distp_prev) > 0:  # turning point
                        print (' ==============  large ====================')
                        self.distp_cmp = self.distp_prev
                        self.idx_cmp = self.seqlist.shape[0]
                        self.chk_flag = True
                self.distp_prev = self.dist_p
        else:
            print('================= exe END ======================')
            self.exechk = False
        # return dtw

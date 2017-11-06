# -*- coding: utf-8 -*-

from scipy.spatial.distance import _validate_vector
from scipy.ndimage.filters import gaussian_filter1d as gf
from scipy.linalg import norm
from collections import defaultdict
from w_fastdtw import fastdtw
import numpy as np
from scipy.signal import argrelextrema
import pdb


order = defaultdict(dict)

order[3][0] = [1]
order[3][1] = [3]
order[3][2] = 'end'
order[3][3] = [4]
order[3][4] = [2, 3]
order[3][5] = 'end'

order[4][0] = [1]
order[4][1] = [3]
order[4][2] = 'end'
order[4][3] = [4]
order[4][4] = [2, 3]
order[4][5] = 'end'
aniorder = defaultdict(dict)

aniorder[3][0] = 1
aniorder[3][1] = 3
aniorder[3][2] = 2
aniorder[3][3] = 4
aniorder[3][4] = 3

aniorder[4][0] = 1
aniorder[4][1] = 3
aniorder[4][2] = 2
aniorder[4][3] = 4
aniorder[4][4] = 3


Jweight = {}
Jweight[3] = np.array([0., 0., 0., 9., 9., 9., 9., 9., 9.,
                       0., 0., 0., 9., 9., 9., 9., 9., 9.,
                       0., 0., 0.])
Jweight[4] = np.array([0., 0., 0., 3., 3., 3., 9., 9., 9.,
                       0., 0., 0., 3., 3., 3., 9., 9., 9.,
                       0., 0., 0.])


for ii in Jweight.keys():
        Jweight[ii] = Jweight[ii]/sum(Jweight[ii])*1.5


def wt_euclidean(u, v, w):
    u = _validate_vector(u)
    v = _validate_vector(v)
    dist = norm(w*(u - v))
    return dist


def clip(seqlist, exeno):

    tgrad = 0

    for ii in [3, 4, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17]:
        tgrad += (np.gradient(gf(seqlist[:, ii], 1))**2)*Jweight[exeno][ii]
    tgrad = tgrad**0.5
    lcalminm = argrelextrema(tgrad, np.less, order=5)[0]
    foo = np.where(((tgrad < 1)*1) == 0)[0]
    if (len(foo) == 0) | (len(lcalminm) == []):
        return []
    else:
        LB = max(foo[0], 50)
        minm = []
        for ii in lcalminm[lcalminm > LB]:
            if tgrad[ii] < 1:
                minm.append(ii)
        if len(minm) > 1:
            pdb.set_trace()
        return minm


def seg_update(Dtw, endidx):
    Dtw['seqlist'] = Dtw['seqlist'][endidx+1:, :]  # update the seqlist
    Dtw['presv_size'] = Dtw['seqlist'].shape[0]
    Dtw['cnt'] = 0
    Dtw['oidx'] = Dtw['gt_idx']
    Dtw['dpfirst'] = {}
    Dtw['dist_p'] = {}
    Dtw['deflag'] = False
    Dtw['deflag_mul'] = defaultdict(lambda: (bool(False)))
    Dtw['onedeflag'] = False
    Dtw['segini'] = True
    return Dtw


def DTW_matching2(Dtw, reconJ, gt_data, exeno):
    if not order[exeno][Dtw['oidx']] == 'end':
        if Dtw['segini']:  # new segement/movement start
            Dtw['segini'] = False
            Dtw['Ani_idx'] = aniorder[exeno][Dtw['Ani_idx']]
            if len(order[exeno][Dtw['oidx']]) == 1:
                Dtw['gt_idx'] = order[exeno][Dtw['oidx']][0]
                Dtw['idxlist'].append(Dtw['gt_idx'])
        if len(Dtw['seqlist']) == 0:  # build sequence list
            Dtw['seqlist'] = reconJ
            Dtw['seqlist'] = Dtw['seqlist'].reshape(-1, 21)
        else:
            Dtw['seqlist'] = np.vstack([Dtw['seqlist'], reconJ])
            Dtw['seqlist'] = gf(Dtw['seqlist'], 3, axis=0)
        if not Dtw['deflag']:  # Not yet decreasing
            if np.mod(Dtw['seqlist'].shape[0]-Dtw['presv_size']-1, 10) == 0:
                # check every 10 frames
                if len(order[exeno][Dtw['oidx']]) > 1:
                    if Dtw['seqlist'].shape[0] > 1:
                        result = clip(Dtw['seqlist'], exeno)
                        if result != []:
                            endidx = result[0]
                            if Dtw['seqlist'][endidx, 7] < 150:
                                minidx = 2
                            else:
                                minidx = 3
                            Dtw['gt_idx'] = minidx
                            Dtw['idxlist'].append(Dtw['gt_idx'])
                            Dtw.update(seg_update(Dtw, endidx))
                else:
                    test_data_p = Dtw['seqlist'] + np.atleast_2d((gt_data[Dtw['gt_idx']][0, :]-Dtw['seqlist'][0, :]))
                    Dtw['dist_p'], _ = fastdtw(gt_data[Dtw['gt_idx']], test_data_p, Jweight[exeno], dist=wt_euclidean)
                    if (Dtw['seqlist'].shape[0] == 1+Dtw['presv_size']):  # new movement initail setting
                        Dtw['dpfirst'], _ = fastdtw(gt_data[Dtw['gt_idx']], test_data_p[:2], Jweight[exeno], dist=wt_euclidean)
                        print('dpfirst is : %f' % Dtw['dpfirst'])
                    else:
                        print('de diff is :%f' % (Dtw['dpfirst'] - Dtw['dist_p']))
                        if (Dtw['dpfirst'] - Dtw['dist_p']) > Dtw['decTh']:
                            print('=========')
                            print('deflag on')
                            print('=========')
                            Dtw['deflag'] = True
                            Dtw['distp_prev'] = Dtw['dist_p']
        else:  # already start decreasing
            test_data_p = Dtw['seqlist'] + np.atleast_2d((gt_data[Dtw['gt_idx']][0, :] - Dtw['seqlist'][0, :]))
            Dtw['dist_p'], path_p = fastdtw(gt_data[Dtw['gt_idx']], test_data_p, Jweight[exeno], dist=wt_euclidean)
            if Dtw['chk_flag']:  # in check global min status
                Dtw['cnt'] += 1
                if Dtw['dist_p'] < Dtw['distp_cmp']:  # find smaller value
                    Dtw['cnt'] = 1
                    Dtw['distp_cmp'] = Dtw['dist_p']
                    Dtw['idx_cmp'] = Dtw['seqlist'].shape[0]
                    print(' ==== reset ====')
                elif Dtw['cnt'] == 20:
                    Dtw['evalstr'] = 'Well done'
                    Dtw['chk_flag'] = False
                    tgrad = 0
                    for ii in xrange(Dtw['seqlist'].shape[1]):  # maybe can include Jweight
                        tgrad += (np.gradient(gf(Dtw['seqlist'][:, ii], 1))**2)*Jweight[exeno][ii]
                    tgrad = tgrad**0.5
                    endidx = np.argmin(tgrad[Dtw['idx_cmp']-10:Dtw['idx_cmp']+19])+(Dtw['idx_cmp']-10)
                    Dtw['seqlist'] = Dtw['seqlist'][endidx+1:, :]  # update the seqlist
                    Dtw['presv_size'] = Dtw['seqlist'].shape[0]
                    Dtw['cnt'] = 0
                    Dtw['oidx'] = Dtw['gt_idx']
                    Dtw['dpfirst'] = {}
                    Dtw['dist_p'] = {}
                    Dtw['deflag'] = False
                    Dtw['deflag_mul'] = defaultdict(lambda: (bool(False)))
                    Dtw['onedeflag'] = False
                    Dtw['segini'] = True
            else:
                if (Dtw['dist_p'] - Dtw['distp_prev']) > 0:  # turning point
                    print (' ==============  large ====================')
                    Dtw['distp_cmp'] = Dtw['distp_prev']
                    Dtw['idx_cmp'] = Dtw['seqlist'].shape[0]
                    Dtw['chk_flag'] = True
            Dtw['distp_prev'] = Dtw['dist_p']
    else:
        print('================= exe END ======================')
        Dtw['exechk'] = False
    return Dtw

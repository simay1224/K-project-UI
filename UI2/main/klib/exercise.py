import numpy as np
import h5py, pdb


data2 = h5py.File('data/GT_V_data_mod_EX2.h5', 'r')
data3 = h5py.File('data/GT_V_data_mod_EX3.h5', 'r')
data4 = h5py.File('data/GT_V_data_mod_EX4.h5', 'r')

class Exer1(object):

    def __init__(self):
        self.no = 1
        self.cntdown       = 90     
        # order
        self.order = {}
        self.order[0] = [1]
        self.order[1] = [2]
        self.order[2] = 'end'
        # weight
        self.jweight = np.array([0., 0., 0., 3., 3., 3., 9., 9., 9.,
                                 0., 0., 0., 3., 3., 3., 9., 9., 9.,
                                 0., 0., 0.])
        self.jweight = self.jweight/sum(self.jweight)*1.5

class Exer2(object):

    def __init__(self):
        self.no = 2
        # reference subsequences
        self.gt_data = {}
        self.gt_data[1] = data2['GT_1'][:]
        self.gt_data[2] = data2['GT_2'][:]
        # parameters

        # order
        self.order = {}
        self.order[0] = [1]
        self.order[1] = [2]
        self.order[2] = 'end'
        # weight
        self.jweight = np.array([0., 0., 0., 3., 3., 3., 9., 9., 9.,
                                 0., 0., 0., 3., 3., 3., 9., 9., 9.,
                                 0., 0., 0.])
        self.jweight = self.jweight/sum(self.jweight)*1.5

class Exer3(object):

    def __init__(self):
        self.no = 3
        # reference subsequences
        self.gt_data = {}
        self.gt_data[1] = data3['GT_1'][:]
        self.gt_data[2] = data3['GT_2'][:]
        self.gt_data[3] = data3['GT_3'][:]
        self.gt_data[4] = data3['GT_4'][:]       
        # order
        self.order = {}
        self.order[0] = [1]
        self.order[1] = [3]
        self.order[2] = 'end'
        self.order[3] = [4]
        self.order[4] = [2, 3]
        self.order[5] = 'end'
        # weight
        self.jweight = np.array([0., 0., 0., 9., 9., 9., 9., 9., 9.,
                                 0., 0., 0., 9., 9., 9., 9., 9., 9.,
                                 0., 0., 0.])
        self.jweight = self.jweight/sum(self.jweight)*1.5

class Exer4(object):

    def __init__(self):
        self.no = 4
        # reference subsequences
        self.gt_data = {}
        self.gt_data[1] = data4['GT_1'][:]
        self.gt_data[2] = data4['GT_2'][:]
        self.gt_data[3] = data4['GT_3'][:]
        self.gt_data[4] = data4['GT_4'][:]         
        # order
        self.order = {}
        self.order[0] = [1]
        self.order[1] = [3]
        self.order[2] = 'end'
        self.order[3] = [4]
        self.order[4] = [2, 3]
        self.order[5] = 'end'
        # weight
        self.jweight = np.array([0., 0., 0., 3., 3., 3., 9., 9., 9.,
                                 0., 0., 0., 3., 3., 3., 9., 9., 9.,
                                 0., 0., 0.])
        self.jweight = self.jweight/sum(self.jweight)*1.5
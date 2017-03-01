# -*- coding: utf-8 -*-
"""
Created on Tue Jan 03 12:07:09 2017

@author: medialab
"""

import cPickle 
import matplotlib.pyplot as plt
from hmmlearn import hmm
import numpy as np
from Kfunc import *
from Kfunc.model import *
from mpl_toolkits.mplot3d import Axes3D


data = cPickle.load(file('./output/pkl/mocapdata1128_array.pkl','r'))

tdata = data['rcpos'][:,:400].T



model = hmm.GaussianHMM(n_components=8).fit(tdata)

Z =model.predict(tdata)


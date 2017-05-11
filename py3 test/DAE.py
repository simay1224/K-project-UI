# -*- coding: utf-8 -*-
"""
Created on Thu May 11 16:01:14 2017

@author: medialab
"""
import numpy as np

def sigmoid(x):
    return 1/(1+np.exp(-x))
    
def relu(x):
    x[x<0]=0
    return x
    

def DAE(Kdata,W1,W2,Wp1,Wp2,be1,be2,bd1,bd2):
    
    
    h1 = sigmoid(np.dot(Kdata,W1)+be1)
    h2 = sigmoid(np.dot(   h1,W1)+be2)
    h3 = sigmoid(np.dot(   h2,Wp1)+bd2)
    h4 = sigmoid(np.dot(   h3,Wp2)+bd2)
    
    return h4
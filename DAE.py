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
    

def DAE(kdata,W1,W2,Wp1,Wp2,be1,be2,bd1,bd2):
    
    
#    h1 = sigmoid(np.dot(kdata,W1 )+be1)
#    h2 = sigmoid(np.dot(   h1,W2 )+be2)
#    h3 = sigmoid(np.dot(   h2,Wp1)+bd1)
#    h4 = sigmoid(np.dot(   h3,Wp2)+bd2)

    h1 = relu(np.dot(kdata,W1 )+be1)
    h2 = relu(np.dot(   h1,W2 )+be2)
    h3 = relu(np.dot(   h2,Wp1)+bd1)
    h4 = sigmoid(np.dot(   h3,Wp2)+bd2)    
    return h4.reshape(-1,18)
 


#
#
#import tensorflow as tf
#
#import numpy as np
#
#kdata = np.ones((1,18))
#
#
#def DAE(Kdata,W1,W2,Wp1,Wp2,be1,be2,bd1,bd2):
#    
#x = tf.placeholder(tf.float32, shape = [None, 18])
#h_e_1 = tf.nn.sigmoid(tf.matmul(x,W1)+be1)
#h_e_2 = tf.nn.sigmoid(tf.matmul(h_e_1,W2)+be2)
#h_d_1 = tf.nn.sigmoid(tf.matmul(h_e_2,Wp1)+bd1)
#h_d_2 = tf.sigmoid(tf.matmul(h_d_1,Wp2)+bd2)
#
#sess = tf.InteractiveSession()
#output = sess.run(h_d_2, feed_dict={x : Kdata})
#    
#    return output
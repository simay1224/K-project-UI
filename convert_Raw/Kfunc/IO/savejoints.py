# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 14:18:41 2016

@author: medialab
"""
import cPickle

def savejoints(string,colorjoint,depthjoint):        
    cPickle.dump(colorjoint,file('bodyjoints'+string+'.pkl','wb'))        
    cPickle.dump(depthjoint,file('bodyjoints'+string+'_dp.pkl','wb'))
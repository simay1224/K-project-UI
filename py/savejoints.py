# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 14:18:41 2016

@author: medialab
"""
import cPickle

def savejoints(self,colorjoint,depthjoint):        
    cPickle.dump(colorjoint,file('bodyjoints'+repr(self.now.month).zfill(2)+repr(self.now.day).zfill(2)+repr(self.now.hour).zfill(2)+repr(self.now.minute).zfill(2)+'.pkl','wb'))        
    cPickle.dump(colorjoint,file('bodyjoints'+repr(self.now.month).zfill(2)+repr(self.now.day).zfill(2)+repr(self.now.hour).zfill(2)+repr(self.now.minute).zfill(2)+'_dp.pkl','wb'))
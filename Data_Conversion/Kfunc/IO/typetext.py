# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 16:48:49 2016

@author: medialab
"""
import pygame

def typetext(frame_surface,string,pos,color = (255,255,0),fontsize=60,bold=False):
    myfont = pygame.font.SysFont("Arial", fontsize,bold)
    label = myfont.render(string, 1, color)
    frame_surface.blit(label, pos)
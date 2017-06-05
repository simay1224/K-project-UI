# -*- coding: utf-8 -*-
"""
Created on Sun Jun 04 16:06:41 2017

@author: Dawnknight
"""
import pygame,os
import numpy as np


pygame.init()
screen = pygame.display.set_mode((1920,1080),pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE,32)
pygame.display.set_caption('My game')
draw_surface = pygame.Surface((1920, 1080))



frame = pygame.image.load(os.path.abspath("BK_left.JPG"))
done = False
pygame.draw.line(draw_surface, pygame.color.THECOLORS["red"], (200,0), (200,1000), 18)
while not done:

#    screen
#    
    
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
    
        elif event.type == pygame.VIDEORESIZE: # window resized
            screen = pygame.display.set_mode(event.dict['size'],pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
    
    
#    h_to_w = float(frame_surface.get_height()) / frame_surface.get_width()
#    target_height = int(h_to_w * screen.get_width())    
#    surface_to_draw = pygame.transform.scale(frame_surface, (screen.get_width(), target_height))

#    h_to_w = float(frame_surface.get_height()) / frame_surface.get_width()
#    target_height = int(h_to_w * screen.get_width())    
#    surface_to_draw = pygame.transform.scale(frame_surface, (screen.get_width(), target_height))
    
    screen.blit(draw_surface, (0,0))
    screen.blit(frame, (0,0))
#    frame_surface.blit(frame, (0,0))
    surface_to_draw = None
    pygame.display.update()        


        
pygame.quit()        
        
#screen.blit(charImage,(0,0))
#pygame.display.flip()
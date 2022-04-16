import pygame
import sys
import pygame.gfxdraw

from math import *
from pygame.locals import *
from copy import *

def gen_points(beginning , wave_length , amplitude , number):
     
     points = []
     current_point = copy(beginning)
     
     for i in range(number):
          if i % 2 == 0:
               cpoints = [
                    copy(current_point),
                    current_point + pygame.Vector2(wave_length/4 , 0) + amplitude,
                    current_point + pygame.Vector2(wave_length/4*3 , 0 ) + amplitude,
                    current_point + pygame.Vector2(wave_length , 0),
               ]
          else:
               cpoints = [
                    copy(current_point),
                    current_point + pygame.Vector2(wave_length/4 , 0) - amplitude,
                    current_point + pygame.Vector2(wave_length/4*3 , 0) - amplitude,
                    current_point + pygame.Vector2(wave_length , 0),
               ]
          
          points.append(cpoints)
          current_point += pygame.Vector2(wave_length , 0)
     
     return points

pygame.init()
screen = pygame.display.set_mode([500 , 500])
amplitude = pygame.Vector2(0 , 20) 
points = gen_points(pygame.Vector2(0 , 250) , 20 , amplitude , 30)      
clock = pygame.time.Clock()
timer = 0
font = pygame.font.Font(None , 20)

while True:
     
     dt = clock.tick(300)*0.001
     timer += dt
     screen.fill([0,0,0])
     amplitude.y = sin(timer)*20
     for event in pygame.event.get():
          if event.type == QUIT:
               pygame.quit()
               sys.exit(0)
     
     for curve in points:
          pygame.gfxdraw.bezier(screen , curve , 200 , [255,255,255])
     
     screen.blit(font.render(f"FPS : {int(clock.get_fps())}" , True , [255 , 0 , 0]) , [0,0])
     pygame.display.flip()
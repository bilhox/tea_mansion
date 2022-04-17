import pygame
import sys
import pygame.gfxdraw

from math import *
from pygame.locals import *
from copy import *

pygame.init()
screen = pygame.display.set_mode([500 , 500])
clock = pygame.time.Clock()
font = pygame.font.Font(None , 20)
start = pygame.Vector2(250 , 250)
vect = pygame.Vector2(100 , 0)
vect = vect.rotate(45)
print(vect)

while True:
     
     dt = clock.tick(300)*0.001
     screen.fill([0,0,0])
     for event in pygame.event.get():
          if event.type == QUIT:
               pygame.quit()
               sys.exit(0)
     
     pygame.draw.line(screen , [255]*3 , start , start+vect , 1)
     screen.blit(font.render(f"FPS : {int(clock.get_fps())}" , True , [255 , 0 , 0]) , [0,0])
     pygame.display.flip()
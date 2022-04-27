import pygame
import sys

from pygame.locals import *
from scripts.camera import *
from scripts.particles import *
from scripts.unclassed_functions import *
from random import *
from math import *

pygame.init()

screen = pygame.display.set_mode([600 , 600])
camera = Camera(pygame.Vector2(0,0) , pygame.Vector2(300 , 300))
clock = pygame.time.Clock()

colors = [
     [255, 103, 43],
     [222, 80, 24],
     [255, 140, 25],
     [129, 129, 127]
]

part_imgs = get_imgs_from_sheet("./assets/particles/burn_particles-Sheet.png" , 4)
particle_system = Particle_system()
font = pygame.font.Font(None , 20)
timer = 0
     
while True:
     
     dt = clock.tick(200) * 0.001
     timer += dt
     camera.erase_surf([0 , 0 , 0])
     
     for event in pygame.event.get():
          if event.type == QUIT:
               pygame.quit()
               sys.exit(0)
     
     mpos = pygame.mouse.get_pos()
     
     if timer - .5 > 0:
          timer = 0
          particle_burst(particle_system , pygame.Vector2(mpos)*.5 , 40 , 40 , part_imgs , 0.3 , choice(colors))
     
     particle_system.update_and_draw(dt , camera.render_surf , camera.pos)
     
     camera.display(screen , screen.get_rect())
     screen.blit(font.render(f"FPS : {int(clock.get_fps())}" , True , [255 , 0 , 0]) , [0,0])
     screen.blit(font.render(f"particles : {len(particle_system.particles)}" , True , [255 , 0 , 0]) , [0,22])
     pygame.display.flip()
     


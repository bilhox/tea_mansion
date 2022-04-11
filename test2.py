import pygame
import pygame.gfxdraw
import pygame.camera
import pygame.tests
import sys

from pygame.locals import *
from scripts.camera import *
from random import *


pygame.init()
pygame.camera.init()

screen = pygame.display.set_mode([800 , 600])
camera = Camera([0,0],[400 , 300])
cameras = pygame.camera.list_cameras()
cam = pygame.camera.Camera(cameras[0])
cam.start()
size = cam.get_size()

frame = pygame.Surface(size)

while True:
     
     # screen.fill([0,0,0])
     # camera.erase_surf([0,0,0])
     # camera.update()
     
     for event in pygame.event.get():
          if event.type == QUIT:
               pygame.quit()
               sys.exit()
     
     # pygame.gfxdraw.bezier(camera.render_surf, [[100 , 150],[200 , 10],[300 , 200]], 201 , [255 , 255 , 255])
     img = cam.get_image().copy()
     screen.blit(img,[randint(0 , 10),randint(0,10)])
     # camera.display(screen)
     pygame.display.flip()
     
import pygame
import sys

from pygame.locals import *

pygame.mixer.init()

screen = pygame.display.set_mode([100  , 100])

a = pygame.mixer.Sound("./assets/sfx/ringing.mp3")

while True:
     
     for event in pygame.event.get():
          if event.type == QUIT:
               pygame.quit()
               sys.exit(0)
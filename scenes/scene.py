from re import S
import pygame
import sys

from pygame.locals import *

MAX_FPS = 125

class Scene:
     
     def __init__(self , screen , scene_manager):
          self.screen = screen
          self.scene_manager = scene_manager
          
          
     def start(self):
          pass
     
     def update(self):
          
          for event in pygame.event.get():
               if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
          
          pygame.display.flip()

class Scene_Manager():
     
     def __init__(self):
          
          self.scenes = {}
          
          self.current_scene = None
     
     def set_scene(self , id):
          self.current_scene = self.scenes[id]
          self.current_scene.start()
          
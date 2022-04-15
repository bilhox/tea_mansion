from re import S
import pygame
import sys

from pygame.locals import *

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

class Transition:
     
     def __init__(self , b_dur , a_dur , event):
          self.filter = pygame.Surface(pygame.display.get_window_size() , SRCALPHA)
          self.alpha = 0
          
          self.timer = 0
          self.b_dur = b_dur
          self.a_dur = a_dur
          self.alpha_coef = 1
          self.event = event
          self.event_called = False
     
     def update(self , time_infos):
          max_fps = time_infos["max_fps"]
          dt = time_infos["dt"]
          
          if self.timer == 0:
               self.alpha_coef = 255 / self.b_dur
          
          if self.b_dur - self.timer >= 0:
               self.alpha += self.alpha_coef * dt
          else:
               self.alpha -= self.alpha_coef * dt
          
          self.timer += dt
          
          if self.b_dur - self.timer <= 0 and not self.event_called:
               self.alpha_coef = 255 / self.a_dur
               self.event_called = True
               self.event()
          
          self.filter = pygame.Surface(pygame.display.get_window_size() , SRCALPHA)
          self.filter.fill([0,0,0,max(0 , min(255 , self.alpha))])
     
     def is_finished(self):
          return self.a_dur + self.b_dur - self.timer <= 0
     
     def display(self , screen):
          screen.blit(self.filter , [0,0])

class Scene_Manager():
     
     def __init__(self):
          
          self.scenes = {}
          self.transition = None
          self.current_scene = None
     
     def set_scene(self , id):
          self.current_scene = self.scenes[id]
          self.current_scene.start()
     
     def update(self , time_infos):
          if self.current_scene != None:
               self.current_scene.update(time_infos)
          if self.transition != None:
               self.transition.update(time_infos)
               self.transition.display(pygame.display.get_surface())
               if self.transition.is_finished():
                    self.transition = None
          pygame.display.flip()
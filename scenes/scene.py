import pygame
import sys

from math import pi , cos , sin , radians
from random import randint , choice
from pygame.locals import *
from copy import copy
from scripts.particles import *

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
     
     def __init__(self , duration , event=None):
          
          self.timer = 0
          self.duration = duration
          self.event = event
          self.finished = False
     
     def update(self , time_infos):
          
          if not self.finished:
               dt = time_infos["dt"]
               
               self.timer += dt
               
               if self.timer - self.duration >= 0:
                    if self.event != None:
                         self.event()
                    self.finished = True
     
     def display(self , screen):
          pass
          
class Fade_transition(Transition):
     
     def __init__(self , duration , on : bool , event=None):
          super().__init__(duration , event)
          self.filter = pygame.Surface(pygame.display.get_window_size() , SRCALPHA)
          self.alpha_coef = 255 / self.duration
          self.state = on
          self.alpha = 0 if self.state else 255
     
     def update(self , time_infos):
          super().update(time_infos)

          dt = time_infos["dt"]
          
          if not self.finished:
               if self.state:
                    self.alpha += self.alpha_coef * dt
               else:
                    self.alpha -= self.alpha_coef * dt
               
               
               self.filter = pygame.Surface(pygame.display.get_window_size() , SRCALPHA)
               self.filter.fill([0,0,0,max(0 , min(255 , self.alpha))])
     
     def display(self , screen):
          screen.blit(self.filter , [0,0])

class Rand_transition:
     
     def __init__(self, on , event=None):
          
          self.event = event
          self.state = on
          
          self.finished = False
          
          if self.state:
               self.part_sys = Particle_system()
               self.part_img = pygame.Surface([1 , 1])
               self.part_img.fill([255 , 255 , 255])
               
               def custom_update(particle : Particle , dt : float):
                    particle.motion -= particle.motion * dt * 0.95
                    # particle.decay_rate = max(particle.decay_rate , 0.1)
               
               self.part_sys.custom_update = custom_update
          
          self.progression = 1
          self.alpha = 255 if self.state else 0
          
          self.beginning_timer = 0

          self.screen_size = pygame.display.get_window_size()
          
          self.filter = pygame.Surface(self.screen_size , SRCALPHA)
          self.filter.fill([0,0,0,255 if not self.state else 0])
          
          self.points = [
               pygame.Vector2(self.screen_size[0] / 2 , self.screen_size[1] / 2) for _ in range(4)
          ]
          
     def update(self , time_infos):
          dt = time_infos["dt"]
          if hasattr(self , "part_sys"):
               self.part_sys.update(dt)
          if self.state and self.beginning_timer - 1 <= 0:
               if self.beginning_timer == 0:
                         
                    for _ in range(1000):
                         angle = radians(randint(1 , 360))
                         motion = pygame.Vector2(cos(angle) * randint(10 , 200) , sin(angle) * randint(10 , 200))
                         self.part_sys.particles.append(Particle(
                              pygame.Vector2(randint(0 , self.screen_size[0]) , self.screen_size[1] / 2),
                              motion,
                              1,
                              [self.part_img],
                              2
                         ))

               
               self.beginning_timer += dt
          else:
               self.progression += 2000 * dt * max((self.progression / self.screen_size[0]) , 0.2)
               
               
               self.points[0].y = self.screen_size[1] / 2 - self.progression 
               self.points[1].x = self.screen_size[0] / 2 + self.progression 
               self.points[2].y = self.screen_size[1] / 2 + self.progression 
               self.points[3].x = self.screen_size[0] / 2 - self.progression
          
               
          if self.progression > self.screen_size[0] * 1.5:
               if self.event != None:
                    self.event()
               self.finished = True     
     
     def display(self , screen):
          
          if hasattr(self , "part_sys"):
               self.part_sys.draw(screen)
          pygame.draw.polygon(self.filter , [0,0,0,self.alpha] , self.points)
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
               if self.transition.finished:
                    self.transition = None
          pygame.display.flip()
import pygame
import scripts.entity
import scripts.map

from scripts.form import *

class Camera():
     
     def __init__(self , pos , size):
          self.rect = pygame.FRect(pos, size)
          self.output_pos = pygame.Vector2(0, 0)
          self.render_surf = pygame.Surface(self.rect.size)
     
     def erase_surf(self , color):
          self.render_surf.fill(color)
     
     def update(self , dt , max_fps=60):
          if (self.render_surf.get_width() != self.rect.w or self.render_surf.get_height() != self.rect.h):
               self.render_surf = pygame.Surface(self.rect.size)
     
     def display(self , dest : pygame.Surface , scale_factor = 1):
          dest.blit(pygame.transform.scale_by(self.render_surf , scale_factor) , self.output_pos)

class Transition_data:
     
     def __init__(self , data):
          self.data = data
          self.timer = 0
          self.current_part = self.data[0]
          self.ended = False
          self.index = 0
     
     def update(self):
          if not self.ended:
               self.timer += 1
               if (self.current_part["duration"] < self.timer):
                    a = pygame.Vector2(self.current_part["value"],0)
                    b = pygame.Vector2(self.current_part["to"] , 0)
                    c = pygame.Vector2.lerp(a , b , self.current_part["coef"])
                    return self.current_part["type"] , c.x
               else:
                    try:
                         self.index += 1
                         self.current_part = self.data[self.index]
                         self.timer = 0
                    except:
                         self.ended = True
               
          
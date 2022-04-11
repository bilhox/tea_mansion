import pygame
import scripts.entity
import scripts.map

from pygame.locals import *
from scripts.form import *

class Camera():
     
     def __init__(self , pos , size):
          self.pos = pygame.math.Vector2(pos)
          self.size = pygame.math.Vector2(size)
          self.render_surf = pygame.Surface(self.rect.size)
     
     @property
     def rect(self):
          return FloatRect(self.pos , self.size)
     
     def erase_surf(self , color):
          self.render_surf.fill(color)
     
     def update(self , dt , max_fps=60):
          if (self.render_surf.get_width() != self.size.x or self.render_surf.get_height() != self.size.y):
               self.render_surf = pygame.Surface(self.rect.size)
     
     def display(self , screen , display_rect : Rect):
          screen.blit(pygame.transform.scale(self.render_surf , display_rect.size) , [display_rect.x , display_rect.y])
     
     # def display(self , screen , *drawables):
          
     #      self.render_surf.fill([0,0,0])
     #      int_rect = self.rect.int_rect()
          
     #      if (self.render_surf.get_width() != self.rect.size.x or self.render_surf.get_height() != self.rect.size.y):
     #           self.render_surf = pygame.Surface(self.rect.size)
          
     #      for drawable in drawables:
     #           if isinstance(drawable , scripts.entity.Player):
     #                if collide_rect(drawable.rect , self.rect):
     #                     drawable.display(self.render_surf , [self.pos.x , self.pos.y])
     #           elif isinstance(drawable , scripts.map.TileMap):
     #                drawable.display(self.render_surf , int_rect , self.pos)
     #           elif isinstance(drawable , FloatRect):
     #                if collide_rect(drawable , self.rect):
     #                     drawable.draw(self.render_surf , self.pos)
          
     #      screen.blit(pygame.transform.scale(self.render_surf , screen.get_size()) , [0,0])

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
               
          
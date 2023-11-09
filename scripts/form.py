import pygame
import asyncio 

from math import *

# class FloatRect:
     
#      def __init__(self , pos : pygame.Vector2 , size : pygame.Vector2):
          
#           assert size.x > 0 and size.y > 0 , "The size can't have negative values !"
#           self.pos = pos
#           self.size = size
#           self.rotation = 0
#           self.origin = pygame.Vector2(0,0)
#           self.color = [0,0,0]
#           self.border_thickness = 1
     
#      def get_vertices(self , rounded=False , offset=pygame.Vector2(0,0)):
#           vertices = [
#                self.pos - self.origin,
#                pygame.Vector2(self.right , self.pos.y) - self.origin,
#                pygame.Vector2(self.right , self.bottom) - self.origin,
#                pygame.Vector2(self.pos.x , self.bottom) - self.origin
#           ]
               
#           for vertex in vertices:
#                if self.rotation != 0:
#                     vertex_center = vertex - self.pos
#                     vertex.x = vertex_center.x*cos(radians(self.rotation))-vertex_center.y*sin(radians(self.rotation))+self.pos.x
#                     vertex.y = vertex_center.x*sin(radians(self.rotation))+vertex_center.y*cos(radians(self.rotation))+self.pos.y
               
#                vertex -= offset
          
#           if (rounded):
#                vertexArray = []
#                for vertex in vertices:
#                     vertexArray.append([int(vertex.x) , int(vertex.y)])
               
#                return vertexArray
          
#           return vertices
     
#      def int_rect(self , offset=pygame.Vector2(0,0)):
#           return Rect((self.pos.x - self.origin.x - offset.x) , (self.pos.y - self.origin.y - offset.y), self.size.x // 1 , self.size.y // 1)
     

#      def get_right(self):
#           return self.pos.x + self.size.x
     

#      def set_right(self , value):
#           self.pos.x = value - self.size.x
     

#      def get_bottom(self):
#           return self.pos.y + self.size.y
     

#      def set_bottom(self , value):
#           self.pos.y = value - self.size.y
          
#      def get_x(self): return self.pos.x
#      def set_x(self , value): self.pos.x = value
     
#      def get_y(self): return self.pos.y
#      def set_y(self , value): self.pos.y = value
          
#      right = property(get_right , set_right)
#      bottom = property(get_bottom , set_bottom)
#      x = property(get_x , set_x)
#      y = property(get_y , set_y)
     
#      def collidepoint(self , point : pygame.Vector2):
#           return (self.x <= point.x <= self.right and self.y <= point.y <= self.bottom)
     
#      def draw(self , surface , offset=pygame.Vector2(0,0) , ignore_transform=False):
#           if not ignore_transform:
#                pygame.draw.polygon(surface , self.color , self.get_vertices(True , offset) , self.border_thickness)
#           else:
#                pygame.draw.rect(surface , self.color , self.int_rect(offset) , self.border_thickness)
     

class Collider():
     
     def __init__(self , rect : pygame.FRect , type : str):
          self.type = type
          self.rect = rect
          self.colliders_on = []
          self.timer = 0
          self.move_above = False
          self.on_moving_platform = False
          self.collider_under = None
          
     def set_on_moving_platform(self , case : bool , c=None):
          if case:
               self.on_moving_platform = True
               # if c != None and self.collider_under == None:
               c.colliders_on.append(self)
               self.collider_under = c
          else:
               self.on_moving_platform = False
               self.collider_under.colliders_on.remove(self)
               self.collider_under = None
               
     
     def move(self , vector : pygame.Vector2):
          self.rect.x += vector.x
          self.rect.y += vector.y
          if self.colliders_on != []:
               for c in self.colliders_on:
                    c.rect.x += vector.x
                    c.rect.y += vector.y
                    # rect.pos = self.rect.pos + pygame.Vector2(rect.x - self.rect.x , rect.y - self.rect.y) + vector
          
          self.timer += 1
     
     def collide(self , collider):
          if collider in self.colliders_on:
               return True
          else:
               return self.rect.colliderect(collider.rect)
               
     
def SAT_collision(r1 : pygame.FRect , r2 : pygame.FRect):
     rect1 = r1.get_vertices()
     rect2 = r2.get_vertices()
     
     overlap = inf
     
     for shape in range(2):
          
          if shape == 1:
               rect1 = r2.get_vertices()
               rect2 = r1.get_vertices()
          
          for i in range(4):
               b = (i+1)%4
               axisProj = pygame.Vector2(-(rect1[b].y - rect1[i].y),(rect1[b].x - rect1[i].x))
               d = sqrt(axisProj.x * axisProj.x + axisProj.y * axisProj.y)
               axisProj /= d
               min_r1 , max_r1 = inf , -inf
               
               for h in range(4):
				
                    q = (rect1[h].x * axisProj.x + rect1[h].y * axisProj.y)
                    min_r1 = min(min_r1, q)
                    max_r1 = max(max_r1, q)
               
               min_r2 , max_r2 = inf , -inf
               
               for f in range(4):
				
                    q = (rect2[f].x * axisProj.x + rect2[f].y * axisProj.y)
                    min_r2 = min(min_r2, q)
                    max_r2 = max(max_r2, q)
               
               overlap = min(min(max_r1, max_r2) - max(min_r1, min_r2), overlap)
               
               if (not (max_r2 >= min_r1 and max_r1 >= min_r2)):
                    return

     d = pygame.Vector2(r2.pos.x - r1.pos.x , r2.pos.y - r1.pos.y)
     s = sqrt(d.x**2 + d.y**2)
     r1.pos.x -= overlap * d.x / s
     r1.pos.y -= overlap * d.y / s
				

async def diag_collision(r1 : pygame.FRect, r2 : pygame.FRect):
     
     rect1 = r1.get_vertices()
     rect2 = r2.get_vertices()
     
     collision_infos = {"rect1":[False , False , False , False],"rect2":[False , False , False , False]}
     
     for i in range(2):
          
          if i == 1:
               rect1 = r2.get_vertices()
               rect2 = r1.get_vertices()
               
          for v in range(4):
               
               line_r1s = r1.pos if i == 0 else r2.pos
               line_r1e = rect1[v]
               
               move_amount = pygame.Vector2(0,0)
               
               for s in range(4):
                    
                    line_r2s = rect2[s]
                    line_r2e = rect2[(s + 1) % 4]
                    
                    h = (line_r2e.x - line_r2s.x) * (line_r1s.y - line_r1e.y) - (line_r1s.x - line_r1e.x) * (line_r2e.y - line_r2s.y)
                    if h != 0:
                         t1 = ((line_r2s.y - line_r2e.y) * (line_r1s.x - line_r2s.x) + (line_r2e.x - line_r2s.x) * (line_r1s.y - line_r2s.y)) / h if h != 0 else 0
                         t2 = ((line_r1s.y - line_r1e.y) * (line_r1s.x - line_r2s.x) + (line_r1e.x - line_r1s.x) * (line_r1s.y - line_r2s.y)) / h if h != 0 else 0
                         
                         if (t1 > 0.0 and t1 < 1.0 and t2 > 0.0 and t2 < 1.0):					
                              move_amount.x += (1.0 - t1) * (line_r1e.x - line_r1s.x)
                              move_amount.y += (1.0 - t1) * (line_r1e.y - line_r1s.y)	
                              
                              collision_infos[f"rect{i+1}"][v] = True
               
               if i == 0:
                    r1.pos.x += move_amount.x * (-1)
                    r1.pos.y += move_amount.y * (-1)	
               else:
                    r1.pos.x += move_amount.x
                    r1.pos.y += move_amount.y
     
     return collision_infos
import pygame
import asyncio

from math import *
from pygame.locals import *
from scripts.form import *

class Player():
     
     def __init__(self , pos):
          self.rect = FloatRect(pygame.Vector2(pos) , pygame.Vector2(8,12))
          self.keys = {"left":False , "right":False , "up":False , "down":False}
          self.collision_side = {"left":False , "right":False , "top":False , "bottom":False}
          self.n_gravity = 0.15
          self.velocity_y = 0
          self.speed = 1.75
          self.jump_amount = 4.5
          self.air_time = 0
          self.current_movement = pygame.Vector2(0,0)
          
          self.texture = pygame.Surface([8 , 12])
          self.texture.fill([123 , 45 , 234])
          self.chunk_pos = [int(self.rect.x // 32) , int(self.rect.y // 32)]
          self.map_pos = [int((self.rect.x + self.rect.size.x / 2) / (8*44)),int((self.rect.y + self.rect.size.y / 2) / (8*32))]
     
     def reset_keys(self):
          for key in self.keys:
               self.keys[key] = False
     
     def update(self , dt , max_fps=60):
          
          self.chunk_pos = [int(self.rect.x // 32) , int(self.rect.y // 32)]
          self.map_pos = [int((self.rect.x + self.rect.size.x / 2) / (8*44)),int((self.rect.y + self.rect.size.y / 2) / (8*32))]
          
          self.air_time += 1
          self.velocity_y = min(self.velocity_y + self.n_gravity * dt * max_fps , 5)
          
          movement = pygame.Vector2(0 , self.velocity_y)
          
          if(self.keys["left"]):
               movement.x -= self.speed
          elif(self.keys["right"]):
               movement.x += self.speed
          
          movement *= dt * max_fps
          movement.x = min(movement.x , 3)
          movement.y = min(movement.y , 8)
          self.current_movement = movement
          # print(self.rect.pos)
     
     def update_after_moved(self):
          if (self.collision_side["bottom"]):
               self.air_time = 0
               self.velocity_y = 0
          if (self.collision_side["top"]):
               self.velocity_y = 1
     
     def collision(self , rects):
          
          colliders = []
          for collider in rects:
               if collide_rect(self.rect , collider.rect):
                    colliders.append(collider)
          
          return colliders
     
     async def move(self , rects):
          
          self.rect.pos.x += self.current_movement.x
          collision_side = {"left":False , "right":False , "top":False , "bottom":False}
          collided = self.collision(rects)
          for collider in collided:
               if (collider.type == "block"):
                    if (self.current_movement.x < 0):
                         self.rect.pos.x = collider.rect.x + collider.rect.size.x
                         collision_side["left"] = True
                    elif (self.current_movement.x > 0):
                         self.rect.x = collider.rect.pos.x - self.rect.size.x
                         collision_side["right"] = True
          
          self.rect.pos.y += self.current_movement.y
          collided = self.collision(rects)
          
          for collider in collided:
               if (collider.type == "block"):
                    if (self.current_movement.y < 0):
                         self.rect.pos.y = collider.rect.y + collider.rect.size.y
                         collision_side["top"] = True
                    elif (self.current_movement.y > 0):
                         self.rect.pos.y = collider.rect.y - self.rect.size.y
                         collision_side["bottom"] = True
               elif (collider.type == "platform"):
                    if (self.rect.bottom - self.current_movement.y <= collider.rect.y and self.current_movement.y > 0):
                         self.rect.pos.y = collider.rect.y - self.rect.size.y
                         collision_side["bottom"] = True
          
          
          self.collision_side = collision_side
          
     def event_handler(self , event):
          
          if event.type == KEYDOWN:
               if event.key == K_d:
                    self.keys["right"] = True
               if event.key == K_q:
                    self.keys["left"] = True
               if event.key == K_s:
                    if (self.air_time <= 4):
                         self.velocity_y = -(self.jump_amount)
          elif event.type == KEYUP:
               if event.key == K_d:
                    self.keys["right"] = False
               if event.key == K_q:
                    self.keys["left"] = False
     
     def display(self , screen , scroll):
          
          screen.blit(self.texture , [self.rect.pos.x - scroll[0] , self.rect.pos.y - scroll[1]])
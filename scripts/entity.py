import pygame
import asyncio

from math import *
from pygame.locals import *
from scripts.form import *
from scripts.particles import *
from scripts.animation import *
from scripts.unclassed_functions import *
from random import *
from copy import *

class Sprite():
     
     def __init__(self , pos , box_size):
          self.rect = FloatRect(pos , box_size)
          self.surface = pygame.Surface([box_size.x , box_size.y])
     
     def update(self , dt , max_fps=60):
          pass

     def evnt_handler(self , event : pygame.event.Event):
          pass

     def display(self , surface , offset=pygame.Vector2(0,0)):
          surface.blit(self.surface , [self.rect.x - offset.x , self.rect.y - offset.y])

class Player():
     
     def __init__(self , pos):
          self.collider = Collider(FloatRect(pos , pygame.Vector2(8,12)) , "block")
          self.keys = {"left":False , "right":False , "dash":False}
          self.dash_direction = "RIGHT"
          self.collision_side = {"left":False , "right":False , "top":False , "bottom":False}
          self.n_gravity = 0.1
          self.velocity = pygame.Vector2(0,0)
          self.speed = 1
          self.jump_amount = 2.8
          self.air_time = 0
          self.current_movement = pygame.Vector2(0,0)
          self.dead = False
          self.kinematic = False
          self.on_moving_platform = False
          self.flip = False
          
          texture = pygame.Surface([20 , 12])
          texture.fill([123 , 45 , 234])
          self.current_texture = texture
          
          self.chunk_pos = [int(self.rect.x // 32) , int(self.rect.y // 32)]
          self.map_pos = [int((self.rect.x + self.rect.size.x / 2) / (8*44)),int((self.rect.y + self.rect.size.y / 2) / (8*32))]
          
          self.sl_size = [80 , 80]
          
          self.light = pygame.image.load("./assets/light.png").convert_alpha()
          self.light = pygame.transform.scale(self.light , [80 , 80])
          
          self.light = mult_image(self.light , [100 , 100 , 100])
          
          self.anim_manager = AnimationManager("./assets/player/animations/")
          self.current_anim = None
          
          self.dash_timer = 0
          self.dash_duration = 0.2
          
          self.img_scale = pygame.Vector2(1,1)
     
     def set_action(self , id):
          
          if self.current_anim == None or id != self.current_anim.data.id != id:
               self.current_anim = self.anim_manager.get(id)     
     
     @property
     def rect(self):
          return self.collider.rect
     
     def reset_keys(self):
          for key in self.keys:
               self.keys[key] = False
     
     def update_lights(self , timer):
          self.sl_size = [80 + sin(timer)*15 , 80 + sin(timer)*15]
     
     def update(self , dt , max_fps=60):
          
          self.chunk_pos = [int(self.rect.x // 32) , int(self.rect.y // 32)]
          self.map_pos = [int((self.rect.x + self.rect.size.x / 2) / (8*44)),int((self.rect.y + self.rect.size.y / 2) / (8*32))]
          
          try:
               self.collider.set_on_moving_platform(False)
          except:
               pass
          self.air_time += 1
          if not self.keys["dash"]:
               self.velocity.y = min(self.velocity.y + self.n_gravity * dt * max_fps , 5)
          else:
               self.velocity.y = 0

          if not self.keys["dash"]:
               if(self.keys["left"]):
                    self.dash_direction = "LEFT"
                    self.velocity.x = -(abs(self.velocity.x) + dt * max_fps * .1 * (self.speed - abs(self.velocity.x)))
               elif(self.keys["right"]):
                    self.dash_direction = "RIGHT"
                    self.velocity.x = (abs(self.velocity.x) + dt * max_fps * .1 * (self.speed - abs(self.velocity.x)))
               else:
                    self.velocity.x *= 0.5
          elif self.keys["dash"]:
               self.dash_timer += dt
               if self.dash_direction == "LEFT":
                    self.velocity.x = min((-5 * ((self.dash_duration - self.dash_timer)/self.dash_duration)) , 0)
               elif self.dash_direction == "RIGHT":
                    self.velocity.x = max((5 * ((self.dash_duration - self.dash_timer)/self.dash_duration)) , 0)
               elif self.dash_direction == "UP":
                    self.velocity.y = min((-5 * ((self.dash_duration - self.dash_timer)/self.dash_duration)) , 0)
               if self.dash_duration - self.dash_timer <= 0:
                    self.keys["dash"] = False
                    self.dash_timer = 0
                    
          if self.velocity.y < 0:
               self.dash_direction = "UP"
          
          if self.velocity.x < 0:
               self.flip = True
          elif self.velocity.x > 0:
               self.flip = False
          
          movement = copy(self.velocity) * dt * max_fps
          movement.x = max(min(movement.x , 7),-7)
          movement.y = max(min(movement.y , 1.4),-7)
          
          self.current_movement = movement
          # print(self.current_movement)
          # print(self.rect.pos)
          
          if self.current_anim != None:
               self.current_anim.play(dt)
     
     def update_after_moved(self):
          if (self.collision_side["bottom"]):
               self.air_time = 0
               self.velocity.y = 0
          if (self.collision_side["top"]):
               self.velocity.y = 1
          if (self.collision_side["top"] and self.collision_side["bottom"] ):
               self.dead = True
          
          if self.velocity.y >= 0.0:
               if not self.collision_side["right"] and not self.collision_side["left"] and (-0.5 >= round(self.velocity.x , 1) or round(self.velocity.x , 1) >= 0.5):
                    self.set_action("running")
               elif round(self.velocity.x , 1) == 0:
                    self.set_action("idle")
               else:
                    self.current_anim = None
                    
          if self.current_anim != None:
               self.current_texture = self.current_anim.get_current_img(self.flip)
     
     def collision(self , rects):
          
          colliders = []
          for collider in rects:
               if self.collider.collide(collider):
                    colliders.append(collider)
          
          return colliders
     
     def move(self , rects):
          
          self.rect.pos.x += self.current_movement.x
          collision_side = {"left":False , "right":False , "top":False , "bottom":False}
          if not self.kinematic:
               collided = self.collision(rects)
               for collider in collided:
                    if (collider.type == "block"):
                         if (self.current_movement.x < 0):
                              self.rect.pos.x = collider.rect.x + collider.rect.size.x
                              collision_side["left"] = True
                         elif (self.current_movement.x > 0):
                              self.rect.x = collider.rect.pos.x - self.rect.size.x
                              collision_side["right"] = True
                    elif (collider.type == "trap"):
                         self.dead = True
          
          self.rect.pos.y += self.current_movement.y
          if not self.kinematic:
               collided = self.collision(rects)
               
               for collider in collided:
                    if (collider.type == "block"):
                         if (self.current_movement.y < 0):
                              self.rect.pos.y = collider.rect.y + collider.rect.size.y
                              collision_side["top"] = True
                         elif (self.current_movement.y > 0):
                              if not self.collider.on_moving_platform and collider.move_above:
                                   self.collider.set_on_moving_platform(True , collider)
                              self.rect.pos.y = collider.rect.y - self.rect.size.y
                              collision_side["bottom"] = True
                    elif (collider.type == "platform"):
                         if (floor(self.rect.bottom - self.current_movement.y) <= collider.rect.y and self.current_movement.y > 0):
                              if not self.collider.on_moving_platform and collider.move_above:
                                   self.collider.set_on_moving_platform(True , collider)
                              self.rect.pos.y = collider.rect.y - self.rect.size.y
                              collision_side["bottom"] = True
                    elif (collider.type == "trap"):
                         self.dead = True
          
          
          self.collision_side = collision_side
          
     def event_handler(self , event):
          
          if event.type == KEYDOWN:
               if event.key == K_d:
                    self.keys["right"] = True
               if event.key == K_q:
                    self.keys["left"] = True
               if event.key == K_z:
                    if (self.air_time <= 4):
                         self.velocity.y = -(self.jump_amount)
          elif event.type == KEYUP:
               if event.key == K_d:
                    self.keys["right"] = False
               if event.key == K_q:
                    self.keys["left"] = False
               if event.key == K_s:
                    self.keys["dash"] = True
                    
     def display_light(self , surface : pygame.Surface , offset=pygame.Vector2(0,0)):
          light_size = pygame.Vector2(self.sl_size)
          light_offset = offset - (self.rect.size / 2 - light_size / 2)
          surface.blit(pygame.transform.scale(self.light , self.sl_size) , [self.rect.x - light_offset.x , self.rect.y - light_offset.y] , special_flags=BLEND_RGB_ADD)
     
     def display(self , surface : pygame.Surface , offset=pygame.Vector2(0,0)):
          final_texture = pygame.transform.scale(self.current_texture , [self.current_texture.get_width() * self.img_scale.x , self.current_texture.get_height() * self.img_scale.y])
          text_size = final_texture.get_size()
          text_offset = self.rect.pos - offset + pygame.Vector2(self.rect.size.x / 2 - text_size[0] / 2 , self.rect.size.y - text_size[1])
          surface.blit(final_texture , text_offset)
     

class Book(Sprite):
     
     def __init__(self , pos , box_size):
          super().__init__(pos , box_size)
          self.surface = pygame.image.load("./assets/objects/book.png")
          self.anim_offset = pygame.Vector2(0,0)
          self.anim_dir = True
          self.anim_timer = 0
          
          self.particle_data = Particle_data()
          self.particle_data.set_intervall("pos" , self.rect.pos , self.rect.pos)
          self.particle_data.set_intervall("angle" , 0 , 360)
          self.particle_data.set_intervall("speed" , 1.6 , 2)
          self.particle_data.set_intervall("life_time" , 0.8 , 1)
          self.particle_data.speed_multiplicator = 0.94
          
          p_surfaces = []
          colors = [[207 , 87 , 60],[167 , 48 , 48],[222 , 158 , 65]]
          
          for i in range(2):
               surf = pygame.Surface([1,1])
               surf.fill(colors[i])
               p_surfaces.append(surf)
          
          self.particle_data.particle_surfaces = p_surfaces
          self.part_system = Particle_system()
          self.part_timer = 0
          
          self.light = pygame.image.load("./assets/light.png").convert_alpha()
          self.light = pygame.transform.scale(self.light , [128 , 128])
          
          self.light = mult_image(self.light , [180]*3)
          self.light = mult_image(self.light , [randint(0 , 255), randint(0 , 255), randint(0 , 255)])
          # self.light = mult_image(self.light , [10]*3)
          
          self.caught = False
          self.to_remove = False
          # light alpha
          self.scale_coef = 1
          self.la = 0
          self.remove_timer = 0
          self.remove_duration = 1
          
     def is_caught(self):
          self.caught = True
          self.part_system.spawnparticles(100 , self.particle_data , circular=True)
      
     def update(self , dt , max_fps=60):
          super().update(dt , max_fps)
          self.part_system.update(dt , max_fps)
          if not self.caught:
               self.anim_timer += dt

               self.part_timer += 1
               
               if self.part_timer % 10 == 0:
                    self.part_system.spawnparticles(2 , self.particle_data)
                    self.part_timer = 0
               if 0.2 - self.anim_timer <= 0:
                    self.anim_timer = 0
                    self.anim_offset.y += (1 if self.anim_dir else -1)
               
               if self.anim_offset.y == 2 or self.anim_offset.y == -2:
                    self.anim_dir = False if self.anim_dir else True
                    self.anim_timer = 0
                    self.anim_offset.y += (1 if self.anim_dir else -1)
          else:
               self.remove_timer += dt
               self.scale_coef -= (1/self.remove_duration) * dt
               if self.remove_duration - self.remove_timer <= 0:
                    self.to_remove = True
                    self.remove_timer = 0
     
     def display_light(self , surface : pygame.Surface , offset=pygame.Vector2(0,0)):
          light_size = pygame.Vector2(self.light.get_size())
          if self.caught:
               light_size = pygame.Vector2([self.light.get_width()*self.scale_coef , self.light.get_height()*self.scale_coef])
               light_offset = offset + self.anim_offset - (self.rect.size / 2 - light_size / 2)
               surface.blit(pygame.transform.scale(self.light , light_size) , [self.rect.x - light_offset.x , self.rect.y - light_offset.y] , special_flags=BLEND_RGB_ADD)
          else:
               light_offset = offset + self.anim_offset - (self.rect.size / 2 - light_size / 2)
               surface.blit(self.light , [self.rect.x - light_offset.x , self.rect.y - light_offset.y] , special_flags=BLEND_RGB_ADD)
     
     def display(self , surface : pygame.Surface , offset):
          surf_size = pygame.Vector2(self.surface.get_size())
          text_offset = offset+self.anim_offset-(self.rect.size / 2 - surf_size / 2)
          self.part_system.display(surface ,offset-self.rect.size / 2)
          if not self.caught:
               super().display(surface , text_offset)
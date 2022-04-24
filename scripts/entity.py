import pygame
import asyncio

from math import *
from pygame.locals import *
from scripts.form import *
from scripts.particles import *
from scripts.animation import *
from scripts.text import Font, Text
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
          self.keys = {"left":False , "right":False , "up":False , "down":False}
          self.dash_direction = "RIGHT"
          self.collision_side = {"left":False , "right":False , "top":False , "bottom":False}
          self.n_gravity = 0.08
          self.velocity = pygame.Vector2(0,0)
          self.speed = 1
          self.jump_amount = 2.7
          self.air_time = 0
          self.current_movement = pygame.Vector2(0,0)
          self.dead = False
          self.kinematic = False
          self.on_moving_platform = False
          self.flip = False
          self.mode = 0
          
          texture = pygame.Surface([20 , 12])
          texture.fill([123 , 45 , 234])
          self.current_texture = texture
          
          self.chunk_pos = [int(self.rect.x // 32) , int(self.rect.y // 32)]
          self.map_pos = [int((self.rect.x + self.rect.size.x / 2) / (8*44)),int((self.rect.y + self.rect.size.y / 2) / (8*32))]
          
          self.sl_size = [80 , 80]
          
          self.light = pygame.image.load("./assets/light.png").convert_alpha()
          self.light = pygame.transform.scale(self.light , [80 , 80])
          
          self.light = mult_image(self.light , [100 , 100 , 100])
          
          #animation variables
          self.anim_manager = AnimationManager("./assets/player/animations/")
          self.player_orb_t = pygame.image.load("./assets/player/player_orb.png").convert_alpha()
          self.current_anim = None
          
          self.timers = {}
          
          # Dash variables
          self.dash_amount = 50
          self.distance_traveled = 0
          self.dash_speed = 10
          
          self.img_scale = pygame.Vector2(1,1)
          
          self.books = 0
     
     def set_action(self , id):
          
          if self.current_anim == None or id != self.current_anim.data.id != id:
               self.current_anim = self.anim_manager.get(id)  
     
     def set_hitbox(self , size : pygame.Vector2):
          self.rect.pos += self.rect.size / 2 - size / 2
          self.rect.size = size   
     
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
          
          # if the player is on a platform , update the player position
          try:
               self.collider.set_on_moving_platform(False)
          except:
               pass
          
          # gravity
          self.air_time += 1
          if self.mode == 0:
               self.velocity.y = min(self.velocity.y + self.n_gravity * dt * max_fps , 5)
               # basic movements
               if(self.keys["left"]):
                    self.dash_direction = "LEFT"
                    self.velocity.x = -(abs(self.velocity.x) + dt * max_fps * .1 * (self.speed - abs(self.velocity.x)))
               elif(self.keys["right"]):
                    self.dash_direction = "RIGHT"
                    self.velocity.x = (abs(self.velocity.x) + dt * max_fps * .1 * (self.speed - abs(self.velocity.x)))
               else:
                    self.velocity.x *= 0.5
          elif self.mode == 1:
               distance_remaining = self.dash_amount - self.distance_traveled
               distance_remaining_at_mid = max(self.distance_traveled - self.dash_amount / 2 , 0)
               # print(self.img_scale)
               # dashing scale effect code
               if self.dash_amount / 2 - self.distance_traveled >= 0:
                    if not self.dash_direction == "UP":
                         self.img_scale.x = 1 + 2 * min(self.distance_traveled / (self.dash_amount / 2), 1)
                         self.img_scale.y = 1 - 0.9 * min(self.distance_traveled / (self.dash_amount / 2), 1)
                    else:
                         self.img_scale.x = 1 - 0.9 * min(self.distance_traveled / (self.dash_amount / 2), 1)
                         self.img_scale.y = 1 + 2 * min(self.distance_traveled / (self.dash_amount / 2), 1)
               else:
                    if not self.dash_direction == "UP":
                         self.img_scale.x = 3 - 2 * min(distance_remaining_at_mid / (self.dash_amount / 2), 1)
                         self.img_scale.y = 0.1 + 0.9 * min(distance_remaining_at_mid / (self.dash_amount / 2), 1)
                    else:
                         self.img_scale.x = 0.1 + 0.9 * min(distance_remaining_at_mid / (self.dash_amount / 2), 1)
                         self.img_scale.y = 3 - 2 * min(distance_remaining_at_mid / (self.dash_amount / 2), 1)
               
               # dashing movement
               if self.dash_direction == "LEFT":
                    self.velocity.x = -self.dash_speed * max(distance_remaining / (self.dash_amount), 0.05)  * dt * max_fps
               elif self.dash_direction == "RIGHT":
                    self.velocity.x = self.dash_speed * max(distance_remaining / (self.dash_amount), 0.05) * dt * max_fps
               elif self.dash_direction == "UP":
                    self.velocity.y = -self.dash_speed * max(distance_remaining / (self.dash_amount), 0.05) * dt * max_fps
               
               self.distance_traveled += max(min(self.dash_speed * max(distance_remaining / (self.dash_amount), 0.05) * dt**2 * max_fps**2 , 7) , -7)
               
               if self.distance_traveled - self.dash_amount >= 0:
                    self.img_scale.x = self.img_scale.y = 1
                    self.slow_mode = True
                    self.mode = 0
                    self.distance_traveled = 0
                    self.velocity = pygame.Vector2(0,0)
          elif self.mode == 2:
               if(self.keys["left"]):
                    self.velocity.y = 0
                    self.velocity.x = -(abs(self.velocity.x) + dt * max_fps * .1 * (self.speed - abs(self.velocity.x)))
               elif(self.keys["right"]):
                    self.velocity.y = 0
                    self.velocity.x = (abs(self.velocity.x) + dt * max_fps * .1 * (self.speed - abs(self.velocity.x)))
               elif(self.keys["up"]):
                    self.velocity.x = 0
                    self.velocity.y = -(abs(self.velocity.y) + dt * max_fps * .1 * (self.speed - abs(self.velocity.y)))
               elif(self.keys["down"]):
                    self.velocity.x = 0
                    self.velocity.y = (abs(self.velocity.y) + dt * max_fps * .1 * (self.speed - abs(self.velocity.y)))
               else:
                    self.velocity *= 0.5
                    
          if self.velocity.y < 0:
               self.dash_direction = "UP"
          
          if self.velocity.x < 0:
               self.flip = True
          elif self.velocity.x > 0:
               self.flip = False
          
          movement = copy(self.velocity)
          movement *= dt * max_fps
          movement.x = max(min(movement.x , 7),-7)
          movement.y = max(min(movement.y , 2.5 if not self.mode == 2 else 7),-7)
          
          self.current_movement = movement
          
          if self.current_anim != None:
               self.current_anim.play(dt , max_fps)
     
     def update_after_moved(self):
          if (self.collision_side["bottom"]):
               self.air_time = 0
               self.velocity.y = 0
          if (self.collision_side["top"]) and not self.mode == 2:
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
                    
          if self.current_anim != None and self.mode != 2:
               self.current_texture = self.current_anim.get_current_img(self.flip)
          elif self.mode == 2:
               self.current_texture = self.player_orb_t
               
     
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
                    
     def display_light(self , surface : pygame.Surface , offset=pygame.Vector2(0,0)):
          light_size = pygame.Vector2(self.sl_size)
          light_offset = offset - (self.rect.size / 2 - light_size / 2)
          surface.blit(pygame.transform.scale(self.light , self.sl_size) , [self.rect.x - light_offset.x , self.rect.y - light_offset.y] , special_flags=BLEND_RGB_ADD)
     
     def display(self , surface : pygame.Surface , offset=pygame.Vector2(0,0)):
          final_texture = pygame.transform.scale(self.current_texture , [self.current_texture.get_width() * self.img_scale.x , self.current_texture.get_height() * self.img_scale.y])
          text_size = final_texture.get_size()
          text_offset = self.rect.pos - offset + pygame.Vector2(self.rect.size.x / 2 - text_size[0] / 2 , self.rect.size.y - text_size[1] if text_size[1] > self.rect.size.y else self.rect.size.y / 2 - text_size[1] / 2)
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


class Bookshelf(Sprite):
     
     def __init__(self , pos):
          super().__init__(pos , pygame.Vector2(32 , 48))
          self.texture = pygame.image.load("./assets/objects/bookshelf.png").convert_alpha()
          self.shadow = self.texture.copy()
          self.shadow.fill([0,0,0,128] , special_flags=BLEND_RGBA_MULT)
          
          self.shadow_scale = [1 , 1]
          self.is_colliding = False
          self.scale_timer = 0
          
          self.n_books = 0
          self.books_needed = 5
          
          font = Font("./assets/fonts/small_font.png" , [255 , 255 , 255])
          
          self.book_text = Text(font , f"0 / {self.books_needed}")
          self.book_text.pos = self.rect.pos + pygame.Vector2(self.rect.size.x / 2 - self.book_text.size.x / 2 , -self.book_text.size.y - 10)
     
     def update(self , player : Player , dt , max_fps=60):
          if collide_rect(self.rect , player.rect):
               self.is_colliding = True
               self.n_books += player.books
               player.books = 0
               self.book_text.set_string(f"{self.n_books} / {self.books_needed}")
               self.book_text.pos = self.rect.pos + pygame.Vector2(self.rect.size.x / 2 - self.book_text.size.x / 2 , -self.book_text.size.y - 10)
     
          else:
               self.is_colliding = False
               
          if self.is_colliding:
               if self.scale_timer <= 1:
                    self.scale_timer += dt
                    self.shadow_scale = [1 + 0.4 * (self.scale_timer / 1)]*2       
          else:
               if self.scale_timer >= 0:
                    self.scale_timer -= dt
                    self.shadow_scale = [1 + 0.4 * (self.scale_timer / 1)]*2  
     
          
     
     def display(self , surface : pygame.Surface , offset=pygame.Vector2(0,0)):
          shadow = pygame.transform.scale(self.shadow , [self.shadow.get_width() * self.shadow_scale[0] , self.shadow.get_height() * self.shadow_scale[1]])
          shadow_offset = self.rect.size / 2 - pygame.Vector2(shadow.get_size()) / 2
          
          surface.blit(shadow , [self.rect.x - offset.x + shadow_offset.x , self.rect.y - offset.y + shadow_offset.y])
          self.book_text.display(surface , offset=offset)
          surface.blit(self.texture , [self.rect.x - offset.x , self.rect.y - offset.y])
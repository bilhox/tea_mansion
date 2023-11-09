import pygame

from math import *
from scripts.form import *
from scripts.particles import *
from scripts.animation import *
from scripts.text import Font, Text
from scripts.unclassed_functions import *
from random import *
from copy import *

# No documentation because I was too lazy to make one

class Sprite():
     
     def __init__(self , pos , box_size):
          self.rect = pygame.FRect(pos , box_size)
          self.surface = pygame.Surface([box_size.x , box_size.y])
     
     def update(self , dt , max_fps=60):
          pass

     def display(self , surface , offset=pygame.Vector2(0,0)):
          surface.blit(self.surface , [self.rect.x - offset.x , self.rect.y - offset.y])

class Player(Sprite):
     
     def __init__(self , pos):
          self.collider = Collider(pygame.FRect(pos , pygame.Vector2(8,12)) , "block")
          self.keys = {"left":False , "right":False , "up":False , "down":False}
          self.dash_direction = "RIGHT"
          self.collision_side = {"left":False , "right":False , "top":False , "bottom":False}
          self.n_gravity = 0.038
          self.velocity = pygame.Vector2(0,0)
          self.speed = .8
          self.jump_amount = 1.65
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
          self.map_pos = [int((self.rect.x + self.rect.width / 2) / (8*44)),int((self.rect.y + self.rect.height / 2) / (8*32))]
          
          self.sl_size = [80 , 80]
          
          self.light = pygame.image.load("./assets/light.png").convert_alpha()
          self.light = pygame.transform.scale(self.light , [80 , 80])
          
          self.light = mult_image(self.light , [100 , 100 , 100])
          
          #animation variables
          self.anim_manager = AnimationManager("./assets/player/animations/")
          self.player_orb_t = pygame.image.load("./assets/player/player_orb.png").convert_alpha()
          self.current_anim = None
          
          self.timers = {}
          self.collider_check = False
          
          # Dash variables
          self.able_to_dash = False
          self.dash_amount = 50
          self.distance_traveled = 0
          self.dash_speed = 10
          
          self.img_scale = pygame.Vector2(1,1)
          
          self.part_sys = Particle_system()
          self.part_img = pygame.Surface((1 , 1))
          self.part_img.fill([255]*3)
     
     
     def set_mode(self , mode):
          self.mode = mode
          self.img_scale = pygame.Vector2(1 , 1)
          if self.mode == 0:
               self.speed = .8
               self.collider_check = True
          elif self.mode == 2:
               self.set_hitbox(pygame.Vector2(6 , 6) , pygame.Vector2(self.rect.size) / 2 - pygame.Vector2(3 , 3))
               self.velocity = pygame.Vector2(0,0)
               self.speed = 0.6
          elif self.mode == 1:
               self.distance_traveled = 0
               self.velocity.y = 0
               self.able_to_dash = False
     
     def set_action(self , id):
          
          if self.current_anim == None or id != self.current_anim.data.id != id:
               self.current_anim = self.anim_manager.get(id)  
     
     def set_hitbox(self , size : pygame.Vector2 , offset=pygame.Vector2(0,0)):
          self.rect.topleft += offset
          self.rect.size = size   
     
     @property
     def rect(self):
          return self.collider.rect
     
     def reset_keys(self):
          for key in self.keys:
               self.keys[key] = False
     
     def spawn_particle(self , amt):
          
          if self.mode == 1:
               for _ in range(amt):
                    if self.dash_direction == "RIGHT":
                         motion = pygame.Vector2(randint(-20 , -15) , 0)
                    elif self.dash_direction == "LEFT":
                         motion = pygame.Vector2(randint(15 , 20) , 0)
                    self.part_sys.particles.append(Particle(
                         self.rect.topleft + (pygame.Vector2(0 , randint(1 , int(self.rect.height) - 1)) if not self.dash_direction == "UP" else pygame.Vector2(randint(1 , int(self.rect.width) - 1) , self.rect.height)) ,
                         motion , # mouvement
                         2 , # decay rate
                         [self.part_img].copy() , # particule images
                         0.6 , # duration 
                         color=[220 , 220 , 220] # color (optional)
                         ))
          elif self.mode == 2:
               angle = radians(randint(1 , 360))
               motion = pygame.Vector2(cos(angle) * randint(5 , 10) , sin(angle) * randint(5 , 10))
               self.part_sys.particles.append(Particle(
                    pygame.Vector2(self.rect.topleft) + pygame.Vector2(self.rect.size) / 2 ,
                    motion ,
                    .5 ,
                    [self.part_img].copy() , # particle imgs
                    random(), # duration
                    color=choice([[255, 202, 110] , [255, 186, 117]]) # color (optional)
               ))
     
     def update_lights(self , timer):
          self.sl_size = [80 + sin(timer)*15 , 80 + sin(timer)*15]
     
     def update(self , dt , max_fps=60):
          
          self.chunk_pos = [int(self.rect.x // 32) , int(self.rect.y // 32)]
          self.map_pos = [int((self.rect.x + self.rect.width / 2) / (8*44)),int((self.rect.y + self.rect.height / 2) / (8*32))]
          self.part_sys.update(dt)
          # if the player is on a platform , update the player position
          try:
               self.collider.set_on_moving_platform(False)
          except:
               pass
          
          # gravity
          self.air_time += 1
          if self.mode == 0:
               self.velocity.y = min(self.velocity.y + self.n_gravity * dt * max_fps , 3)
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
               self.spawn_particle(1)
               distance_remaining = self.dash_amount - self.distance_traveled
               distance_remaining_at_mid = max(self.distance_traveled - self.dash_amount / 2 , 0)
               # dashing scale effect code
               if self.dash_amount / 2 - self.distance_traveled >= 0:
                    self.img_scale.x = 1 + 2 * min(self.distance_traveled / (self.dash_amount / 2), 1)
                    self.img_scale.y = 1 - 0.9 * min(self.distance_traveled / (self.dash_amount / 2), 1)
               else:
                    self.img_scale.x = 3 - 2 * min(distance_remaining_at_mid / (self.dash_amount / 2), 1)
                    self.img_scale.y = 0.1 + 0.9 * min(distance_remaining_at_mid / (self.dash_amount / 2), 1)
               
               # dashing movement
               if self.dash_direction == "LEFT":
                    self.velocity.x = -self.dash_speed * max(distance_remaining / (self.dash_amount), 0.05)  * dt * max_fps
               elif self.dash_direction == "RIGHT":
                    self.velocity.x = self.dash_speed * max(distance_remaining / (self.dash_amount), 0.05) * dt * max_fps
               
               self.distance_traveled += max(min(self.dash_speed * max(distance_remaining / (self.dash_amount), 0.05) * dt**2 * max_fps**2 , 7) , -7)
               
               if self.distance_traveled - self.dash_amount >= 0:
                    self.img_scale.x = self.img_scale.y = 1
                    self.mode = 0
                    self.distance_traveled = 0
                    self.velocity = pygame.Vector2(0,0)
          elif self.mode == 2:
               if len(self.part_sys.particles) < 30:
                    self.spawn_particle(1)
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
               self.able_to_dash = True
          if (self.collision_side["top"]) and not self.mode == 2:
               self.velocity.y = abs(self.velocity.y)

          # Code for collision resolution when the player switch from orb mode to normal mode
          if self.collider_check:
               self.collider_check = False
               offset = pygame.Vector2(0 , 0)
               if self.collision_side["top"]:
                    offset.y = 3
               elif self.collision_side["bottom"]:
                    offset.y = -10
               elif self.collision_side["top"] and self.collision_side["bottom"]:
                    self.dead = True
               else:
                    offset.y = 0
               if self.collision_side["right"]:
                    offset.x = -1
               elif self.collision_side["left"]:
                    offset.x = 1
               elif self.collision_side["right"] and self.collision_side["left"]:
                    self.dead = True
               else:
                    offset.x = 0
               self.rect.topleft += offset
          
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
          
          if not self.collider_check:
               self.rect.x += self.current_movement.x
          else:
               self.set_hitbox(pygame.Vector2(8 , 6) , pygame.Vector2(self.rect.width / 2 - 4 , 0))
          collision_side = {"left":False , "right":False , "top":False , "bottom":False}
          if not self.kinematic:
               collided = self.collision(rects)
               for collider in collided:
                    if (collider.type == "block"):
                         
                         if not self.collider_check:
                              if (self.current_movement.x < 0):
                                   self.rect.left = collider.rect.right
                              elif (self.current_movement.x > 0):
                                   self.rect.right = collider.rect.left
                    
                         if self.rect.x < collider.rect.x:
                              collision_side["right"] = True
                         elif self.rect.x > collider.rect.x:
                              collision_side["left"] = True
                              
                    elif (collider.type == "trap"):
                         self.dead = True
          
          if not self.collider_check:
               self.rect.y += self.current_movement.y
          else:
               self.set_hitbox(pygame.Vector2(8 , 12) , pygame.Vector2(0 , 6))
               
          if not self.kinematic:
               collided = self.collision(rects)
               
               for collider in collided:
                    if (collider.type == "block"):
                         
                         if not self.collider_check:
                              if (self.current_movement.y < 0):
                                   self.rect.top = collider.rect.bottom
                              elif (self.current_movement.y > 0):
                                   if not self.collider.on_moving_platform and collider.move_above:
                                        self.collider.set_on_moving_platform(True , collider)
                                   self.rect.bottom = collider.rect.top
                              
                         if self.rect.y <= collider.rect.y:
                              collision_side["bottom"] = True
                         elif self.rect.y > collider.rect.y:
                              collision_side["top"] = True
                         
                              
                    elif (collider.type == "platform"):
                         if (floor(self.rect.bottom - self.current_movement.y) <= collider.rect.y and self.current_movement.y > 0):
                              if not self.collider.on_moving_platform and collider.move_above:
                                   self.collider.set_on_moving_platform(True , collider)
                              self.rect.y = collider.rect.y - self.rect.height
                              collision_side["bottom"] = True
                    elif (collider.type == "trap"):
                         self.dead = True
          
          
          self.collision_side = collision_side
                    
     def display_light(self , surface : pygame.Surface , offset=pygame.Vector2(0,0)):
          light_size = pygame.Vector2(self.sl_size)
          light_offset = offset - (pygame.Vector2(self.rect.size) / 2 - light_size / 2)
          surface.blit(pygame.transform.scale(self.light , self.sl_size) , [self.rect.x - light_offset.x , self.rect.y - light_offset.y] , special_flags=BLEND_RGB_ADD)
     
     def display(self , surface : pygame.Surface , offset=pygame.Vector2(0,0)):
          final_texture = pygame.transform.scale(self.current_texture , [self.current_texture.get_width() * self.img_scale.x , self.current_texture.get_height() * self.img_scale.y])
          text_size = final_texture.get_size()
          text_offset = self.rect.topleft - offset + pygame.Vector2(self.rect.width / 2 - text_size[0] / 2 , self.rect.height - text_size[1] if text_size[1] > self.rect.height else self.rect.height / 2 - text_size[1] / 2)
          self.part_sys.draw(surface , offset)
          surface.blit(final_texture , text_offset)
     

class Book(Sprite):
     
     def __init__(self , pos , box_size):
          super().__init__(pos , box_size)
          self.surface = pygame.image.load("./assets/objects/book.png")
          self.anim_offset = pygame.Vector2(0,0)
          self.anim_dir = True
          self.anim_timer = 0
          
          self.part_timer = 0
          
          self.light = pygame.image.load("./assets/light.png").convert_alpha()
          self.light = pygame.transform.scale(self.light , [100 , 100])
          
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
          
          self.part_sys = Particle_system()
          self.part_img = pygame.Surface((1 , 1))
          self.part_img.fill([255 , 255 , 255])

          self.part_colors = [
               [245, 141, 66],
               [247, 169, 74]
          ]
          
     def is_caught(self):
          self.caught = True
          
     def spawn_particles(self , amt):
          for _ in range(amt):
               angle = radians(randint(1 , 360))
               motion = pygame.Vector2(cos(angle) * randint(60 , 80) , sin(angle) * randint(60 , 80))
               self.part_sys.particles.append(Particle(pygame.Vector2(self.rect.topleft) + pygame.Vector2(self.rect.size) / 2 , motion , 1 , [self.part_img] , .5 , choice(self.part_colors)))

      
     def update(self , dt , max_fps=60):
          super().update(dt , max_fps)
          self.part_sys.update(dt)
          if not self.caught:
               self.anim_timer += dt * 10
               self.part_timer += dt
               
               if self.part_timer - 0.05 >= 0:
                    self.spawn_particles(1)
                    self.part_timer = 0
               
               if self.part_timer % 10 == 0:
                    self.part_timer = 0
               
               self.anim_offset.y = cos(self.anim_timer)
               
          else:
               self.remove_timer += dt
               self.scale_coef -= (1/self.remove_duration) * dt
               if self.remove_duration - self.remove_timer <= 0:
                    self.to_remove = True
                    self.remove_timer = 0
     
     def display_light(self , surface : pygame.Surface , offset=pygame.Vector2(0,0)):
          light_size = pygame.Vector2(self.light.get_size())
          if self.caught:
               light_size = pygame.Vector2([self.light.get_width() * max(self.scale_coef , 0) , self.light.get_height() * max(self.scale_coef , 0)])
               light_offset = offset + self.anim_offset - (pygame.Vector2(self.rect.size) / 2 - light_size / 2)
               surface.blit(pygame.transform.scale(self.light , light_size) , [self.rect.x - light_offset.x , self.rect.y - light_offset.y] , special_flags=BLEND_RGB_ADD)
          else:
               light_offset = offset + self.anim_offset - (pygame.Vector2(self.rect.size) / 2 - light_size / 2)
               surface.blit(self.light , [self.rect.x - light_offset.x , self.rect.y - light_offset.y] , special_flags=BLEND_RGB_ADD)
     
     def display(self , surface : pygame.Surface , offset):
          surf_size = pygame.Vector2(self.surface.get_size())
          text_offset = offset + self.anim_offset - (pygame.Vector2(self.rect.size) / 2 - surf_size / 2)
          self.part_sys.draw(surface , offset)
          if not self.caught:
               super().display(surface , text_offset)


class Bookshelf(Sprite):
     
     def __init__(self , pos , n_books):
          super().__init__(pos , pygame.Vector2(32 , 48))
          self.texture = pygame.image.load("./assets/objects/bookshelf.png").convert_alpha()
          self.shadow = self.texture.copy()
          self.shadow.fill([0,0,0,128] , special_flags=BLEND_RGBA_MULT)
          
          self.shadow_scale = [1 , 1]
          self.is_colliding = False
          self.scale_timer = 0
          self.full = False
          
          self.n_books = 0
          self.books_needed = n_books
          
          self.full_sound = pygame.mixer.Sound("./assets/sfx/bookshelf_full.wav")
          
          font = Font("./assets/fonts/small_font.png" , [255 , 255 , 255])
          
          self.book_text = Text(font , f"0 / {self.books_needed}")
          self.book_text.pos = self.rect.topleft + pygame.Vector2(self.rect.width / 2 - self.book_text.size.x / 2 , -self.book_text.size.y - 10)
     
     def update_text(self):
          
          self.book_text.set_string(f"{self.n_books} / {self.books_needed}" if not self.full else "full !")
          self.book_text.pos = self.rect.topleft + pygame.Vector2(self.rect.width / 2 - self.book_text.size.x / 2 , -self.book_text.size.y - 10)
     
     def deposit(self , book_carrying : list):
          if not self.full:
               self.n_books += len(book_carrying)
               if self.n_books >= self.books_needed:
                    self.full = True
                    self.full_sound.play()
               books_to_remove = len(book_carrying) - max(len(book_carrying) - self.books_needed , 0)
               del book_carrying[:books_to_remove]
               self.update_text()
               return books_to_remove
          
          return 0
     
     def update(self , dt , max_fps=60):
               
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
          shadow_offset = pygame.Vector2(self.rect.size) / 2 - pygame.Vector2(shadow.get_size()) / 2
          
          surface.blit(shadow , [self.rect.x - offset.x + shadow_offset.x , self.rect.y - offset.y + shadow_offset.y])
          self.book_text.display(surface , offset=offset)
          surface.blit(self.texture , [self.rect.x - offset.x , self.rect.y - offset.y])

class Power(Sprite):
     
     def __init__(self , pos , type):
          super().__init__(pos , pygame.Vector2(8 , 8))
          self.type = type
          self.timer = choice([0 , pi])
          self.reload_timer = 0
          self.part_timer = 0
          self.floating_offset = pygame.Vector2(0,0)
          
          self.part_sys = Particle_system()
          self.part_img = pygame.Surface([1 , 1])
          
          self.textures = {"visible":None , "caught":pygame.image.load("./assets/powers/power_caught.png").convert_alpha()}
          
          if self.type == "dash":
               self.textures["visible"] = pygame.image.load("./assets/powers/dash_power.png").convert_alpha()
               self.part_img.fill([77, 115, 227])
          elif self.type == "orb":
               self.textures["visible"] = pygame.image.load("./assets/powers/orb_power.png").convert_alpha()
               self.part_img.fill([237, 160, 121])
          
          self.caught = False          
     
     def spawn_particles(self , amt):
          for _ in range(amt):
               angle = radians(randint(1 , 360))
               motion = pygame.Vector2(cos(angle) * randint(5 , 10) , sin(angle) * randint(5 , 10))
               self.part_sys.particles.append(Particle(pygame.Vector2(self.rect.topleft) + pygame.Vector2(self.rect.size) / 2 , motion , 1 , [self.part_img] , 0.8))
     
     def update(self , dt , max_fps=60):
          
          self.part_sys.update(dt)
          self.floating_offset.y = cos(self.timer)
          self.timer += dt * 10
          if not self.caught:
               self.part_timer += dt
               
               if self.part_timer - 0.05 >= 0:
                    self.spawn_particles(1)
                    self.part_timer = 0
          else:
               self.reload_timer += dt
               if 6 - self.reload_timer <= 0:
                    self.reload_timer = 0
                    self.caught = False
     
     def display(self, surface, offset=pygame.Vector2(0, 0)):
         
          self.part_sys.draw(surface , offset)
          if not self.caught:
               surface.blit(self.textures["visible"] , [self.rect.x - offset.x , self.rect.y - offset.y])
          else:
               surface.blit(self.textures["caught"] , [self.rect.x - offset.x , self.rect.y - offset.y])
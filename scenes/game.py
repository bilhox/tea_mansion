import pygame
import sys

from scenes.scene import *
from pygame.locals import *
from scripts.camera import *
from scripts.entity import *
from scripts.map import *
from scripts.text import *

class Game(Scene):
     
     def __init__(self , screen , scene_manager):
          
          super().__init__(screen , scene_manager)
          self.level = None
          self.camera = Camera([0,0] , [352 , 256])
          self.font = pygame.font.Font(None , 20)
          self.game_timer = 0
          self.death_timer = 0
          self.map_transition = False
          
          self.black_filter = pygame.Surface([self.camera.rect.size.x , self.camera.rect.size.y] , SRCALPHA)
          
          self.particle_system = Particle_system()
          
          self.bs_filter = pygame.Surface([self.camera.size.x , self.camera.size.y] , SRCALPHA)
          self.game_timer = 0

          self.images = []
          self.book_carrying = []
          self.power_timers = []
     
     def start(self):
          
          self.level = Level("./assets/levels/level_demo.json")
          self.tilemap = self.level.tilemap
          
          pygame.mouse.set_visible(False)
          self.player = Player(copy(self.tilemap.objects["player_spawn"]["coord"]))
          
          self.black_filter.fill([0,0,0,80])
          
          surf = pygame.Surface([7 , 7] , SRCALPHA)
          pygame.draw.circle(surf , [143 , 65 , 234] , [4,4] , 3)
          
          border = pygame.image.load("./assets/border_shadow.png").convert_alpha()
          
          self.bs_filter.blit(pygame.transform.scale(border , [self.camera.size.x , 12]) , [0 , self.camera.size.y - 8])
          self.bs_filter.blit(pygame.transform.rotate(pygame.transform.scale(border , [self.camera.size.y , 12]) , -90) , [-4 , 0])
          self.bs_filter.blit(pygame.transform.rotate(pygame.transform.scale(border , [self.camera.size.y , 12]) , 90) , [self.camera.size.x - 8 , 0])
          self.bs_filter.blit(pygame.transform.rotate(pygame.transform.scale(border , [self.camera.size.x , 12]) , 180) , [0 , -4])
          
          self.texts = {}
          
          s2font = Font("./assets/fonts/small_font.png" , [255 , 255 , 255])
          s2font.zoom = 2
          
          fps_text = Text(s2font , "FPS : 0")
          fps_text.pos = pygame.Vector2(6,6)
          
          levelmd_text = Text(s2font , "Level : " + self.level.name)
          levelmd_text.pos = pygame.Vector2(self.screen.get_width() - 6 , 6)
          levelmd_text.origin = pygame.Vector2(levelmd_text.size.x , 0)
          
          self.texts["fps"] = fps_text
          self.texts["levelmd"] = levelmd_text
          
          self.part_imgs = []
          img = pygame.Surface([5 , 5] , SRCALPHA)
          pygame.draw.circle(img , [96, 0, 156] , [3 , 3] , 2)
          self.part_imgs.append(img)
     
     def events(self):
          
          for event in pygame.event.get():
               if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
               if not self.map_transition and not self.player.dead and not self.scene_manager.transition:
                    if event.type == KEYDOWN:
                         if event.key == K_d:
                              self.player.keys["right"] = True
                         if event.key == K_q:
                              self.player.keys["left"] = True
                         if event.key == K_z:
                              self.player.keys["up"] = True
                              if (self.player.air_time <= 4):
                                   self.player.velocity.y = -(self.player.jump_amount)
                         if event.key == K_s:
                              self.player.keys["down"] = True
                              if self.player.mode == 0 and self.player.able_to_dash:
                                   self.player.set_mode(1)
                              
                    elif event.type == KEYUP:
                         if event.key == K_d:
                              self.player.keys["right"] = False
                         if event.key == K_q:
                              self.player.keys["left"] = False
                         if event.key == K_z:
                              self.player.keys["up"] = False
                         if event.key == K_s:
                              self.player.keys["down"] = False
                         if event.key == K_f:
                              if self.level.bookshelf.is_colliding:
                                   self.level.bookshelf.n_books += len(self.book_carrying)
                                   self.book_carrying = []
                                   self.level.bookshelf.update_text()
                         if event.key == K_p:
                              if self.player.mode == 2:
                                   self.player.set_mode(0)
               
     
     def update(self , time_infos):
          
          dt = time_infos["dt"]
          clock = time_infos["clock"]
          max_fps = time_infos["max_fps"]
          
          self.game_timer += dt
          self.black_filter.fill([0,0,0,80])
          self.camera.update(dt , max_fps)
          self.particle_system.update(dt)
          self.screen.fill([17 , 9 , 13])
          
          for power in self.power_timers:
               power["timer"] += dt
               if power["duration"] - power["timer"] <= 0:
                    if power["type"] == "orb":
                         self.player.set_mode(0)
                    self.power_timers.remove(power)
          
          #event loop
          self.events()
          
          self.tilemap.update_platforms(dt , max_fps)
          
          # Getting all colliders
          rects = []
          
          for y in range(-1 , 2):
               for x in range(-1 , 2):
                    try:
                         rects.extend(self.tilemap.collider_chunks[f"{self.player.chunk_pos[0]+x},{self.player.chunk_pos[1]+y}"])
                    except:
                         pass
          
          rects.extend(self.tilemap.get_platform_colliders())

          # Code for transition between rooms 
          if self.map_transition:
               # Interpolating makes a progressive slow effect
               camera_center = pygame.Vector2(self.player.map_pos[0]*8*44 , self.player.map_pos[1]*8*32)
               self.camera.pos = pygame.Vector2.lerp(self.camera.pos , camera_center , min(15*dt , 1))
          else:
               self.player.update(dt , max_fps)
               self.player.update_lights(self.game_timer)
               self.player.move(rects)
               self.player.update_after_moved()
          
          # See if the camera is in the right room , transition otherwise   
          if not self.player.dead and (not int(abs((self.player.map_pos[0]*8*44) - (self.camera.pos.x))) == 0 or not int(abs((self.player.map_pos[1]*8*32) - (self.camera.pos.y))) == 0):
               self.map_transition = True
               self.player.reset_keys()
          else:
               if self.map_transition:
                    self.camera.pos = pygame.Vector2(self.player.map_pos[0]*8*44 , self.player.map_pos[1]*8*32)
               self.map_transition = False
          
          # --------------------------------------------------------------------   
          # Player death stuff
          if self.player.dead:
               if self.death_timer == 0:
                    particle_burst(self.particle_system , self.player.rect.pos + self.player.rect.size / 2 , 40 , 80 , self.part_imgs , 0.6)
               self.death_timer += dt
               self.player.kinematic = True
               if (.6 - self.death_timer) <= 0:
                    self.death_timer = 0
                    self.player.rect.pos = copy(self.tilemap.objects["player_spawn"]["coord"])
                    self.player.kinematic = False
                    self.player.dead = False
                    self.player.set_mode(0)
                    for book in self.book_carrying:
                         book.caught = False
                         book.to_remove = False
                         book.scale_coef = 1
                         self.level.tilemap.books.append(book)
                    self.book_carrying = []
                    self.player.reset_keys()
          else:
               self.room_pos = f"{self.player.map_pos[0]},{self.player.map_pos[1]}"
          
          self.tilemap.update_books(dt , max_fps)
          
          # ---------------------------------------------------------------
          # update books and bookshelfs
          for book in self.tilemap.books:
               if not book.caught:
                    if collide_rect(book.rect , self.player.rect):
                         book.is_caught()
                         self.book_carrying.append(book)
               elif book.to_remove:
                    self.tilemap.books.remove(book)
          
          for book in self.tilemap.books:
               book.display_light(self.black_filter , self.camera.pos)
          for torch in self.tilemap.deco_objects:
               torch.display_light(self.black_filter , self.camera.pos)
               torch.update(dt , max_fps)
          
          self.level.bookshelf.update(dt , max_fps)
          
          
          if collide_rect(self.player.rect, self.level.bookshelf.rect):
               self.level.bookshelf.is_colliding = True
          else:
               self.level.bookshelf.is_colliding = False
          
          # -----------------------------------------------------------------
          # Powers code
          
          for power in self.level.tilemap.powers:
               if collide_rect(self.player.rect , power.rect) and not power.caught:
                    power.caught = True  
                    particle_burst(power.part_sys , copy(power.rect.pos) , 60 , 200 , [power.part_img] , 0.2 , n_angles=2)
                    if power.type == "dash":
                         self.player.able_to_dash = True
                    elif power.type == "orb":
                         self.player.set_mode(2)
                         self.power_timers.append( {"type":"orb" , "duration":4 , "timer":0} )
               power.update(dt)
          # -----------------------------------------------------------------
          
          # Display part
               
          if not self.player.dead:
               self.player.display_light(self.black_filter , self.camera.pos)
          
          
          self.tilemap.display_layer(self.camera.render_surf ,"background",chunk=self.room_pos,offset=self.camera.pos)
          self.tilemap.display_layer(self.camera.render_surf ,"background objects",chunk=self.room_pos,offset=self.camera.pos)
          for torch in self.tilemap.deco_objects:
               torch.display(self.camera.render_surf , self.camera.pos)
          
          self.tilemap.display_layer(self.camera.render_surf ,"foreground",chunk=self.room_pos,offset=self.camera.pos)
          
          self.level.bookshelf.display(self.camera.render_surf , self.camera.pos)
          if not self.player.dead:
               self.player.display(self.camera.render_surf , self.camera.pos)
               
          for power in self.tilemap.powers:
               power.display(self.camera.render_surf , self.camera.pos)
          
          self.tilemap.display_layer(self.camera.render_surf ,"platforms",chunk=self.room_pos,offset=self.camera.pos)
          self.tilemap.display_platforms(self.camera.render_surf , self.camera.pos)
          self.particle_system.draw(self.camera.render_surf , self.camera.pos)
          self.tilemap.display_books(self.camera.render_surf , self.camera.pos)
          self.camera.render_surf.blit(self.black_filter , [0,0])
          self.camera.render_surf.blit(self.bs_filter , [0,0])
          
          cam_pos = [
               self.screen.get_width() / 2 - self.camera.size.x,
               self.screen.get_height() / 2 - self.camera.size.y
          ]
          
          self.camera.display(self.screen , Rect(cam_pos,[704 , 512]))
          
          # -----------------------------------------------------------------
          # Finally , display texts that are out of the camera
          
          self.texts["fps"].set_string(f"FPS : {int(clock.get_fps())}")
          
          for text in self.texts.values():
               text.display(self.screen)
          
          for image in self.images:
               self.screen.blit(image[0] , [image[1].x , image[1].y])
          
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
          self.death_timer = 0
          self.map_transition = False
          
          self.black_filter = pygame.Surface([self.camera.rect.size.x , self.camera.rect.size.y] , SRCALPHA)
          self.black_filter.fill([0,0,0,80])
          
          self.particle_system = Particle_system()
          
          self.bs_filter = pygame.Surface([self.camera.size.x , self.camera.size.y] , SRCALPHA)
          
          border = pygame.image.load("./assets/border_shadow.png").convert_alpha()
          self.bs_filter.blit(pygame.transform.scale(border , [self.camera.size.x , 12]) , [0 , self.camera.size.y - 8])
          self.bs_filter.blit(pygame.transform.rotate(pygame.transform.scale(border , [self.camera.size.y , 12]) , -90) , [-4 , 0])
          self.bs_filter.blit(pygame.transform.rotate(pygame.transform.scale(border , [self.camera.size.y , 12]) , 90) , [self.camera.size.x - 8 , 0])
          self.bs_filter.blit(pygame.transform.rotate(pygame.transform.scale(border , [self.camera.size.x , 12]) , 180) , [0 , -4])
          
          self.game_timer = 0

          self.images = []
          self.book_carrying = []
          self.book_sorted = 0
          self.power_timers = []
          
          self.sounds = {}
          
          self.sounds["dash"] = pygame.mixer.Sound("./assets/sfx/dash.wav")
          self.sounds["jump"] = pygame.mixer.Sound("./assets/sfx/jump.wav")
          self.sounds["book_gathered"] = pygame.mixer.Sound("./assets/sfx/book_gathered.wav")
          self.sounds["end_game"] = pygame.mixer.Sound("./assets/sfx/bookshelf_full.wav")
          self.sounds["item_gathered"] = pygame.mixer.Sound("./assets/sfx/item_gathered.wav")

          for sound in self.sounds.values():
               sound.set_volume(0.1)
          
     def next_level(self):
          
          self.book_carrying.clear()
          self.book_sorted = 0
          self.power_timers.clear()
          
          try:
               self.level.load(self.level.current_level + 1)
          except IndexError as e:
               self.game_ended = True
               pygame.mouse.set_visible(True)
               self.sounds["end_game"].play()
               return
               
          self.tilemap = self.level.tilemap
          

          self.player.set_mode(0)
          self.player.velocity = pygame.Vector2(0,0)
          self.player.reset_keys()
          self.player.able_to_dash = False
          self.player.air_time = 0
          self.player.rect.pos = copy(self.tilemap.objects["player_spawn"]["coord"])
          self.camera.pos = pygame.Vector2(self.player.map_pos)*8
          self.camera.pos.x *= 44 ; self.camera.pos.y *= 32
          
          self.game_timer = 0
          self.texts["levelmd"].set_string("Level : " + self.level.name)
          self.texts["levelmd"].origin = pygame.Vector2(self.texts["levelmd"].size.x , 0)
          
          pygame.mixer.music.load("./assets/sfx/game.wav")
          pygame.mixer.music.play(loops=2000)
     
     def start(self):
          
          pygame.mixer.music.load("./assets/sfx/game.wav")
          pygame.mixer.music.play(loops=2000)
          
          self.level = Level_Manager("./assets/datas/level_demo.json")
          self.tilemap = self.level.tilemap
          
          pygame.mouse.set_visible(False)
          self.player = Player(copy(self.tilemap.objects["player_spawn"]["coord"]))
          self.camera.pos = pygame.Vector2(self.player.map_pos)*8
          self.camera.pos.x *= 44 ; self.camera.pos.y *= 32
          
          self.texts = {}
          
          sfont = Font("./assets/fonts/small_font.png" , [255 , 255 , 255])
          sfont.zoom = 2
          
          lfont = Font("./assets/fonts/large_font.png" , [255 , 255 , 255])
          lfont.zoom = 2
          
          fps_text = Text(sfont , "FPS : 0")
          fps_text.pos = pygame.Vector2(6,self.screen.get_height() - fps_text.size.y - 1)
          
          timer_text = Text(sfont , f"Time : {get_timestring(int(self.game_timer))}")
          timer_text.pos = pygame.Vector2(6,6)
          
          levelmd_text = Text(sfont , "Level : " + self.level.name)
          levelmd_text.pos = pygame.Vector2(self.screen.get_width() - 6 , 6)
          levelmd_text.origin = pygame.Vector2(levelmd_text.size.x , 0)
          
          thanks_text = Text(lfont , "Thanks for playing !")
          thanks_text.pos = pygame.Vector2(self.screen.get_width() / 2 , 200)
          thanks_text.origin = thanks_text.size / 2
          
          click_text = Text(sfont , "Click to continue ...")
          click_text.pos = pygame.Vector2(self.screen.get_width() / 2 , 500)
          click_text.origin = click_text.size / 2
          
          self.texts["fps"] = fps_text
          self.texts["levelmd"] = levelmd_text
          self.texts["game timer"] = timer_text
          self.texts["thanks"] = thanks_text
          self.texts["click"] = click_text
          
          self.part_imgs = []
          img = pygame.Surface([5 , 5] , SRCALPHA)
          pygame.draw.circle(img , [96, 0, 156] , [3 , 3] , 2)
          self.part_imgs.append(img)
          
          self.game_ended = False
          
          self.thanks_timer = 0
          self.game_timer = 0
     
     def events(self):
          
          for event in pygame.event.get():
               if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
               if not self.map_transition and not self.player.dead and not self.scene_manager.transition and not self.game_ended:
                    if event.type == KEYDOWN:
                         if event.key == K_d:
                              self.player.keys["right"] = True
                         if event.key == K_q:
                              self.player.keys["left"] = True
                         if event.key == K_z:
                              self.player.keys["up"] = True
                              if (self.player.air_time <= 4):
                                   self.sounds["jump"].play()
                                   self.player.velocity.y = -(self.player.jump_amount)
                         if event.key == K_s:
                              self.player.keys["down"] = True
                              if self.player.mode == 0 and self.player.able_to_dash:
                                   self.sounds["dash"].play()
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
                              for bookshelf in self.level.bookshelfs:
                                   if bookshelf.is_colliding:
                                        self.book_sorted += bookshelf.deposit(self.book_carrying) 
                         if event.key == K_p:
                              if self.player.mode == 2:
                                   self.player.set_mode(0)
               elif self.game_ended and self.thanks_timer > 1 and not self.scene_manager.transition:
                    if event.type == MOUSEBUTTONDOWN:
                         def change_scene():
                              self.scene_manager.set_scene("menu")
                              self.scene_manager.transition = Fade_transition(1 , False)
                         self.scene_manager.transition = Fade_transition(1 , True , change_scene)
     
     def thanks(self , time_infos):
          
          dt = time_infos["dt"]
          
          self.thanks_timer += dt
          self.screen.fill([0,0,0])
          self.events()
          self.texts["thanks"].display(self.screen)
          
          if self.thanks_timer > 2:
               if cos(self.thanks_timer * pi) > 0:
                    self.texts["click"].display(self.screen)
     
     def update(self , time_infos):
          if self.game_ended:
               self.thanks(time_infos)
          else:
               self.game(time_infos)
          
     def game(self , time_infos):
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
                         self.sounds["book_gathered"].play()
                         self.book_carrying.append(book)
               elif book.to_remove:
                    self.tilemap.books.remove(book)
          
          for book in self.tilemap.books:
               book.display_light(self.black_filter , self.camera.pos)
          for torch in self.tilemap.deco_objects:
               torch.display_light(self.black_filter , self.camera.pos)
               torch.update(dt , max_fps)
          
          for bookshelf in self.level.bookshelfs:
               
               bookshelf.update(dt , max_fps)
          
               if collide_rect(self.player.rect, bookshelf.rect):
                    bookshelf.is_colliding = True
               else:
                    bookshelf.is_colliding = False
          
          if self.book_sorted >= self.level.total_books_needed and self.scene_manager.transition == None:
               def foo():
                    self.book_sorted = 0
                    pygame.mixer.music.fadeout(1000)
                    self.next_level()
                    self.scene_manager.transition = Rand_transition(False)
               self.scene_manager.transition = Fade_transition(1 , True , foo)
          
          # -----------------------------------------------------------------
          # Powers code
          
          for power in self.level.tilemap.powers:
               if collide_rect(self.player.rect , power.rect) and not power.caught:
                    self.sounds["item_gathered"].play()
                    power.caught = True  
                    particle_burst(power.part_sys , copy(power.rect.pos) , 60 , 200 , [power.part_img] , 0.2 , n_angles=2)
                    if power.type == "dash":
                         self.player.able_to_dash = True
                    elif power.type == "orb":
                         self.player.set_mode(2)
                         present = False
                         for timer in self.power_timers:
                              if timer["type"] == "orb":
                                   timer["timer"] = 0
                                   present = True
                                   break
                         if not present:
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
          
          for bookshelf in self.level.bookshelfs:
               bookshelf.display(self.camera.render_surf , self.camera.pos)
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
          self.texts["game timer"].set_string(f"Time : {get_timestring(int(self.game_timer))}")
          
          for key , text in self.texts.items():
               if not key in ["thanks" , "click"]:
                    text.display(self.screen)
          
          for image in self.images:
               self.screen.blit(image[0] , [image[1].x , image[1].y])
          
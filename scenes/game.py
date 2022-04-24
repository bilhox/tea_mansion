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
          self.level = Level("./assets/levels/level_demo.json")
          self.tilemap = self.level.tilemap
          self.camera = Camera([0,0] , [352 , 256])
          self.font = pygame.font.Font(None , 20)
          self.game_timer = 0
          self.death_timer = 0
          self.book_caught = 0
          self.map_transition = False
          
          self.black_filter = pygame.Surface([self.camera.rect.size.x , self.camera.rect.size.y] , SRCALPHA)
          
          self.P_deathdata = Particle_data()
          self.particle_system = Particle_system()
          
          self.bs_filter = pygame.Surface([self.camera.size.x , self.camera.size.y] , SRCALPHA)
          self.game_timer = 0

          self.images = []
     
     def start(self):
          
          pygame.mouse.set_visible(False)
          self.player = Player(copy(self.tilemap.objects["player_spawn"]["coord"]))
          
          self.black_filter.fill([0,0,0,80])
          
          surf = pygame.Surface([7 , 7] , SRCALPHA)
          pygame.draw.circle(surf , [143 , 65 , 234] , [4,4] , 3)
          
          self.P_deathdata.particle_surfaces = [surf]
          self.P_deathdata.set_intervall("angle" , 0 , 360)
          self.P_deathdata.set_intervall("speed" , 1 , 4)
          self.P_deathdata.set_intervall("life_time" , .6 , .6)
          self.P_deathdata.speed_multiplicator = .94
          self.P_deathdata.set_intervall("pos" , self.player.rect.pos , self.player.rect.pos)
          
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
          
          book = pygame.image.load("./assets/objects/book.png").convert_alpha()
          pos = pygame.Vector2(150 , 2)
          self.images.append([book , pos])
          
          bc_text = Text(s2font , f": 0 / {self.level.n_book}")
          bc_text.pos = pygame.Vector2(175,6)
          
          self.clock = pygame.time.Clock()
          
          self.texts["book_counter"] = bc_text
     
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
                              if (self.player.air_time <= 4):
                                   self.player.velocity.y = -(self.player.jump_amount)
                    elif event.type == KEYUP:
                         if event.key == K_d:
                              self.player.keys["right"] = False
                         if event.key == K_q:
                              self.player.keys["left"] = False
                         if event.key == K_s:
                              if not self.player.dashing:
                                   self.player.dashing = True
                                   self.player.velocity.y = 0
               
     
     def update(self , time_infos):
          
          dt = time_infos["dt"]
          clock = time_infos["clock"]
          max_fps = time_infos["max_fps"]
          
          self.game_timer += dt
          self.black_filter.fill([0,0,0,80])
          self.camera.update(dt , max_fps)
          self.screen.fill([17 , 9 , 13])
          self.particle_system.update(dt , max_fps)
          
          #event loop
          self.events()
          
          self.tilemap.update_platforms(dt , max_fps)
          
          # Récupération de tout les colliders
          rects = []
          
          for y in range(-1 , 2):
               for x in range(-1 , 2):
                    try:
                         rects.extend(self.tilemap.collider_chunks[f"{self.player.chunk_pos[0]+x},{self.player.chunk_pos[1]+y}"])
                    except:
                         pass
          
          rects.extend(self.tilemap.get_platform_colliders())

          #Code pour faire la transition entre les salles
          if self.map_transition:
               camera_center = pygame.Vector2(self.player.map_pos[0]*8*44 , self.player.map_pos[1]*8*32)
               self.camera.pos = pygame.Vector2.lerp(self.camera.pos , camera_center , min(15*dt , 1))
          else:
               self.player.update(dt , max_fps)
               self.player.update_lights(self.game_timer)
               self.player.move(rects)
               self.player.update_after_moved()
          
          #Voir si la caméra affiche bien la bonne salle , puis transition si le contraire    
          if not self.player.dead and (not int(abs((self.player.map_pos[0]*8*44) - (self.camera.pos.x))) == 0 or not int(abs((self.player.map_pos[1]*8*32) - (self.camera.pos.y))) == 0):
               self.map_transition = True
               self.player.reset_keys()
          else:
               if self.map_transition:
                    self.camera.pos = pygame.Vector2(self.player.map_pos[0]*8*44 , self.player.map_pos[1]*8*32)
               self.map_transition = False
               
          # Player death movement
          if self.player.dead:
               if self.death_timer == 0:
                    self.particle_system.spawnparticles(40 ,  self.P_deathdata , circular=True)
               self.death_timer += dt
               self.player.kinematic = True
               if (.6 - self.death_timer) <= 0:
                    self.death_timer = 0
                    self.player.rect.pos = copy(self.tilemap.objects["player_spawn"]["coord"])
                    self.player.kinematic = False
                    self.player.dead = False
                    self.player.reset_keys()
                    self.P_deathdata.set_intervall("pos" , self.player.rect.pos , self.player.rect.pos)
          else:
               self.room_pos = f"{self.player.map_pos[0]},{self.player.map_pos[1]}"
          
          self.tilemap.update_books(dt , max_fps)
          
          for book in self.tilemap.books:
               if not book.caught:
                    if collide_rect(book.rect , self.player.rect):
                         book.is_caught()
                         self.player.books += 1
               elif book.to_remove:
                    self.tilemap.books.remove(book)
          
          for book in self.tilemap.books:
               book.display_light(self.black_filter , self.camera.pos)
          for torch in self.tilemap.deco_objects:
               torch.display_light(self.black_filter , self.camera.pos)
               torch.update(dt , max_fps)
          
          self.level.bookshelf.update(self.player , dt , max_fps)    
                
          if not self.player.dead:
               self.player.display_light(self.black_filter , self.camera.pos)
          
          #Affichage de tout les éléments (tilemap layers , player , particles , camera_surf , texts ..)
          self.tilemap.display_layer(self.camera.render_surf ,"background",chunk=self.room_pos,offset=self.camera.pos)
          self.tilemap.display_layer(self.camera.render_surf ,"background objects",chunk=self.room_pos,offset=self.camera.pos)
          for torch in self.tilemap.deco_objects:
               torch.display(self.camera.render_surf , self.camera.pos)
          
          self.tilemap.display_layer(self.camera.render_surf ,"foreground",chunk=self.room_pos,offset=self.camera.pos)
          
          self.level.bookshelf.display(self.camera.render_surf , self.camera.pos)
          if not self.player.dead:
               self.player.display(self.camera.render_surf , self.camera.pos)
          self.tilemap.display_layer(self.camera.render_surf ,"platforms",chunk=self.room_pos,offset=self.camera.pos)
          self.tilemap.display_platforms(self.camera.render_surf , self.camera.pos)
          self.particle_system.display(self.camera.render_surf , self.camera.pos)
          self.tilemap.display_books(self.camera.render_surf , self.camera.pos)
          self.camera.render_surf.blit(self.black_filter , [0,0])
          self.camera.render_surf.blit(self.bs_filter , [0,0])
          self.camera.display(self.screen , Rect([23,19],[704 , 512]))
          
          self.texts["fps"].set_string(f"FPS : {int(clock.get_fps())}")
          self.texts["book_counter"].set_string(f": {self.book_caught} / {self.level.n_book}")
          
          for text in self.texts.values():
               text.display(self.screen)
          
          for image in self.images:
               self.screen.blit(image[0] , [image[1].x , image[1].y])
          
          
if __name__ == "__main__":
     screen = pygame.display.set_mode([704 , 512])
     pygame.init()
     scene = Game(screen)
     scene.start()
     clock = pygame.time.Clock()
     while True:
          scene.update(clock)
          
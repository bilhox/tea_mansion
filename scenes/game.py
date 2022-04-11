import pygame
import sys

from scenes.scene import *
from pygame.locals import *
from scripts.camera import *
from scripts.entity import *
from scripts.map import *

class Game(Scene):
     
     def __init__(self , screen , scene_manager):
          
          super().__init__(screen , scene_manager)
          self.tilemap = TileMap(chunk_size=[44 , 32])
          self.camera = Camera([0,0] , [352 , 256])
          self.font = pygame.font.Font(None , 20)
          self.game_timer = 0
          self.death_timer = 0
          self.map_transition = False
          
          self.black_filter = pygame.Surface([self.camera.rect.size.x , self.camera.rect.size.y] , SRCALPHA)
          
          self.P_deathdata = Particle_data()
          self.particle_system = Particle_system()
          
          self.bs_filter = pygame.Surface([self.camera.size.x , self.camera.size.y] , SRCALPHA)
     
     
     def start(self):
          
          pygame.mouse.set_visible(False)
          self.tilemap.load_map("./assets/tilemaps/level_demo.tmx")
          self.player = Player(copy(self.tilemap.object_datas["player_spawn"]["coord"]))
          
          self.black_filter.fill([0,0,0,70])
          
          surf = pygame.Surface([7 , 7] , SRCALPHA)
          pygame.draw.circle(surf , [143 , 65 , 234] , [4,4] , 3)
          
          self.P_deathdata.particle_surfaces = [surf]
          self.P_deathdata.set_intervall("angle" , 0 , 360)
          self.P_deathdata.set_intervall("speed" , 1 , 4)
          self.P_deathdata.set_intervall("life_time" , .6 , .6)
          self.P_deathdata.speed_multiplicator = .94
          self.P_deathdata.set_intervall("pos" , self.player.rect.pos , self.player.rect.pos)
          
          border = pygame.image.load("./assets/border_shadow.png").convert_alpha()
          
          self.bs_filter.blit(pygame.transform.scale(border , [self.camera.size.x , 12]) , [0 , self.camera.size.y - 10])
          self.bs_filter.blit(pygame.transform.rotate(pygame.transform.scale(border , [self.camera.size.y , 12]) , -90) , [-2 , 0])
          self.bs_filter.blit(pygame.transform.rotate(pygame.transform.scale(border , [self.camera.size.y , 12]) , 90) , [self.camera.size.x - 10 , 0])
          self.bs_filter.blit(pygame.transform.rotate(pygame.transform.scale(border , [self.camera.size.x , 12]) , 180) , [0 , -2])
     
     def update(self , clock):
          dt = min(clock.tick(MAX_FPS) * 0.001 , 10)
          self.game_timer += dt
          # if game_ended:
          #      if game_timer - gameover_timepoint <= 2:
          #           slowness -= abs(0.6 - slowness) * 0.8
          #           # dt *= slowness
          #      elif game_timer - gameover_timepoint <= 3.5:
          #           slowness += abs(1 - slowness) * 0.8
          #           # dt *= slowness
          #      else:
          #           game_ended = False
          
          self.black_filter.fill([0,0,0,80])
          self.camera.update(dt , MAX_FPS)
          self.screen.fill([0,0,0])
          self.particle_system.update(dt , max_fps=MAX_FPS)
          
          #event loop
          for event in pygame.event.get():
               if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
               if not self.map_transition and not self.player.dead:
                    self.player.event_handler(event)
          
          self.tilemap.update_platforms(dt , MAX_FPS)
          
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
               self.player.update(dt , max_fps=MAX_FPS)
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
                    self.player.rect.pos = copy(self.tilemap.object_datas["player_spawn"]["coord"])
                    self.player.kinematic = False
                    self.player.dead = False
                    self.player.reset_keys()
                    self.P_deathdata.set_intervall("pos" , self.player.rect.pos , self.player.rect.pos)
          else:
               self.room_pos = f"{self.player.map_pos[0]},{self.player.map_pos[1]}"
          
          self.tilemap.update_books(dt , MAX_FPS)
          
          for book in self.tilemap.books:
               if collide_rect(book.rect , self.player.rect):
                    self.camera.shakevalues = pygame.Vector2(0 , 15)
          
          for book in self.tilemap.books:
               book.display_light(self.black_filter , self.camera.pos)
          if not self.player.dead:
               self.player.display_light(self.black_filter , self.camera.pos)
          
          #Affichage de tout les éléments (tilemap layers , player , particles , camera_surf , texts ..)
          self.tilemap.display_layer(self.camera.render_surf ,"background",chunk="0,0")
          self.tilemap.display_layer(self.camera.render_surf ,"foreground",chunk=self.room_pos,offset=self.camera.pos)
          
          if not self.player.dead:
               self.player.display(self.camera.render_surf , self.camera.pos)
          self.tilemap.display_layer(self.camera.render_surf ,"platforms",chunk=self.room_pos,offset=self.camera.pos)
          self.tilemap.display_platforms(self.camera.render_surf , self.camera.pos)
          self.particle_system.display(self.camera.render_surf , self.camera.pos)
          self.tilemap.display_books(self.camera.render_surf , self.camera.pos)
          self.camera.render_surf.blit(self.black_filter , [0,0])
          self.camera.render_surf.blit(self.bs_filter , [0,0])
          self.camera.display(self.screen , Rect([23,19],[704 , 512]))
          self.screen.blit(self.font.render(str(int(clock.get_fps())) , True , [255 , 255 , 255]) , [0,0])
          self.screen.blit(self.font.render(str(len(self.particle_system.particles)) , True , [255 , 255 , 255]) , [0,12])
          pygame.display.flip()
          
          
if __name__ == "__main__":
     screen = pygame.display.set_mode([704 , 512])
     pygame.init()
     scene = Game(screen)
     scene.start()
     clock = pygame.time.Clock()
     while True:
          scene.update(clock)
          
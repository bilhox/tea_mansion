import pygame
import sys   
import asyncio

from pygame.locals import *
from scripts.camera import Camera
from scripts.entity import *
from scripts.map import *   
from copy import * 
from scripts.particles import *

def resolve_campos(camera : Camera , map_size):
     if camera.pos.x < 0:
          camera.pos.x = 0
     elif camera.pos.x + camera.size.x > map_size[0]*8:
          camera.pos.x = map_size[0]*8 - camera.size.x

     if camera.pos.y < 0:
          camera.pos.y = 0
     elif camera.pos.y + camera.size.y > map_size[1]*8:
          camera.pos.y = map_size[1]*8 - camera.size.y

def prepare_light_filter(rendering_size : list, light_sources : list[dict]):
     filter = pygame.Surface(rendering_size , SRCALPHA)
     filter.fill([0,0,0,128])
     for light_source in light_sources:
          source = pygame.Surface([light_source["radius"]*2 , light_source["radius"]*2])
          pygame.draw.circle(source , light_source["color"] , [light_source["radius"]]*2 , light_source["radius"] )
          filter.blit(source , [light_source["pos"][0] - light_source["radius"],light_source["pos"][1] - light_source["radius"]] , special_flags=BLEND_RGB_SUB)
     
     return filter

async def main():
     pygame.init()
     pygame.mouse.set_visible(False)
     screen = pygame.display.set_mode([704 , 512])

     tilemap = TileMap(chunk_size=[44 , 32])
     tilemap.load_map("./assets/tilemaps/level_demo.tmx")

     player = Player(copy(tilemap.object_datas["player_spawn"]["coord"]))
     
     clock = pygame.time.Clock()
     MAX_FPS = 120
     font = pygame.font.Font(None , 20)
     camera = Camera([0,0] , [352 , 256])
     game_timer = 0
     death_timer = 0
     map_transition = False
     # black_filter = prepare_light_filter(camera.render_surf.get_size() , [{"pos":[100 , 100],"radius":64,"color":[255 , 255 , 255 , 0]}])
     
     surf = pygame.Surface([7 , 7] , SRCALPHA)
     pygame.draw.circle(surf , [143 , 65 , 234] , [4,4] , 3)
     P_deathdata = Particle_data()
     P_deathdata.startpos = player.rect.pos
     P_deathdata.particle_surface = surf
     P_deathdata.adding_particle_intervall = 50
     P_deathdata.particle_spawncoef = 500
     P_deathdata.set_intervall("angle" , 0 , 360)
     P_deathdata.set_intervall("speed" , 1 , 4)
     P_deathdata.set_intervall("life_time" , .6 , .6)
     P_deathdata.speed_multiplicator = .94
     particle_system = Particle_system()
     last_chunk_pos = "0,0"
     
     while True:
          
          game_timer += 1
          dt = min(clock.tick(MAX_FPS) * 0.001 , 10)
          # camera.erase_surf([67 , 28 , 48])
          camera.update()
          particle_system.update(dt , max_fps=MAX_FPS)
          
          #event loop
          for event in pygame.event.get():
               if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
               elif event.type == KEYDOWN:
                    if event.key == K_c:
                         print(camera.pos)
               if not map_transition and not player.dead:
                    player.event_handler(event)
          
          tilemap.update_platforms(dt , MAX_FPS)
          
          # Récupération de tout les colliders
          rects = []
          
          for y in range(-1 , 2):
               for x in range(-1 , 2):
                    try:
                         rects.extend(tilemap.collider_chunks[f"{player.chunk_pos[0]+x},{player.chunk_pos[1]+y}"])
                    except:
                         pass
          
          rects.extend(tilemap.get_platform_colliders())

          #Code pour faire la transition entre les salles
          if map_transition:
               camera_center = pygame.Vector2(player.map_pos[0]*8*44 , player.map_pos[1]*8*32)
               camera.pos = pygame.Vector2.lerp(camera.pos , camera_center , min(15*dt , 1))
          else:
               player.update(dt , max_fps=MAX_FPS)
               await player.move(rects)
               player.update_after_moved()
          
          #Voir si la caméra affiche bien la bonne salle , puis transition si le contraire    
          if not player.dead and (not int(abs((player.map_pos[0]*8*44) - (camera.pos.x))) == 0 or not int(abs((player.map_pos[1]*8*32) - (camera.pos.y))) == 0):
               map_transition = True
               player.reset_keys()
          else:
               if map_transition:
                    camera.pos = pygame.Vector2(player.map_pos[0]*8*44 , player.map_pos[1]*8*32)
               map_transition = False
               
          # Player death movement
          if player.dead:
               if death_timer == 0:
                    particle_system.spawnparticles(50, P_deathdata , circular=True)
               death_timer += dt
               player.kinematic = True
               if (.6 - death_timer) <= 0:
                    death_timer = 0
                    player.rect.pos = copy(tilemap.object_datas["player_spawn"]["coord"])
                    player.kinematic = False
                    player.dead = False
                    player.reset_keys()
                    P_deathdata.startpos = player.rect.pos
          else:
               last_chunk_pos = f"{player.map_pos[0]},{player.map_pos[1]}"
          
          
          #Affichage de tout les éléments (tilemap layers , player , particles , camera_surf , texts ..)
          tilemap.display_layer(camera.render_surf ,"background",chunk="0,0")
          # q
          if not player.dead:
               player.display(camera.render_surf , camera.pos)
          tilemap.display_layer(camera.render_surf ,"foreground",chunk=last_chunk_pos,offset=camera.pos)
          tilemap.display_platforms(camera.render_surf , camera.pos)
          particle_system.display(camera.render_surf , camera.pos)
          camera.display(screen)
          screen.blit(font.render(str(int(clock.get_fps())) , True , [255 , 255 , 255]) , [0,0])
          screen.blit(font.render(str(len(particle_system.particles)) , True , [255 , 255 , 255]) , [0,12])
          pygame.display.flip()

if __name__ == "__main__":
     asyncio.run(main())

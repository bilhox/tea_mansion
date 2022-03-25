import pygame
import sys   
import asyncio

from pygame.locals import *
from scripts.camera import Camera
from scripts.entity import *
from scripts.map import *   
from copy import * 

def resolve_campos(camera : Camera , map_size):
     if camera.pos.x < 0:
          camera.pos.x = 0
     elif camera.pos.x + camera.size.x > map_size[0]*8:
          camera.pos.x = map_size[0]*8 - camera.size.x

     if camera.pos.y < 0:
          camera.pos.y = 0
     elif camera.pos.y + camera.size.y > map_size[1]*8:
          camera.pos.y = map_size[1]*8 - camera.size.y

def display_platform(surface , collider : Collider , camera_pos : pygame.Vector2):
     a = pygame.Surface([collider.rect.size.x , collider.rect.size.y])
     a.fill([13 , 210 , 120])
     surface.blit(a , [collider.rect.x - camera_pos.x , collider.rect.y - camera_pos.y])

async def main():
     pygame.init()
     screen = pygame.display.set_mode([704 , 512] , SCALED+RESIZABLE)

     tilemap = TileMap("./assets/tilemaps/level_demo.tmx")

     player = Player(copy(tilemap.object_datas["player_spawn"]["coord"]))
     
     clock = pygame.time.Clock()
     MAX_FPS = 120
     font = pygame.font.Font(None , 20)
     camera = Camera([0,0] , [352 , 256])
     game_timer = 0
     map_transition = False
     
     while True:
          
          game_timer += 1
          dt = min(clock.tick(MAX_FPS) * 0.001 , 10)
          # camera.erase_surf([67 , 28 , 48])
          camera.update()
          
          for event in pygame.event.get():
               if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
               elif event.type == MOUSEWHEEL:
                    if event.y < 0:
                         camera.size += pygame.Vector2(20 , 15)
                    elif event.y > 0:
                         camera.size -= pygame.Vector2(20 , 15)
               elif event.type == KEYDOWN:
                    if event.key == K_c:
                         print(camera.pos)
               if not map_transition:
                    player.event_handler(event)
          
          tilemap.update_platforms(dt , MAX_FPS)
          
          rects = []
          
          # print(map_pos)
          for y in range(-1 , 2):
               for x in range(-1 , 2):
                    try:
                         rects.extend(tilemap.collider_chunks[f"{player.chunk_pos[0]+x},{player.chunk_pos[1]+y}"])
                    except:
                         pass
          
          rects.extend(tilemap.get_platform_colliders())
          # if (camera.pos.x - map_pos[0]*8*44 < 1 and camera.pos.y - map_pos[1]*8*32 < 1):
          if map_transition:
               camera_center = pygame.Vector2(player.map_pos[0]*8*44 , player.map_pos[1]*8*32)
               camera.pos = pygame.Vector2.lerp(camera.pos , camera_center , min(15*dt , 1))
          else:
               player.update(dt , max_fps=MAX_FPS)
               await player.move(rects)
               player.update_after_moved()
               
          if not int(abs((player.map_pos[0]*8*44) - (camera.pos.x))) == 0 or not int(abs((player.map_pos[1]*8*32) - (camera.pos.y))) == 0:
               map_transition = True
               player.reset_keys()
          else:
               if map_transition:
                    camera.pos = pygame.Vector2(player.map_pos[0]*8*44 , player.map_pos[1]*8*32)
               map_transition = False
          
          if player.dead:
               player = Player(copy(tilemap.object_datas["player_spawn"]["coord"]))
          
          display_layer(camera.render_surf ,tilemap.layers["background"],chunk="0,0")
          player.display(camera.render_surf , camera.pos)
          display_layer(camera.render_surf ,tilemap.layers["foreground"],chunk=f"{player.map_pos[0]},{player.map_pos[1]}",offset=camera.pos)
          tilemap.display_platforms(camera.render_surf , camera.pos)
          camera.display(screen)
          screen.blit(font.render(str(int(clock.get_fps())) , True , [255 , 255 , 255]) , [0,0])
          
          pygame.display.flip()

if __name__ == "__main__":
     asyncio.run(main())

import pygame
import sys
import asyncio

from pygame.locals import *
from scripts.form import *
from scripts.camera import *

async def main():
     screen = pygame.display.set_mode([500 , 500])

     fR = FloatRect(pygame.Vector2(0 , 0) , pygame.Vector2(50 , 50))
     fR2 = FloatRect(pygame.Vector2(240, 210) , pygame.Vector2(100 , 100))

     fR.origin = pygame.Vector2(fR.size.x / 2 , fR.size.y / 2)
     fR2.origin = pygame.Vector2(fR2.size.x / 2 , fR2.size.y / 2)

     camera = Camera([0,0] , [500 , 500])

     cam_keys = {"left":False , "right":False , "up":False , "down":False}
     rect_keys = {"left":False , "right":False , "up":False , "down":False , "rotate":False}
     fR.color = [100 , 0 , 0]
     fR2.color = [200 , 34 , 120]	

     while True:
          
          screen.fill([255,0,0])
          
          for event in pygame.event.get():
               if (event.type == QUIT):
                    pygame.quit()
                    sys.exit(0)
               elif event.type == KEYDOWN:
                    if event.key == K_RIGHT:
                         cam_keys["right"] = True
                    if event.key == K_LEFT:
                         cam_keys["left"] = True
                    if event.key == K_UP:
                         cam_keys["up"] = True
                    if event.key == K_DOWN:
                         cam_keys["down"] = True
                    if event.key == K_r:
                         cam_keys["rotate"] = True
                    if event.key == K_d:
                         rect_keys["right"] = True
                    if event.key == K_q:
                         rect_keys["left"] = True
                    if event.key == K_z:
                         rect_keys["up"] = True
                    if event.key == K_s:
                         rect_keys["down"] = True
                    if event.key == K_r:
                         rect_keys["rotate"] = True
               elif event.type == KEYUP:
                    if event.key == K_RIGHT:
                         cam_keys["right"] = False
                    if event.key == K_LEFT:
                         cam_keys["left"] = False
                    if event.key == K_UP:
                         cam_keys["up"] = False
                    if event.key == K_DOWN:
                         cam_keys["down"] = False
                    if event.key == K_r:
                         rect_keys["rotate"] = False
                    if event.key == K_d:
                         rect_keys["right"] = False
                    if event.key == K_q:
                         rect_keys["left"] = False
                    if event.key == K_z:
                         rect_keys["up"] = False
                    if event.key == K_s:
                         rect_keys["down"] = False
          
          if cam_keys["right"]:
               camera.pos.x += 1
          if cam_keys["left"]:
               camera.pos.x -= 1
          if cam_keys["up"]:
               camera.pos.y -= 1
          if cam_keys["down"]:
               camera.pos.y += 1
               
          if rect_keys["right"]:
               fR.pos.x += .8
          if rect_keys["left"]:
               fR.pos.x -= .8
          if rect_keys["up"]:
               fR.pos.y -= .8
          if rect_keys["down"]:
               fR.pos.y += .8
          if rect_keys["rotate"]:
               fR.rotation += 0.25
               
          await diag_collision(fR , fR2)
          camera.display(screen , fR , fR2)
          pygame.display.flip()

if __name__ == "__main__":
     asyncio.run(main())
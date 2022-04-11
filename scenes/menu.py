import pygame
import sys

from scenes.scene import *
from pygame.locals import *
from scripts.text import *

class Menu(Scene):
     
     def __init__(self, screen , scene_manager):
         super().__init__(screen , scene_manager)
         self.fnt = Font("./assets/fonts/large_font.png" , [255,255,255])
         
     def update(self , clock):
          
          self.screen.fill([0,0,0])
          for event in pygame.event.get():
               
               if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
          
          self.fnt.render("Jaim\ne les chats" , self.screen , [100 , 100] , zoom=4)
          pygame.display.flip()
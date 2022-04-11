import pygame
import sys

from scenes.scene import *
from pygame.locals import *
from scripts.text import *
from scripts.button import *

class Menu(Scene):
     
     def __init__(self, screen , scene_manager):
          super().__init__(screen , scene_manager)
          self.fnt = Font("./assets/fonts/large_font.png" , [255,255,255])
         
          def start_game():
               self.scene_manager.set_scene("game")
               print("re")
     
          start_button_data = {
          "target":start_game,
          "text-data":{
               "content":"",
               "font":pygame.font.Font(None , 30),
               "centered":True
          },
          "textures":{
               "nothing":pygame.image.load("./assets/button_textures/start.png").convert_alpha(),
               "hover":pygame.image.load("./assets/button_textures/start.png").convert_alpha(),
               "clicked":pygame.image.load("./assets/button_textures/start.png").convert_alpha(),
          }
          }
         
          self.start_button = Button([self.screen.get_width() / 2 - 32 ,300],[64 , 64], start_button_data)
         
     def start(self):
          pygame.mouse.set_visible(True)
         
     def update(self , clock):
          
          self.screen.fill([0,0,0])
          for event in pygame.event.get():
               
               if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
                    
               self.start_button.update(event)
          
          text = self.fnt.render("Unamed project",zoom=2)
          self.screen.blit(text ,  [self.screen.get_width()/2-text.get_width()/2, 100])
          self.start_button.display(self.screen)
          pygame.display.flip()
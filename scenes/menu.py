import pygame
import sys

from scenes.scene import *
from pygame.locals import *
from scripts.text import *
from scripts.button import *

class Menu(Scene):
     
     def __init__(self, screen , scene_manager):
          super().__init__(screen , scene_manager)
         
     def start(self):
          pygame.mouse.set_visible(True)
          
          fnt = Font("./assets/fonts/large_font.png" , [255,255,255])
          fnt.zoom = 4
          self.text = Text(fnt , "Unamed project")
          self.text.origin = self.text.size / 2
          self.text.pos = pygame.Vector2(self.screen.get_width()/2 , 100)
          
          def start_game():
               def change_scene():
                    self.scene_manager.set_scene("game")
               self.scene_manager.transition = Transition(1 , 1 , change_scene)
          
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
         
     def update(self , time_infos):
          
          self.screen.fill([0,0,0])
          for event in pygame.event.get():
               
               if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
                    
               self.start_button.update(event)
          
          self.text.display(self.screen)
          self.start_button.display(self.screen)
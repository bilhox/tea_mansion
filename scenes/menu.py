import pygame
import sys

from scenes.scene import *
from pygame.locals import *
from scripts.text import *
from scripts.button import *
from math import cos , sin

class Menu(Scene):
     
     def __init__(self, screen , scene_manager):
          super().__init__(screen , scene_manager)
          
          self.game_title = []
          self.background = pygame.image.load("./assets/start_menu.png").convert_alpha()
         
     def start(self):
          pygame.mouse.set_visible(True)
          
          fnt = Font("./assets/fonts/large_font.png" , [255,255,255])
          fnt.zoom = 4
          
          t_text = Text(fnt , "Tea Mansion")
          
          txt = "Tea Mansion"
          offset = 0
          for letter in txt:
               text = Text(fnt , letter)
               text.pos = pygame.Vector2(self.screen.get_width() / 2 - t_text.size.x / 2 + offset , 100)
               offset += text.size.x
               self.game_title.append({"text":text , "anim_offset":pygame.Vector2(0,0)})
          
          def start_game():
               def change_scene():
                    self.scene_manager.set_scene("game")
                    self.scene_manager.transition = Fade_transition(1 , False)
               self.scene_manager.transition = Fade_transition(1 , True , change_scene)
          
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

          self.timer = 0
          
     def update(self , time_infos):
          
          dt = time_infos["dt"]
          
          self.timer += dt * 4
          self.screen.blit(self.background , [0,0])
          
          for index , letter in enumerate(self.game_title):
               if index % 2 == 0:
                    letter["anim_offset"].y = cos(self.timer) * 4
               else:
                    letter["anim_offset"].y = sin(self.timer) * 4
          
          for event in pygame.event.get():
               
               if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)

               if not self.scene_manager.transition:    
                    self.start_button.update(event)
          
          for letter in self.game_title:
               letter["text"].display(self.screen , offset=letter["anim_offset"])
          self.start_button.display(self.screen)
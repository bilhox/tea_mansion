import pygame
import sys

from scenes.scene import *
from scripts.text import *
from scripts.button import *
from math import cos , sin

class Menu(Scene):
     
     def __init__(self, screen , scene_manager):
          super().__init__(screen , scene_manager)
          
          self.sounds = {}
          self.game_title = []
          self.background = pygame.transform.scale_by(pygame.image.load("./assets/start_menu.png").convert_alpha(), 3/2)
          
          fnt = Font("./assets/fonts/large_font.png" , [255,255,255])
          fnt.zoom = 4
          
          t_text = Text(fnt , "Tea Mansion")
          
          txt = "Tea Mansion"
          offset = 0
          # Variable used for animation offset , for all letters don't begin at the same frequency
          ao_radians = 0
          for letter in txt:
               text = Text(fnt , letter)
               text.pos = pygame.Vector2(self.screen.get_width() / 2 - t_text.size.x / 2 + offset , 100)
               offset += text.size.x
               self.game_title.append({"text":text , "timer":ao_radians , "anim_offset":pygame.Vector2(0,0)})
               ao_radians += pi/4
               
          self.sounds["button"] = pygame.mixer.Sound("./assets/sfx/menu_select.wav")
          self.sounds["button"].set_volume(0.2)
          
          def start_game():
               self.sounds["button"].play()
               def change_scene():
                    self.scene_manager.set_scene("game")
                    self.scene_manager.transition = Fade_transition(1 , False)
               self.scene_manager.transition = Fade_transition(1 , True , change_scene)
               pygame.mixer.music.fadeout(1000)
          
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
         
          self.start_button = Button([self.screen.get_width() / 2 - 32 ,self.screen.get_height() * 2/3],[64 , 64], start_button_data)
         
     def start(self):
          pygame.mouse.set_visible(True)
          pygame.mixer.music.load("./assets/sfx/menu.ogg")
          pygame.mixer.music.play(loops=2000)
          self.timer = 0
          
     def update(self , time_infos):
          
          dt = time_infos["dt"]
          
          self.timer += dt
          self.screen.blit(self.background , [0,0])
          
          for index , letter in enumerate(self.game_title):
               letter["timer"] += dt * 3
               if index % 2 == 0:
                    letter["anim_offset"].y = cos(letter["timer"]) * 4
               else:
                    letter["anim_offset"].y = sin(letter["timer"]) * 4
          
          for event in pygame.event.get():
               
               if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

               if not self.scene_manager.transition:    
                    self.start_button.update(event)
          
          for letter in self.game_title:
               letter["text"].display(self.screen , offset=letter["anim_offset"])
          self.start_button.display(self.screen)
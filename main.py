import pygame
import sys   

from pygame.locals import *
from scripts.entity import *
from scripts.map import *   
from copy import * 
from scripts.particles import *
from scripts.text import *
from scenes import game , menu , scene

class App():
     
     def __init__(self):
          pygame.init()
          self.screen = pygame.display.set_mode([750 , 550])
          pygame.display.set_caption("Tea Mansion - v0.9.1")
          self.scene_manager = scene.Scene_Manager()
          self.scene_manager.scenes = {
               "game":game.Game(self.screen , self.scene_manager),
               "menu":menu.Menu(self.screen , self.scene_manager)
          }
          
          self.scene_manager.set_scene("menu")
          self.clock = pygame.time.Clock()
          
     def main_loop(self):
          while True:
               time_infos = {"clock":self.clock , "dt":self.clock.tick(125) * 0.001 , "max_fps":125}
               self.scene_manager.update(time_infos)

if __name__ == "__main__":
     app = App()
     app.main_loop()
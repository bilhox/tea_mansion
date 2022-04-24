import pygame
import os

from xml.etree.ElementTree import *
from pygame.locals import *


class Animation_Data():
     
     def __init__(self , path : str):
          self.id = path.split("/")[-1]
          config_parser = parse(path+"/config.xml")
          self.duration = 0
          self.images = []
          self.infinite = bool(config_parser.getroot().get("infinite"))
          self.speed = float(config_parser.getroot().get("speed"))
          
          
          img_frames = [int(frame) for frame in config_parser.getroot().get("frames").split(",")]
          img_list = []
          
          img = pygame.image.load(path+"/"+config_parser.getroot().get("source"))
          slice_size = int(config_parser.getroot().get("slice_size"))
          
          x = 0
          for i in range(0 , img.get_width() , slice_size):
               image = img.subsurface(Rect(x*slice_size , 0 , slice_size , img.get_height()))
               img_list.append(image)
               x+=1
          
          total = 0
          for index , image in enumerate(img_list):
               total += img_frames[index]
               self.images.append([total , img_list[index]])
          
          self.duration = total

class Animation:
     
     def __init__(self , anim_data : Animation_Data):
          
          self.data = anim_data
          self.frame = 0
          self.pause = False
          self.finished = False
          self.calc_image()
     
     def play(self , dt , max_fps=60):
          if not self.finished:
               if not self.pause:
                    self.frame += dt * max_fps * self.data.speed
               if self.frame > self.data.duration:
                    self.frame = 0 
                    self.finished = True if self.data.infinite else False
               self.calc_image()
     
     def calc_image(self):
          
          for frame in self.data.images:
               if frame[0] > self.frame:
                    self.img = frame[1]
                    break
          
          if self.data.images[-1][0] < self.frame:
               self.img = self.data.images[-1][1]
     
     def render(self , surface , pos , flip=False): 
          surface.blit(pygame.transform.flip(self.img, flip, False) , pos)
          return self.img.get_size()
     
     def get_current_img(self , flip=False):
          return pygame.transform.flip(self.img, flip, False)
               

class AnimationManager():
     
     def __init__(self , path_folder):
          
          self.animations = {}
          
          for file in os.listdir(path_folder):
               self.animations[file] = Animation_Data(path_folder + f"/{file}")
     
     def get(self , id):
          return Animation(self.animations[id])
          
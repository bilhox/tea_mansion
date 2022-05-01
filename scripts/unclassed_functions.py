import pygame

from random import *
from math import *
from pygame.locals import *
from copy import copy

def mult_image(img , color):
     mult_surf = img.copy()
     mult_surf.fill(color)
     new_img = img.copy()
     new_img.blit(mult_surf , (0 , 0), special_flags=BLEND_RGBA_MULT)
     return new_img

def get_imgs_from_sheet(path , slice):
     
     img = pygame.image.load(path).convert_alpha()
     imgs = []
     
     for i in range(0 , img.get_width() , slice):
          imgs.append(img.subsurface(Rect([i , 0],[slice]*2)))
     
     return imgs

def swap_color(img,old_c,new_c):
     
     img.set_colorkey(old_c)
     surf = img.copy()
     surf.fill(new_c)
     surf.blit(img,(0,0))
     surf.set_colorkey([0,0,0])
     return surf

def get_timestring(time : int):
     vals = []
     vals.append(time // 60)
     vals.append(time % 60)
     if vals[0] == 0:
          return f"{vals[1]}s"
     else:
          return f"{vals[0]}m {vals[1]}s"

import pygame

from pygame.locals import * 

def mult_image(img , color):
     mult_surf = img.copy()
     mult_surf.fill(color)
     new_img = img.copy()
     new_img.blit(mult_surf , (0 , 0), special_flags=BLEND_RGBA_MULT)
     return new_img
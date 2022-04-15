import pygame

from pygame.locals import *

def clip(surf,x,y,x_size,y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x,y,x_size,y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

def swap_color(img,old_c,new_c):
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img,(0,0))
    return surf

def load_font_img(path, font_color):
    fg_color = (255, 0, 0)
    bg_color = (0, 0, 0)
    font_img = pygame.image.load(path).convert()
    font_img = swap_color(font_img, fg_color, font_color)
    last_x = 0
    letters = []
    letter_spacing = []
    for x in range(font_img.get_width()):
        if font_img.get_at((x, 0))[0] == 127:
            letters.append(clip(font_img, last_x, 0, x - last_x, font_img.get_height()))
            letter_spacing.append(x - last_x)
            last_x = x + 1
    for letter in letters:
        letter.set_colorkey(bg_color)
    return letters, letter_spacing, font_img.get_height()

class Font():
    def __init__(self, path, color):
        self.letters, self.letter_spacing, self.line_height = load_font_img(path, color)
        self.font_order = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','.','-',',',':','+','\'','!','?','0','1','2','3','4','5','6','7','8','9','(',')','/','_','=','\\','[',']','*','"','<','>',';']
        self.space_width = self.letter_spacing[0]
        self.base_spacing = 1
        self.line_spacing = 2
        self.zoom = 1
    
    @property
    def height(self):
        return self.line_height

    def width(self, text):
        text_width = 0
        for char in text:
            if char == ' ':
                text_width += self.space_width + self.base_spacing
            else:
                text_width += self.letter_spacing[self.font_order.index(char)] + self.base_spacing
        return text_width

    def render(self, text):
        
        width = 0
        height = self.line_height*self.zoom
        
        for char in text:
            if char not in ["\n" , ' ']:
                l = self.font_order.index(char)
                width += self.letters[l].get_width()*self.zoom + self.base_spacing * self.zoom
            elif char == " ":
                width += (self.space_width + self.base_spacing) * self.zoom
        
        final_surf = pygame.Surface([width , height] , SRCALPHA)
        x_offset = 0
        y_offset = 0
        for char in text:
            if char not in ['\n', ' ']:
                l = self.font_order.index(char)
                surface = pygame.transform.scale(self.letters[l] , [self.letters[l].get_width()*self.zoom , self.letters[l].get_height()*self.zoom])
                final_surf.blit(surface, (x_offset, y_offset))
                x_offset += surface.get_width() + self.base_spacing * self.zoom
            elif char == ' ':
                x_offset += (self.space_width + self.base_spacing) * self.zoom
            else:
                y_offset += surface.get_height()*self.zoom + self.height
                x_offset = 0
        
        return final_surf
        # print(x_offset)

class Text():
    
    def __init__(self , font : Font , string : str):
        self.string = string
        self.font = font
        self.pos = pygame.Vector2(0,0)
        self.origin = pygame.Vector2(0,0)
        self.surface = self.font.render(self.string)
    
    def set_string(self , string):
        self.string = string
        self.surface = self.font.render(self.string)
    
    def set_font(self , font):
        self.font = font
        self.surface = self.font.render(self.string)
    
    @property
    def size(self):
        return pygame.Vector2(self.surface.get_size())
    
    def display(self , surface , scale=[0,0]):
        
        if scale == [0,0]:
            surface.blit(self.surface , [self.pos.x - self.origin.x , self.pos.y - self.origin.y])
        else:
            surface.blit(pygame.transform.scale(self.surface , scale) , [self.pos.x - self.origin.x*(scale[0]/self.size.x) , self.pos.y - self.origin.y*(scale[1]/self.size.y)])

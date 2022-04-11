#!/usr/bin/python3.4
import pygame, sys

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
    def __init__(self, path, color , text_zoom=1):
        self.letters, self.letter_spacing, self.line_height = load_font_img(path, color)
        self.font_order = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','.','-',',',':','+','\'','!','?','0','1','2','3','4','5','6','7','8','9','(',')','/','_','=','\\','[',']','*','"','<','>',';']
        self.space_width = self.letter_spacing[0]
        self.base_spacing = 1
        self.line_spacing = 2
        self.text_zoom = text_zoom
    
    @property
    def height(self):
        return self.line_height * self.text_zoom

    def width(self, text):
        text_width = 0
        for char in text:
            if char == ' ':
                text_width += self.space_width * self.text_zoom + self.base_spacing
            else:
                text_width += self.letter_spacing[self.font_order.index(char)] * self.text_zoom + self.base_spacing
        return text_width

    def render(self, text, surf, loc, line_width=0 , zoom=1):
        x_offset = 0
        y_offset = 0
        if line_width != 0:
            spaces = []
            x = 0
            for i, char in enumerate(text):
                if char == ' ':
                    spaces.append((x, i))
                    x += (self.space_width + self.base_spacing) * zoom
                else:
                    x += self.letter_spacing[self.font_order.index(char)]*zoom + self.base_spacing * zoom
            line_offset = 0
            for i, space in enumerate(spaces):
                if (space[0] - line_offset) > line_width:
                    line_offset += spaces[i - 1][0] - line_offset
                    if i != 0:
                        text = text[:spaces[i - 1][1]] + '\n' + text[spaces[i - 1][1] + 1:]
        for char in text:
            if char not in ['\n', ' ']:
                l = self.font_order.index(char)
                surface = pygame.transform.scale(self.letters[l] , [self.letters[l].get_width()*zoom , self.letters[l].get_height()*zoom])
                surf.blit(surface, (loc[0] + x_offset, loc[1] + y_offset))
                x_offset += surface.get_width() + self.base_spacing * zoom
            elif char == ' ':
                x_offset += (self.space_width + self.base_spacing) * zoom
            else:
                y_offset += surface.get_width()*zoom + self.height
                x_offset = 0
        
        # print(x_offset)

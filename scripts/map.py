import os
import pygame

from xml.etree.ElementTree import *
from pygame.locals import *
from scripts.form import *
from scripts.camera import *

def load_tileset(tsx_path):
     parsed = parse(tsx_path)
     root = parsed.getroot()
     tile_size = [int(root.get("tilewidth")),int(root.get("tileheight"))]
     t1_path = root[0].get("source")
     image = pygame.image.load(os.path.join(os.path.dirname(tsx_path) , t1_path))
     image_size = [int(root[0].get("width")) , int(root[0].get("height"))]

     tiles = []
     
     i = 1
     for y in range(0 , image_size[1] // tile_size[1]):
          
          for x in range(0 , image_size[0] // tile_size[0]):
               tile = image.subsurface(Rect(x*tile_size[0],y*tile_size[1],tile_size[0],tile_size[1]))
               tiles.append(tile)
               i+=1
     
     colliders = {}
     
     for special_tile in root.findall("tile"):
          try:
               tile_id = special_tile.get("id")
               tile_type = special_tile.get("type")
               
               if (tile_type == "collider"):
                    collider_type = special_tile.find("properties").find("property").get("value")
                    colliders[int(tile_id)] = collider_type
          except:
               pass
     
     return tiles , colliders

class TileMap():
     
     def __init__(self , map_path):
          
          self.tileset = []
          self.collider_types = {}
          self.size = [0,0]
          self.collider_chunks = {}
          self.layers = {}
          
          root = parse(map_path).getroot()
          self.tileset , self.collider_types = load_tileset(os.path.join(os.path.dirname(map_path) , root.find("tileset").get("source")))
          self.size[0] = int(root.get("width"))
          self.size[1] = int(root.get("height"))
          for layer in root.findall("layer"):
               
               data = layer.find("data").text
               data = data.strip("\n").splitlines()
               t_tab = []
               
               for line in data:
                    l = line.strip(",").split(",")
                    t_tab.append(l)
               
               
               if layer.get("name") == "colliders":
                    for cy in range(0 , self.size[1] // 4):
                         for cx in range(0 , self.size[0] // 4):
                              c_chunk = []
                              pos = f"{cx},{cy}"
                              for y in range(cy*4 , (cy+1)*4):
                                   # print(y)
                                   for x in range(cx*4 , (cx+1)*4):
                                        if (t_tab[y][x] != "0"):
                                             rect = FloatRect(pygame.Vector2(x*8 , y*8) , pygame.Vector2(8,8))
                                             c_chunk.append(Collider(rect , self.collider_types[int(t_tab[y][x])-1]))
                              if c_chunk != []:
                                   self.collider_chunks[pos] = c_chunk
               else:
                    layer_data = {}
                    for cy in range(0 , self.size[1] // 32):
                         for cx in range(0 , self.size[0] // 44):
                              t_chunk = []
                              pos = f"{cx},{cy}"
                              for y in range(cy*32 , (cy+1)*32):
                                   # print(y)
                                   for x in range(cx*44 , (cx+1)*44):
                                        if (t_tab[y][x] != "0"):
                                             tile = Tile([x*8 , y*8],self.tileset[int(t_tab[y][x])-1])
                                             t_chunk.append(tile)
                              if t_chunk != []:
                                   layer_data[pos] = t_chunk  
                    self.layers[layer.get("name")] = layer_data
                        
          # with open(file=map_path , mode="r" , encoding="utf-8") as reader:
               
          #      content = reader.readlines()
          #      data = []
          #      for line in content:
          #           data.append(line.strip("\n"))
               
          #      self.size[0] = len(data[0])
          #      self.size[1] = len(data)
          #      for cy in range(0 , self.size[1] // 4):
          #           for cx in range(0 , self.size[0] // 4):
          #                c_chunk = []
          #                t_chunk = []
          #                pos = f"{cx},{cy}"
          #                for y in range(cy*4 , (cy+1)*4):
          #                     # print(y)
          #                     for x in range(cx*4 , (cx+1)*4):
          #                          if (data[y][x] == "1"):
          #                               rect = FloatRect(pygame.Vector2(x*8 , y*8) , pygame.Vector2(8,8))
          #                               c_chunk.append(rect)
          #                               surf = pygame.Surface([8 , 8])
          #                               surf.fill([230 , 67 , 34])
          #                               tile = Tile([x*8 , y*8],surf)
          #                               t_chunk.append(tile)
                                   
          #                self.texture_chunks[pos] = t_chunk
          #                self.collider_chunks[pos] = c_chunk
          
          # print(self.chunks)

def display_layer(surface , layer , chunk="" , camera_rect=None, offset=pygame.Vector2(0,0)):
          
          if chunk != "":
               try:
                    for tile in layer[chunk]:
                         surface.blit(tile.surface , [(tile.pos[0] - offset.x) , (tile.pos[1] - offset.y)])
               except:
                    pass
          
          else:
               for key , chunk in layer.items():
                    point = [int(val)*32 for val in key.split(",")]
                    point2 = [val+32 for val in point]
                    if camera_rect.collidepoint(point) or camera_rect.collidepoint(point2):
                         for tile in chunk:
                              surface.blit(tile.surface , [(tile.pos[0] - offset.x) , (tile.pos[1] - offset.y)])
                         
     

class Tile():
     
     def __init__(self , pos , surface):
          self.pos = pos
          self.surface = surface
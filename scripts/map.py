import os
import pygame

from xml.etree.ElementTree import *
from pygame.locals import *
from scripts.form import *
from scripts.camera import *
from math import *

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
          self.object_datas = {}
          self.platforms = []
          
          root = parse(map_path).getroot()
          self.tileset , self.collider_types = load_tileset(os.path.join(os.path.dirname(map_path) , root.find("tileset").get("source")))
          self.size[0] = int(root.get("width"))
          self.size[1] = int(root.get("height"))
          
          layer_datas = {}
          
          for layer in root.findall("layer"):
               data = layer.find("data").text
               data = data.strip("\n").splitlines()
               t_tab = []
               
               for line in data:
                    l = line.strip(",").split(",")
                    t_tab.append(l)
               
               layer_datas[layer.get("name")] = t_tab
          
          object_group = root.find("objectgroup")
          for obj in object_group.findall("object"):
               if obj.get("type") == "moving_platform":
                    platform_data = {"direction":True}
                    colliders = []
                    size = [int(obj.get("width")) , int(obj.get("height"))]
                    surface = pygame.Surface(size , SRCALPHA)
                    # surface.set_colorkey([255,255,255])
                    pos = pygame.Vector2(int(obj.get("x")) , int(obj.get("y")))
                    for prop in obj.find("properties").findall("property"):
                         prop_name = prop.get("name")
                         if prop_name == "from":
                              t_pos = prop.get("value").split(";")
                              t_pos = pygame.Vector2(float(t_pos[0]) , float(t_pos[1]))
                              platform_data["from"] = t_pos
                         elif prop_name == "to":
                              t2_pos = prop.get("value").split(";")
                              t2_pos = pygame.Vector2(float(t2_pos[0]) , float(t2_pos[1]))
                              platform_data["to"] = t2_pos
                         elif prop_name == "speed":
                              platform_data["speed"] = float(prop.get("value"))
                         elif prop_name == "layers_included":
                              layer_names = prop.get("value").split(";")
                              for layer_name in layer_names:
                                   t_tab = layer_datas[layer_name]
                                   for y in range(size[1]//8):
                                        for x in range(size[0]//8):
                                             if int(t_tab[int(y+(pos.y // 8))][int(x+(pos.x // 8))]) == 0: continue
                                             if (layer_name == "colliders"):
                                                  rect = FloatRect(pygame.Vector2(pos.x+x*8 , pos.y+y*8) , pygame.Vector2(8,8))
                                                  collider = Collider(rect , self.collider_types[int(t_tab[int(y+(pos.y // 8))][int(x+(pos.x // 8))])-1])
                                                  colliders.append(collider)
                                             else:
                                                  surf = self.tileset[int(t_tab[int(y+(pos.y // 8))][int(x+(pos.x // 8))])-1]
                                                  surface.blit(surf , [x*8 , y*8])
                                             t_tab[int(y+(pos.y // 8))][int(x+(pos.x // 8))] = "0"
                    
                    self.platforms.append(Platform(pos,surface , colliders , platform_data))
                              
               else:
                    data = {}
                    name = obj.get("name")
                    data['type'] = obj.get("type")
                    data["coord"] = pygame.Vector2(float(obj.get("x")) , float(obj.get("y")))
                    self.object_datas[name] = data
          
          for key in layer_datas:
               t_tab = layer_datas[key]
               if key == "colliders":
                    for cy in range(0 , self.size[1] // 4):
                         for cx in range(0 , self.size[0] // 4):
                              c_chunk = []
                              pos = f"{cx},{cy}"
                              for y in range(cy*4 , (cy+1)*4):
                                   # print(y)
                                   for x in range(cx*4 , (cx+1)*4):
                                        if (t_tab[y][x] != "0"):
                                             size = pygame.Vector2(8,8)
                                             if self.collider_types[int(t_tab[y][x])-1] == "trap":
                                                  size = pygame.Vector2(8 , 1)
                                             rect = FloatRect(pygame.Vector2(x*8 , y*8) , size)
                                             collider = Collider(rect , self.collider_types[int(t_tab[y][x])-1])
                                             c_chunk.append(collider)
                              if c_chunk != []:
                                   self.collider_chunks[pos] = c_chunk
               else:
                    layer_data = {}
                    for cy in range(0 , self.size[1] // 32):
                         for cx in range(0 , self.size[0] // 44):
                              chunk_surf = pygame.Surface([8*44 , 8*32] , SRCALPHA)
                              pos = f"{cx},{cy}"
                              py = 0
                              for y in range(cy*32 , (cy+1)*32):
                                   px = 0
                                   for x in range(cx*44 , (cx+1)*44):
                                        if (t_tab[y][x] != "0"):
                                             chunk_surf.blit(self.tileset[int(t_tab[y][x])-1] , [px*8 , py*8])
                                        px += 1
                                   py += 1
                              layer_data[pos] = chunk_surf  
                    self.layers[key] = layer_data
                        
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
          
     def get_platform_colliders(self):
          collider = []
          for platform in self.platforms:
               collider.extend(platform.colliders)
          
          return collider
     
     def update_platforms(self , dt , max_fps=60):
          for platform in self.platforms:
               platform.update(dt , max_fps)
     
     def display_platforms(self , surface , camera_pos=pygame.Vector2(0,0)):
          for platform in self.platforms:
               platform.display(surface , camera_pos)

def display_layer(surface , layer , chunk , offset=pygame.Vector2(0,0)):
     
     try: 
          pos = [int(val) for val in chunk.split(",")]
          pos[0] *= 44*8
          pos[1] *= 32*8
          surface.blit(layer[chunk] , [(pos[0] - offset.x) , (pos[1] - offset.y)])
     except:
          print("nope")
          
                         
     

class Tile():
     
     def __init__(self , pos , surface):
          self.pos = pos
          self.surface = surface

class Platform():
     
     def __init__(self , pos : pygame.Vector2, surface : pygame.Surface , colliders : list[Collider] , platform_data : dict):
          self.pos = pos
          self.surface = surface
          self.colliders = colliders
          self.platform_data = platform_data
          
          self.distance = sqrt((self.platform_data["to"].x - self.platform_data["from"].x)**2 + (self.platform_data["to"].y - self.platform_data["from"].y)**2)
          try:
               self.move_vector = (self.platform_data["to"] - self.platform_data["from"]).normalize()
          except:
               self.move_vector = pygame.Vector2(0,0)
               
     def update(self , dt , max_fps=60):
          # print(self.pos)
          if (self.platform_data["direction"]):
               
               self.pos += self.move_vector * self.platform_data["speed"]
               for collider in self.colliders:
                    collider.rect.pos += self.move_vector * self.platform_data["speed"]
               distance_a = sqrt((self.platform_data["from"].x - self.pos.x)**2 + (self.platform_data["from"].y - self.pos.y)**2)

               
               if (self.distance - distance_a) <= 0:
                    self.platform_data["direction"] = False
          else:
               self.pos -= self.move_vector * self.platform_data["speed"]
               for collider in self.colliders:
                    collider.rect.pos -= self.move_vector * self.platform_data["speed"]
               distance_a = sqrt((self.platform_data["to"].x - self.pos.x)**2 + (self.platform_data["to"].y - self.pos.y)**2)
               
               
               if (self.distance - distance_a) <= 0:
                    self.platform_data["direction"] = True
     
     def display(self , surface , camera_pos=pygame.Vector2(0,0)):
          
          surface.blit(self.surface , [self.pos.x - camera_pos.x , self.pos.y - camera_pos.y])
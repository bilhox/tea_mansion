import os
import pygame
import json

from xml.etree.ElementTree import *
from pygame.locals import *
from scripts.entity import Book, Bookshelf, Power
from scripts.particles import *
from scripts.form import *
from scripts.camera import *
from math import *
from copy import *
from random import *
from scripts.unclassed_functions import *

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
     
     special_tiles = {}
     
     for special_tile in root.findall("tile"):
          tile_id = special_tile.get("id")
          tile_type = special_tile.get("type")
          
          properties = {}
          
          properties["type"] = tile_type
          
          for property in special_tile.find("properties").findall("property"):
               properties[property.get("name")] = property.get("value")
          
          special_tiles[int(tile_id)] = properties
     
     return tiles , special_tiles , tile_size[0]

class TileMap():
     
     def __init__(self , chunk_size=[4,4]):
          
          self.tileset = []
          self.size = [0,0]
          self.collider_chunks = {}
          self.layers = {}
          self.objects = {}
          self.deco_objects = []
          self.platforms = []
          self.chunk_size = chunk_size
          self.tilesize = 0
          self.books = []
          self.powers = []
          
     def get_collider_by_data(self , key , pos):
          
          properties = self.special_tiles[key]
          
          rect = FloatRect(pos , pygame.Vector2(8,8))
          
          if properties["collider_type"] == "trap":
               if properties["orientation"] == "top":
                    rect.size = pygame.Vector2(6 , 4)
                    rect.pos.y += 4
                    rect.pos.x += 1
               elif properties["orientation"] == "down":
                    rect.size = pygame.Vector2(6 , 4)
                    rect.pos.y -= 4
                    rect.pos.x += 1
               elif properties["orientation"] == "right":
                    rect.size = pygame.Vector2(4 , 6)
                    rect.pos.y += 1
               elif properties["orientation"] == "left":
                    rect.size = pygame.Vector2(4 , 6)
                    rect.pos.x += 4
                    rect.pos.y += 1
          
          return Collider(rect , self.special_tiles[key]["collider_type"])
          
     def load_map(self , map_path):
          root = parse(map_path).getroot()
          self.tileset , self.special_tiles , self.tilesize = load_tileset(os.path.join(os.path.dirname(map_path) , root.find("tileset").get("source")))
          self.size[0] = int(root.get("width"))
          self.size[1] = int(root.get("height"))
          
          layer_datas = {}
          
          # preparing the layers , by putting all values in a layer ,  into a 2D array
          for layer in root.findall("layer"):
               data = layer.find("data").text
               data = data.strip("\n").splitlines()
               t_tab = []
               
               for line in data:
                    l = line.strip(",").split(",")
                    t_tab.append(l)
               
               layer_datas[layer.get("name")] = t_tab
          
          # Starting with the object layer
          # it store some main coordinates like player start position
          # it's also for moving platforms and books
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
                         elif prop_name == "pause_time":
                              platform_data["pause_time"] = float(prop.get("value"))
                         elif prop_name == "layers_included":
                              layer_names = prop.get("value").split(";")
                              for layer_name in layer_names:
                                   t_tab = layer_datas[layer_name]
                                   for y in range(size[1]//self.tilesize):
                                        for x in range(size[0]//self.tilesize):
                                             if int(t_tab[int(y+(pos.y // self.tilesize))][int(x+(pos.x // self.tilesize))]) == 0: continue
                                             if (layer_name == "colliders"):
                                                  collider = self.get_collider_by_data(int(t_tab[int(y+(pos.y // self.tilesize))][int(x+(pos.x // self.tilesize))])-1, pygame.Vector2(pos.x+x*self.tilesize , pos.y+y*self.tilesize))
                                                  collider.move_above = True
                                                  colliders.append(collider)
                                             else:
                                                  surf = self.tileset[int(t_tab[int(y+(pos.y // self.tilesize))][int(x+(pos.x // self.tilesize))])-1]
                                                  surface.blit(surf , [x*self.tilesize , y*self.tilesize])
                                             t_tab[int(y+(pos.y // self.tilesize))][int(x+(pos.x // self.tilesize))] = "0"
                    
                    self.platforms.append(Platform(pos,surface , colliders , platform_data))
               elif obj.get("type") == "book":
                    self.books.append(Book(pygame.Vector2(float(obj.get("x")) , float(obj.get("y"))) , pygame.Vector2(8,8)))
               elif obj.get("type") == "power":
                    self.powers.append(Power(pygame.Vector2(float(obj.get("x")) , float(obj.get("y"))) , obj.find("properties").find("property").get("value")))
               elif obj.get("type") == "bookshelf":
                    if "bookshelfs" not in self.objects.keys():
                         self.objects["bookshelfs"] = []
                    self.objects["bookshelfs"].append({
                         "coord":pygame.Vector2(float(obj.get("x")) , float(obj.get("y"))),
                         "n_books":int(obj.find("properties").find("property").get("value"))
                         })
               else:
                    data = {}
                    name = obj.get("name")
                    data['type'] = obj.get("type")
                    data["coord"] = pygame.Vector2(float(obj.get("x")) , float(obj.get("y")))
                    self.objects[name] = data
          
          # iteration through layers
          for key in layer_datas:
               t_tab = layer_datas[key]
               # specific process with the layer for colliders
               if key == "colliders":
                    for cy in range(0 , self.size[1] // 4):
                         for cx in range(0 , self.size[0] // 4):
                              c_chunk = []
                              pos = f"{cx},{cy}"
                              for y in range(cy*4 , (cy+1)*4):
                                   # print(y)
                                   for x in range(cx*4 , (cx+1)*4):
                                        if (t_tab[y][x] != "0"):
                                             collider = self.get_collider_by_data(int(t_tab[y][x])-1 , pygame.Vector2(x*self.tilesize , y*self.tilesize))
                                             c_chunk.append(collider)   
                              if c_chunk != []:
                                   self.collider_chunks[pos] = c_chunk
               else:
                    layer_data = {}
                    for cy in range(0 , self.size[1] // self.chunk_size[1]):
                         for cx in range(0 , self.size[0] // self.chunk_size[0]):
                              chunk_surf = pygame.Surface([self.tilesize*self.chunk_size[0] , self.tilesize*self.chunk_size[1]] , SRCALPHA)
                              pos = f"{cx},{cy}"
                              py = 0
                              for y in range(cy*self.chunk_size[1] , (cy+1)*self.chunk_size[1]):
                                   px = 0
                                   for x in range(cx*self.chunk_size[0] , (cx+1)*self.chunk_size[0]):
                                        if (t_tab[y][x] != "0"):
                                             if not int(t_tab[y][x])-1 in self.special_tiles.keys() or self.special_tiles[int(t_tab[y][x])-1]["type"] != "decoration":
                                                  chunk_surf.blit(self.tileset[int(t_tab[y][x])-1] , [px*self.tilesize , py*self.tilesize])
                                             elif (self.special_tiles[int(t_tab[y][x])-1]["deco_type"] == "torch"):
                                                  self.deco_objects.append(Torch(pygame.Vector2([(cx*self.chunk_size[0]+px)*self.tilesize ,(cy*self.chunk_size[1]+py)*self.tilesize]) , self.tileset[int(t_tab[y][x])-1]))
                                   
                                        px += 1
                                   py += 1
                              layer_data[pos] = chunk_surf  
                    self.layers[key] = layer_data
          
          # print(self.chunks)
          
     def get_platform_colliders(self):
          collider = []
          for platform in self.platforms:
               collider.extend(platform.colliders)
          
          return collider
     
     def update_platforms(self , dt , max_fps=60):
          for platform in self.platforms:
               platform.update(dt , max_fps)
     
     def update_books(self , dt , max_fps=60):
          for book in self.books:
               book.update(dt , max_fps)
     
     def display_platforms(self , surface , camera_pos=pygame.Vector2(0,0)):
          for platform in self.platforms:
               platform.display(surface , camera_pos)

     def display_layer(self , surface , layer , chunk , offset=pygame.Vector2(0,0)):
          
          try: 
               pos = [int(val) for val in chunk.split(",")]
               pos[0] *= self.chunk_size[0]*self.tilesize
               pos[1] *= self.chunk_size[1]*self.tilesize
               surface.blit(self.layers[layer][chunk] , [(pos[0] - offset.x) , (pos[1] - offset.y)])
          except:
               pass
     
     def display_books(self , surface , offset):
          for book in self.books:
               book.display(surface , offset)     
                         
     

class Tile():
     
     def __init__(self , pos , surface):
          self.pos = pos
          self.surface = surface

class Platform():
     
     def __init__(self , pos : pygame.Vector2, surface : pygame.Surface , colliders : list[Collider] , platform_data : dict):
          self.pos = pos
          self.surface = surface
          self.colliders = colliders
          self.paused = False
          self.pause_timer = 0
          self.platform_data = platform_data
          
          self.distance = sqrt((self.platform_data["to"].x - self.platform_data["from"].x)**2 + (self.platform_data["to"].y - self.platform_data["from"].y)**2)
          try:
               self.move_vector = (self.platform_data["to"] - self.platform_data["from"]).normalize()
          except:
               self.move_vector = pygame.Vector2(0,0)
          
          self.pause_time = self.platform_data["pause_time"] if "pause_time" in self.platform_data.keys() else 0
               
     def update(self , dt , max_fps=60):
          # print(self.pos)
          if not self.paused:
               movement = self.move_vector * self.platform_data["speed"] * dt * max_fps
               if (self.platform_data["direction"]):
                    
                    distance_a = sqrt((self.platform_data["from"].x - self.pos.x + movement.x)**2 + (self.platform_data["from"].y - self.pos.y + movement.y)**2)
                    
                    if (self.distance - distance_a) <= 0:
                         self.platform_data["direction"] = False
                         self.paused = True
                         movement = self.platform_data["to"] - self.pos
                    
                    self.pos += movement
                    for collider in self.colliders:
                         collider.move(movement)
               else:
                    
                    distance_a = sqrt((self.platform_data["to"].x - self.pos.x - movement.x)**2 + (self.platform_data["to"].y - self.pos.y - movement.y)**2)
                    
                    if (self.distance - distance_a) <= 0:
                         self.platform_data["direction"] = True
                         self.paused = True
                         movement = -(self.platform_data["from"] - self.pos)
                    
                    self.pos -= movement
                    for collider in self.colliders:
                         collider.move(-movement)
                    
                    
          else:
               self.pause_timer += dt
               if self.pause_time - self.pause_timer <= 0:
                    self.paused = False
                    self.pause_timer = 0
     
     def display(self , surface , camera_pos=pygame.Vector2(0,0)):
          
          surface.blit(self.surface , [self.pos.x - camera_pos.x , self.pos.y - camera_pos.y])


class Level_Manager:
     
     def __init__(self , json_path):
          r = open(json_path)
          data = json.load(r)
          r.close()
          
          self.levels = data["levels"]
          self.load(data["default"])
     
     def load(self , key):
          
          self.current_level = key
          
          self.tilemap = TileMap(chunk_size=[44 , 32])
          self.tilemap.load_map(self.levels[self.current_level]["path"])
          
          self.name = self.levels[self.current_level]["name"]
          self.books = copy(self.tilemap.books)
          self.total_books_needed = 0
          
          self.bookshelfs = []
          for bs_data in self.tilemap.objects["bookshelfs"]:
               self.total_books_needed += bs_data["n_books"]
               self.bookshelfs.append(Bookshelf(bs_data["coord"] , bs_data["n_books"]))
          

class Torch:
     
     def __init__(self , pos , texture):
          self.pos = pos
          self.texture = texture
          
          self.light = pygame.image.load("./assets/light.png").convert_alpha()
          self.light = pygame.transform.scale(self.light , [128 , 128])
          
          self.light = mult_image(self.light , [90 , 50 , 50])
          
          self.part_sys = Particle_system()
          self.part_imgs = get_imgs_from_sheet("./assets/particles/burn_particles-Sheet.png" , 4)
          self.colors = [
               [255, 103, 43],
               [222, 80, 24],
               [255, 140, 25],
               [129, 129, 127]
               ]
     
     def update(self , dt , max_fps=60):
          
          if len(self.part_sys.particles) < 20:
               angle = radians(randint(-130 , -50))
               motion = pygame.Vector2(cos(angle) * uniform(4 , 7) , sin(angle) * uniform(6 , 10))
               self.part_sys.particles.append(Particle(self.pos+pygame.Vector2(3 , 2) , motion , 1.2 , self.part_imgs.copy() , random() , choice(self.colors)))

          self.part_sys.update(dt)
          
     def display_light(self , surface , offset=pygame.Vector2(0,0)):
          light_size = pygame.Vector2(self.light.get_size())
          light_offset = offset - (pygame.Vector2(4,4) - light_size / 2)
          surface.blit(self.light , [self.pos.x - light_offset.x , self.pos.y - light_offset.y] , special_flags=BLEND_RGB_ADD)
     
     def display(self , surface , offset=pygame.Vector2(0,0)):
          surface.blit(self.texture , [self.pos.x - offset.x , self.pos.y - offset.y])
          self.part_sys.draw(surface , offset)
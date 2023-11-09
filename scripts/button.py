import pygame

class Button():
     
     def __init__(self , pos : list[int , int] , size : list[int , int] , button_data : dict):
          self.rect = pygame.Rect(pos , size)
          self.case = "NOTHING"
          self.textures = []
          
          self.data = button_data
          
          if (not "textures" in self.data.keys()):
               textures = {}
               cases = ["nothing" , "hover" , "clicked"]
               colors = [
                    [220 , 220 , 220],
                    [180 , 180 , 180],
                    [100 , 100 , 100]
               ]
               
               for i in range(3):
                    texture = pygame.Surface(self.rect.size)
                    texture.fill(colors[i])
                    textures[cases[i]] = texture

               self.data["textures"] = textures
               
          self.current_texture = self.data["textures"]["nothing"]
     
     def update(self , event : pygame.event.Event):
          
          m_pos = pygame.mouse.get_pos()
          rect = self.rect
          if ("parent" in self.data.keys()):
               parent = self.data["parent"]
               rect = pygame.Rect([rect.x + parent.rect.x , rect.y + parent.rect.y],rect.size)
          
          if(event.type == pygame.MOUSEBUTTONDOWN):
               if (rect.collidepoint(event.pos)):
                    self.case = "CLICKED"
          elif(event.type == pygame.MOUSEBUTTONUP):
               if (self.case == "CLICKED" and rect.collidepoint(event.pos)):
                    if("target" in self.data.keys()):
                         if("parent" in self.data.keys()):
                              self.data["target"](self.data["parent"])
                         else:
                              self.data["target"]()
                    self.case = "HOVER"
               else:
                    self.case = "NOTHING"
          else:
               if (not self.case == "CLICKED"):
                    if (self.rect.collidepoint(m_pos)):
                         self.case = "HOVER"
                    else:
                         self.case = "NOTHING"
                    
          match self.case:
               case "NOTHING":
                    self.current_texture = self.data["textures"]["nothing"]
               case "HOVER":
                    self.current_texture = self.data["textures"]["hover"]
               case  "CLICKED":
                    self.current_texture = self.data["textures"]["clicked"]
               
     
     def display(self , screen : pygame.Surface):
          
          rect = self.rect
          if ("parent" in self.data.keys()):
               parent = self.data["parent"]
               rect = pygame.Rect([rect.x + parent.rect.x , rect.y + parent.rect.y],rect.size)
          
          if(self.current_texture.get_height() <= rect.h and self.current_texture.get_width() <= rect.w):
               screen.blit(self.current_texture , [rect.x , rect.y])
          else:
               sub_surf = self.current_texture.subsurface(pygame.Rect([0,0],rect.size))
               screen.blit(sub_surf , [rect.x , rect.y])
          
          bd_keys = self.data.keys()
          
          if("text-data" in bd_keys):
               text_data = self.data["text-data"]
               td_keys = text_data.keys()
               pos = [0,0]
               if("centered" in td_keys and text_data["centered"]):
                    pos = [rect.x + rect.w // 2 - text_data["font"].size(text_data["content"])[0] // 2,
                           rect.y + rect.h // 2 - text_data["font"].size(text_data["content"])[1] // 2
                           ]
               else:
                    pos = [rect.x , rect.y]
               
               
               if("color" in td_keys):
                    screen.blit(text_data["font"].render(text_data["content"] , True , text_data["color"]) , pos)
               else:
                    screen.blit(text_data["font"].render(text_data["content"] , True , (0,0,0)) , pos)
     
     @staticmethod
     def load_button(component , modules):
          m_event_args = component.get("event")
          button_data = {}
          
          if m_event_args != None and m_event_args != "":
               args = m_event_args.split(".")
               event = getattr(modules[args[0]] , args[1])
               button_data["target"] = event
          
          
          transform = component.find("transform")
          text_data = component.find("text")
          
          if transform != None:
               
               t_pos = transform.get("position").split(",")
               pos = [int(coord) for coord in t_pos]
               
               t_size = transform.get("size").split(",")
               size = [int(val) for val in t_size]
               
               if(text_data != None):
                    txt_data = {}
                    
                    for att in text_data.attrib.items():
                         match att[0]:
                              case "content":
                                   txt_data["content"] = att[1]
                              case "centered":
                                   txt_data["centered"] = eval(att[1])
                    
                    font_data = text_data.find("font")
                    if font_data == None: return None
                    font = pygame.font.Font(None if font_data.get("path") == "None" else font_data.get("path"),
                                             int(font_data.get("size")))
                    txt_data["font"] = font
                    button_data["text-data"] = txt_data
               
               button = Button(pos , size , button_data)
               return button
          else:
               return None
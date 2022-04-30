import pygame

from pygame.locals import *
from scripts.unclassed_functions import *
from math import *
from copy import *
from random import *


class Particle():
     
     def __init__(self , pos , motion , decay_rate , particle_imgs , duration , color=None):
          
          self.motion = motion
          self.origin_motion = copy(self.motion)
          self.pos = pos
          self.decay_rate = decay_rate
          self.color = color
          self.timer = 0
          self.frame = 0
          self.duration = duration
          self.alive = True
          self.particle_imgs = particle_imgs
          
          if color != None:
               for i in range(len(self.particle_imgs)):
                    self.particle_imgs[i] = swap_color(self.particle_imgs[i] , [255 , 255 , 255] , color)


     def draw(self , surface , offset=pygame.Vector2(0,0)):
          
          if self.alive:
               surface.blit(self.particle_imgs[self.frame] , self.pos-offset)
     
     def update(self , dt):
          self.timer += self.decay_rate * dt
          if self.duration - self.timer <= 0:
               self.frame += 1
               self.timer = 0
               if len(self.particle_imgs)-1 < self.frame:
                    self.alive = False
          
          self.pos += self.motion * dt
          
          
class Particle_system():
     
     def __init__(self):
          self.particles = []
          self.custom_update = None
     
     def update(self , dt):
          for particle in self.particles:
               if self.custom_update != None:
                    self.custom_update(particle , dt)
               particle.update(dt)
               if not particle.alive:
                    self.particles.remove(particle)
     
     def draw(self , surface , offset=pygame.Vector2(0,0)):
          for particle in self.particles:
               particle.draw(surface , offset) 
               

def particle_burst(particle_system , pos , amt , speed , part_imgs , duration , n_angles=None, color=None):
     
     if n_angles != None:
          angles = []
          for _ in range(n_angles):
               a = radians(randint(1 , 180))
               b = a+pi
               angles.append(a)
               angles.append(b)
     
     for i in range(amt):
          if n_angles == None:
               angle = radians(randint(1 , 360))
          else:
               angle = choice(angles)
          s = speed * uniform(0.2 , 1)
          motion = pygame.Vector2(cos(angle) * s , sin(angle) * s)
          particle_system.particles.append(Particle(copy(pos) , motion , 2 , part_imgs.copy() , duration , color))
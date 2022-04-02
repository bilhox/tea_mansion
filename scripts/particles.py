import pygame

from pygame.locals import *
from math import *
from copy import *
from random import *

class Particle():
     
     def __init__(self , pos , surface):
          self.timer = 0
          self.life_time = 1
          self.pos = pos
          self.speed = 1
          self.direction = pygame.Vector2(0,0)
          self.surface = surface
          self.end_life = False
     
     def update(self , dt , max_fps=60):
          self.pos += self.direction * self.speed * dt * max_fps
          self.timer += dt
          
          if (self.life_time - self.timer) <= 0:
               self.end_life = True
     
     def display(self , surface , offset=pygame.Vector2(0,0)):
          
          surface.blit(self.surface , [self.pos.x - offset.x , self.pos.y - offset.y])

class Particle_data():
     
     def __init__(self):
          
          self.startpos = pygame.Vector2(0,0)
          self.beginning_angle = -80
          self.end_angle = -100
          self.min_speed = 1
          self.max_speed = 1
          self.min_life_time = 1
          self.max_life_time = 1
          self.particle_spawncoef = 1
          self.adding_particle_intervall = 10
          self.particle_surface = None
          self.speed_multiplicator = 0
          
     def set_intervall(self , type : str , a , b):
          if (type == "life_time"):
               self.min_life_time = a
               self.max_life_time = b
          elif (type == "speed"):
               self.min_speed = a
               self.max_speed = b
          elif (type == "angle"):
               self.beginning_angle = a
               self.end_angle = b

class Particle_system():
     
     def __init__(self , particle_data : Particle_data):
          
          self.data = particle_data
          self.particles = []
          self.tick_timer = 0
          self.infinite_spawn = False
     
     def update(self , dt , max_fps=60):
          
          if self.infinite_spawn:
               self.tick_timer += 1
               self.spawnparticles(self.particle_spawncoef)
               
          for particle in self.particles:
               particle.update(dt , max_fps)
               
               particle.speed *= self.data.speed_multiplicator**(dt * max_fps)
               if particle.end_life:
                    self.particles.remove(particle)
          
          # l = 0
          # while (l < len(self.particles)):
          #      self.particles[l].update(dt , max_fps)
               
          #      self.particles[l].speed *= self.data.speed_multiplicator**(dt * max_fps)
          #      if self.particles[l].end_life:
          #           self.particles.remove(self.particles[l])
          #           l-=1
               
          #      l+=1
               
          #      try:
          #           self.particles[l+1].update(dt , max_fps)
               
          #           self.particles[l+1].speed *= self.data.speed_multiplicator**(dt * max_fps)
          #           if self.particles[l+1].end_life:
          #                self.particles.remove(self.particles[l+1])
          #                l-=1
          #           l+=1
          #      except:
          #           pass
               
     
     def spawnparticles(self , amount , circular=False):
          angle = 0
          for i in range (amount):
               if (self.tick_timer % self.data.adding_particle_intervall) == 0:
                    particle = Particle(copy(self.data.startpos) , self.data.particle_surface)
                    particle.speed = uniform(self.data.min_speed , self.data.max_speed)
                    t_dir = None
                    if circular:
                         angle += (360 / amount)
                         t_dir = [cos(radians(angle)),sin(radians(angle))]
                    else:
                         t_dir = [cos(radians(self.data.beginning_angle+uniform(0 , self.data.end_angle))),sin(radians(self.data.beginning_angle+uniform(0 , self.data.end_angle)))]
                    
                    particle.direction = pygame.Vector2(t_dir)
                    particle.life_time = uniform(self.data.min_life_time , self.data.max_life_time)
                    self.particles.append(particle)
                    
          
     def display(self , surface , offset=pygame.Vector2(0,0)):
          for particle in self.particles:
               particle.display(surface , offset)
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
          self.turning = False
          self.max_life_time = 1
          self.particle_spawncoef = 1
          self.adding_particle_intervall = 10
          self.particle_surface = None
          self.speed_reducing_coef = 0
     
     def set_spawnangle(self , angle_a , angle_b):
          self.beginning_angle = angle_a
          self.end_angle = angle_b

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
               if self.data.turning:
                    particle.direction = pygame.Vector2(
                         particle.direction.x * cos(radians(2))- particle.direction.y*sin(radians(2)),
                         particle.direction.x * sin(radians(2)) + particle.direction.y*cos(radians(2))
                    )
               
               particle.speed -= particle.speed * self.data.speed_reducing_coef
               if particle.end_life:
                    self.particles.remove(particle)
     
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
                         t_dir = [cos(uniform(radians(self.data.beginning_angle),radians(self.data.end_angle))),sin(uniform(radians(self.data.beginning_angle),radians(self.data.end_angle)))]
                    
                    particle.direction = pygame.Vector2(t_dir)
                    particle.life_time = uniform(self.data.min_life_time , self.data.max_life_time)
                    self.particles.append(particle)
                    
          
     def display(self , surface , offset=pygame.Vector2(0,0)):
          for particle in self.particles:
               particle.display(surface , offset)
     

               
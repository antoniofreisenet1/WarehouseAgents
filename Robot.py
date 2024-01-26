# Autor: Ivan Olmos Pineda


import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math
import numpy as np

from Stack import Stack

class Robot:
    def __init__(self, dim, vel, Scala, cube_list=None , stack_list=None):
        # vertices del cubo
        self.points = np.array([[-1.0, -1.0, 1.0], [1.0, -1.0, 1.0], [1.0, -1.0, -1.0], [-1.0, -1.0, -1.0],
                                [-1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, -1.0], [-1.0, 1.0, -1.0]])

        self.DimBoard = dim
        # Se inicializa una posicion aleatoria en el tablero
        self.Position = []
        self.Position.append(random.randint(-1 * self.DimBoard, self.DimBoard))
        self.Position.append(5.0)
        self.Position.append(random.randint(-1 * self.DimBoard, self.DimBoard))
        # Se inicializa un vector de direccion aleatorio
        self.Direction = []
        self.Direction.append(random.random())
        self.Direction.append(5.0)
        self.Direction.append(random.random())
        # Se normaliza el vector de direccion
        m = math.sqrt(self.Direction[0] * self.Direction[0] + self.Direction[2] * self.Direction[2])
        self.Direction[0] /= m
        self.Direction[2] /= m
        # Se cambia la magnitud del vector direccion
        self.Direction[0] *= vel
        self.Direction[2] *= vel
        self.Robots = []
        self.collision = 0
        self.colliding_with_stack = False
        self.radio = 2
        self.Scala = Scala
        self.cube_list = [] if cube_list is None else cube_list
        self.carrying_box = False
        self.carried_box = None
        self.MAX_ALLOWED_DISTANCE_TO_STACK = 10.0
        self.target_stack = None
        self.stack_list = [] if stack_list is None else stack_list
        
        self.state = "buscando_caja"  #Estados: buscando_caja, moviendo_caja, dejando_caja, moviendo_a_stack

    def pickup_box(self, cubo):
        if not self.carrying_box:
            self.carried_box = cubo
            self.carrying_box = True
            cubo.recolectado = True  # Marcar la caja como recolectada
            
    def drop_box(self, stack):
            if self.carrying_box:
                stack.add_box(self.carried_box)
                self.carried_box = None
                self.carrying_box = False
                
    
    
    def getRobots(self, Ncubos):
        self.Robots = Ncubos
        
    def distance_to(self, cubo):
        return math.sqrt((self.Position[0] - cubo.Position[0]) ** 2 +
                         (self.Position[2] - cubo.Position[2]) ** 2)
        
    def move_towards(self, cubo):
        # Calcular la dirección hacia la caja
        direction_x = cubo.Position[0] - self.Position[0]
        direction_z = cubo.Position[2] - self.Position[2]
        
        # Normalizar la dirección
        magnitude = math.sqrt(direction_x ** 2 + direction_z ** 2)
        if magnitude > 0:
            direction_x /= magnitude
            direction_z /= magnitude

        # Actualizar la dirección del robot
        self.Direction[0] = direction_x * self.Scala
        self.Direction[2] = direction_z * self.Scala

    def move_towards_stack(self, stack):
        # Calcular la dirección hacia el stack
        direction_x = stack.Position[0] - self.Position[0]
        direction_z = stack.Position[2] - self.Position[2]
        
        # Normalizar la dirección
        magnitude = math.sqrt(direction_x ** 2 + direction_z ** 2)
        if magnitude > 0:
            direction_x /= magnitude
            direction_z /= magnitude

        # Actualizar la dirección del robot
        self.Direction[0] = direction_x * self.Scala
        self.Direction[2] = direction_z * self.Scala

    def find_closest_stack(self, stacks):
        # Encontrar el stack más cercano
        
        if(stacks):
            closest_stack = min(stacks, key=lambda stack: self.distance_to_stack(stack))
            return closest_stack
        else:
            new_stack = Stack(self.Position, self.DimBoard)
            stacks.append(new_stack)
            closest_stack = new_stack
            return closest_stack
    
    def distance_to_stack(self, stack):
        return math.sqrt((self.Position[0] - stack.Position[0]) ** 2 +
                         (self.Position[2] - stack.Position[2]) ** 2)
        
    
    def update(self, cubos, stacks):
        self.CollisionDetection(cubos, stacks)
        

        if self.collision == 0:
            if not self.carrying_box and any(not cubo.recolectado for cubo in cubos): #self.collision is weird with the logic
                closest_cubo = min((cubo for cubo in cubos if not cubo.recolectado), key=lambda c: self.distance_to(c), default = None)
            
                if(closest_cubo):
                    self.move_towards(closest_cubo)
                    
                elif closest_cubo:
                    self.move_towards(closest_cubo)
                    
                    self.pickup_box(closest_cubo)
                    
            elif self.carrying_box:
                if self.colliding_with_stack and self.target_stack:
                    self.drop_box(self.target_stack)
                else:
                    closest_stack = self.find_closest_stack(stacks)
                if(closest_stack.is_full()):
                    new_stack = Stack(self.Position, self.DimBoard)
                    stacks.append(new_stack)
                    closest_stack = new_stack
                
                self.move_towards_stack(closest_stack)
                
                if(self.distance_to_stack(closest_stack) <= self.MAX_ALLOWED_DISTANCE_TO_STACK):
                    self.drop_box(closest_stack)
                    
                
        else:
            
            # Si hay colisión, dirigir el robot hacia otro lugar aleatorio
            new_direction = np.array([random.randint(-1 * self.DimBoard, self.DimBoard)- self.Position[0], #new x position
                                      0.0 - self.Position[1], #new y position
                                      random.randint(-1 * self.DimBoard, self.DimBoard)- self.Position[2]]) # new z position
            new_direction /= np.linalg.norm(new_direction)  # Normalizar el vector
            
            #if self.cube_list == []:
                
            # Si hay colisión, dirigir el robot hacia el origen (0, 0, 0) de manera más lenta
             #   new_direction = np.array([0.0 - self.Position[0], 0.0 - self.Position[1], 0.0 - self.Position[2]])
              #  new_direction /= np.linalg.norm(new_direction)  # Normalizar el vector

            # Generar velocidad aleatoria entre 0.1 y 1.0
            speed_factor = random.uniform(0.1, 0.3)

            self.Direction = new_direction * (self.Scala * speed_factor)  # Ajustar velocidad
            self.Position[0] += self.Direction[0]
            self.Position[2] += self.Direction[2]

            # Verificar si el robot ha llegado al origen y restablecer la colisión a 0
            if np.allclose(self.Position, [0.0, 0.0, 0.0], atol=1e-2):
                self.Direction[0]+=0.5
                print("Robot ha llegado al origen. Restableciendo colisión a 0.")
                self.collision = 0

        self.collision = 0
        self.update_position()


    def update_position(self):
        # Calcula la nueva posición basada en la dirección y velocidad actuales
        new_x = self.Position[0] + self.Direction[0]
        new_z = self.Position[2] + self.Direction[2]

        # Verifica si el robot se mantiene dentro de los límites del tablero
        if abs(new_x) <= self.DimBoard:
            self.Position[0] = new_x
        else:
            # Si el robot llega al borde del tablero, invierte su dirección
            self.Direction[0] *= -1.0
            self.Position[0] += self.Direction[0]

        if abs(new_z) <= self.DimBoard:
            self.Position[2] = new_z
        else:
            # Lo mismo para el eje Z
            self.Direction[2] *= -1.0
            self.Position[2] += self.Direction[2]

    
    def CollisionDetection(self, cubos, stacks):
        for obj in cubos:
            if(self != obj):
                d_x = self.Position[0] - obj.Position[0]
                d_z = self.Position[2] - obj.Position[2]
                distance = math.sqrt(d_x * d_x + d_z * d_z)

        # Usar radio en la comparación
                if distance - (self.radio + obj.radio) <= 10.0:
                    self.collision = 1
                    obj.Scale = 0.5 #Si la caja no se elimina se hace mas pequeña
                    obj.recolectado = True  # Marcar la caja como recolectada
                    self.carrying_box = True
                    del cubos[cubos.index(obj)]
        self.colliding_with_stack = False
        for stack in stacks:
            # Usar radio en la comparación para stacks
            if distance - self.radio < 1.0 and not stack.is_full(): #+ stack.radio???
                self.colliding_with_stack = True
                self.target_stack = stack


    def drawFaces(self):
        glBegin(GL_QUADS)
        glVertex3fv(self.points[0])
        glVertex3fv(self.points[1])
        glVertex3fv(self.points[2])
        glVertex3fv(self.points[3])
        glEnd()
        glBegin(GL_QUADS)
        glVertex3fv(self.points[4])
        glVertex3fv(self.points[5])
        glVertex3fv(self.points[6])
        glVertex3fv(self.points[7])
        glEnd()
        glBegin(GL_QUADS)
        glVertex3fv(self.points[0])
        glVertex3fv(self.points[1])
        glVertex3fv(self.points[5])
        glVertex3fv(self.points[4])
        glEnd()
        glBegin(GL_QUADS)
        glVertex3fv(self.points[1])
        glVertex3fv(self.points[2])
        glVertex3fv(self.points[6])
        glVertex3fv(self.points[5])
        glEnd()
        glBegin(GL_QUADS)
        glVertex3fv(self.points[2])
        glVertex3fv(self.points[3])
        glVertex3fv(self.points[7])
        glVertex3fv(self.points[6])
        glEnd()
        glBegin(GL_QUADS)
        glVertex3fv(self.points[3])
        glVertex3fv(self.points[0])
        glVertex3fv(self.points[4])
        glVertex3fv(self.points[7])
        glEnd()

    def draw(self):
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        glScaled(self.Scala, self.Scala, self.Scala)
        glColor3f(1.0, 0.0, 1.0)

        for cube in self.cube_list:
            cube.update()
            cube.draw()
            
        for stack in self.stack_list:
            stack.update()
            stack.draw()

        self.drawFaces()
        glPopMatrix()

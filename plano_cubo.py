import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

# Se carga el archivo de la clase Cubo
import sys

sys.path.append('..')
from Robot import Robot
from Cubo import Cubo
from Stack import Stack


screen_width = 500
screen_height = 500
# vc para el obser.
FOVY = 60.0
ZNEAR = 0.01
ZFAR = 900.0
# Variables para definir la posicion del observador
# gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
EYE_X = 300.0
EYE_Y = 0.0  # Modificamos para controlar la posición en el eje Y
EYE_Z = 300.0
CENTER_X = 0
CENTER_Y = 0
CENTER_Z = 0
UP_X = 0
UP_Y = 1
UP_Z = 0
# Variables para dibujar los ejes del sistema
X_MIN = -500
X_MAX = 500
Y_MIN = -500
Y_MAX = 500
Z_MIN = -500
Z_MAX = 500
# Dimension del plano
DimBoard = 200
# Variables para el control del observador
theta = 0.0
radius = 300

pygame.init()

# Modificar para controlar las variables de la simulación
cubos = []
ncubos = 50

robots = []
nrobots = 5

stacks = []
nstacks = 0

def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    # X axis in red
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(X_MIN, 0.0, 0.0)
    glVertex3f(X_MAX, 0.0, 0.0)
    glEnd()
    # Y axis in green
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, Y_MIN, 0.0)
    glVertex3f(0.0, Y_MAX, 0.0)
    glEnd()
    # Z axis in blue
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, Z_MIN)
    glVertex3f(0.0, 0.0, Z_MAX)
    glEnd()
    glLineWidth(1.0)


def lookat():
    global EYE_Y
    global radius
    # Modificamos la posición en el eje Y y ajustamos el radio para hacer zoom
    EYE_Y = radius * math.sin(math.radians(theta))
    radius = max(50, radius - 1)  # Ajusta la velocidad de acercamiento/alejamiento aquí
    glLoadIdentity()
    gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)


def Init():
    global cubos
    global stacks
    
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: cubos")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width / screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)
    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    for i in range(ncubos):
        cubos.append(Cubo(DimBoard, 0.0))

    for obj in cubos:
        obj.getCubos(cubos)


    for i in range(nrobots):
        robots.append(Robot(DimBoard, 0.9, 6))

    for obj in robots:
        obj.getRobots(robots)
    
    for i in range(nstacks):
        stacks.append(Stack(DimBoard, 0.9, 6))
        
    for obj in stacks:
        obj.get_stacks(stacks)
    
    cubos = [cubo for cubo in cubos if not cubo.recolectado]
    stacks = [stack for stack in stacks if not stack.is_full()]


# Se dibuja el plano con una textura de madera

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # Se dibuja el plano gris
    glColor3f(1.0, 0.5, 0.0)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()


    # Se dibuja cubos
    #objetos = robots + cubos

    for obj in cubos:
        obj.draw()

    for obj in robots:
        obj.draw()
        obj.update(cubos, stacks)
        
    for obj in stacks:
        obj.draw()
    


done = False
Init()
#done = False


while not done:
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        if theta < 1.0:
            theta = 360.0
        else:
            theta += -1.0
        lookat()
    if keys[pygame.K_RIGHT]:
        if theta > 359.0:
            theta = 0
        else:
            theta += 1.0
        lookat()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    display()

    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()



"""
This module contains functions that create images of a given 3d object 
from a given camera perspective.
"""

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from tools.objloader import *
import sys
from dataclasses import dataclass, asdict
import glfw
import cv2

from settings import *


@dataclass
class Camera:
    rotation: np.ndarray = None
    position: np.ndarray = None

@dataclass
class Control:
    rotate: bool
    move: bool

def rotation_vector_to_matrix(rotation_vector):
    rotation_vector = np.array([-rotation_vector[0], -rotation_vector[1], -rotation_vector[2]])
    rot = cv2.Rodrigues(rotation_vector)[0]
    # Make the rotation matrix homogeneous
    rot = np.concatenate((rot, np.zeros((1, 3))), axis=0)
    rot = np.concatenate((rot, np.zeros((4, 1))), axis=1)
    rot[3, 3] = 1
    return rot

def quaternion_to_matrix(q):
    """
    Convert a quaternion to a 4x4 homogeneous rotation matrix.

    :param q: A 4-element array representing the quaternion in the form [w, x, y, z].
    :return: A 4x4 numpy array representing the rotation matrix.
    """

    # Normalize the quaternion
    # q /= np.linalg.norm(q)

    # Extract the components of the quaternion
    x, y, z, w = q

    # Compute the elements of the rotation matrix
    m11 = 1 - 2 * (y**2 + z**2)
    m12 = 2 * (x*y - w*z)
    m13 = 2 * (x*z + w*y)
    m14 = 0

    m21 = 2 * (x*y + w*z)
    m22 = 1 - 2 * (x**2 + z**2)
    m23 = 2 * (y*z - w*x)
    m24 = 0

    m31 = 2 * (x*z - w*y)
    m32 = 2 * (y*z + w*x)
    m33 = 1 - 2 * (x**2 + y**2)
    m34 = 0

    m41 = 0
    m42 = 0
    m43 = 0
    m44 = 1

    # Return the rotation matrix
    return np.array([[m11, m12, m13, m14],
                     [m21, m22, m23, m24],
                     [m31, m32, m33, m34],
                     [m41, m42, m43, m44]])


def init(focal_distance, principal_point, video_size=(800, 600)):
    glfw.init()
    viewport = video_size
    glfw.window_hint(glfw.SAMPLES, 4)
    clock = pygame.time.Clock()
    window = glfw.create_window(*viewport, "OpenGL window", None, None)
    framebuffer_size = glfw.get_framebuffer_size(window)
    if not window:
        glfw.terminate()
        print("GLFW window creation failed")
        sys.exit()
    glfw.make_context_current(window)
    obj = OBJ('objects/rubberduckie/rubberduckie.obj')

    glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)  # enables anti-aliasing
    # most obj files expect to be smooth-shaded
    glShadeModel(GL_SMOOTH)

    # LOAD TEXTURES
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # texture = loadTexture('objects/rubberduckie/rubberduckie.png')

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity() # reset the camera
    width, height = viewport
    # focal_distance = 300
    fov = (2 * np.arctan(height / (2 * focal_distance))) * 180 / np.pi
    print(fov)
    gluPerspective(fov, width/float(height), 1, 100.0) # intrinsic camera params
    glMatrixMode(GL_MODELVIEW)
    return window, obj, clock, Camera(), framebuffer_size

first_rot = None
def draw(camera: Camera, obj, window, clock, frame=None, quaternion=None):
    global first_rot
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # If frame is not None, draw the frame as the background
    if frame is not None:
        glLoadIdentity()
        glWindowPos2i(0, 0)
        buffer_size = glfw.get_framebuffer_size(window)
        frame = np.flip(frame, axis=0)
        # frame = np.concatenate((frame, np.zeros((frame.shape[0], 1), dtype=np.uint8)), axis=1)
        glDrawPixels(*buffer_size, GL_LUMINANCE, GL_UNSIGNED_BYTE, frame)
        # clear the depth buffer so that the frame is not occluded
        glClear(GL_DEPTH_BUFFER_BIT)


    if quaternion:
        rot = quaternion_to_matrix(quaternion)
    else:
        rot = rotation_vector_to_matrix(camera.rotation)
    rot = np.linalg.inv(rot)


    from itertools import product
    for i, j, k in product([-2, -1, 0, 1, 2], repeat=3):
        # RENDER OBJECT
        glLoadIdentity()
        # if i == j == k == 0:
        #     continue
        pos = -camera.position.T
        glMultMatrixd(rot) # Rotate object
        glTranslate(OBJECT_POSITION[0] * i, OBJECT_POSITION[1] * j, OBJECT_POSITION[2] * k) # Move object away from camera
        # glTranslate(*OBJECT_POSITION ) # Move object away from camera
        glTranslate(*pos.T) # TODO: fix this
        glCallList(obj.gl_list)

    glfw.swap_buffers(window) # draw the current frame
    clock.tick(60) # limit to 60 fps

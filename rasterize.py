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
from PIL import Image

from settings import *


@dataclass
class Camera:
    rotation: np.ndarray = None
    position: np.ndarray = None

buffer_size = None

def rotation_vector_to_matrix(rotation_vector):
    rotation_vector = np.array([-rotation_vector[0], -rotation_vector[1], -rotation_vector[2]])
    rot = cv2.Rodrigues(rotation_vector)[0]
    # Make the rotation matrix homogeneous
    rot = np.concatenate((rot, np.zeros((1, 3))), axis=0)
    rot = np.concatenate((rot, np.zeros((4, 1))), axis=1)
    rot[3, 3] = 1
    return rot

def matrix_to_quaternion(m):
    if m[2,2] < 0:
        if m[0,0] > m[1,1]:
            t = 1 + m[0,0] - m[1,1] - m[2,2]
            q = (t, m[0,1] + m[1,0], m[2,0] + m[0,2], m[1,2] - m[2,1])
        else:
            t = 1 - m[0,0] + m[1,1] - m[2,2]
            q = (m[0,1] + m[1,0], t, m[1,2] + m[2,1], m[2,0] - m[0,2])
    else:
        if m[0,0] < -m[1,1]:
            t = 1 - m[0,0] - m[1,1] + m[2,2]
            q = (m[2,0] + m[0,2], m[1,2] + m[2,1], t, m[0,1] - m[1,0])
        else:
            t = 1 + m[0,0] + m[1,1] + m[2,2]
            q = (m[1,2] - m[2,1], m[2,0] - m[0,2], m[0,1] - m[1,0], t)

    q = np.array(q)
    q *= 0.5 / np.sqrt(t)

    return q

def window_update(window, width, height):
    global buffer_size
    # Round width, height up to the nearest multiple of 4
    if width % 4 != 0 or height % 4 != 0:
        width = width + (4 - width % 4) % 4
        height = height + (4 - height % 4) % 4
        glfw.set_window_size(window, width, height)

    buffer_size = glfw.get_framebuffer_size(window)
    glViewport(0, 0, width, height)

def init(focal_distance, principal_point, video_size=(800, 600)):
    global buffer_size
    glfw.init()
    viewport = video_size
    glfw.window_hint(glfw.SAMPLES, 4)
    clock = pygame.time.Clock()
    window = glfw.create_window(*viewport, "OpenGL window", None, None)
    glfw.set_window_close_callback(
        window, lambda x: glfw.set_window_should_close(window, True))
    glfw.set_window_size_callback(window, window_update)
    buffer_size = glfw.get_framebuffer_size(window)
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
    print("FOV: ", fov)
    gluPerspective(fov, width/float(height), 1, 100.0) # intrinsic camera params
    glMatrixMode(GL_MODELVIEW)
    return window, obj, clock, Camera()

def handle_events(window):
    glfw.poll_events()

    if glfw.window_should_close(window):
        glfw.terminate()
        sys.exit()

def draw(camera: Camera, obj, window, clock, frame=None, quaternion=None):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # If frame is not None, draw the frame as the background
    if frame is not None:
        glLoadIdentity()
        glWindowPos2i(0, 0)
        frame = np.flip(frame, axis=0)
        # frame = np.concatenate((frame, np.zeros((frame.shape[0], 1), dtype=np.uint8)), axis=1)
        b_size = buffer_size
        glDrawPixels(*buffer_size, GL_BGR, GL_UNSIGNED_BYTE, frame)
        # clear the depth buffer so that the frame is not occluded
        glClear(GL_DEPTH_BUFFER_BIT)


    rot = rotation_vector_to_matrix(camera.rotation)
    rot = np.linalg.inv(rot)

    from itertools import product
    for i, j, k in product([-2, -1, 0, 1, 2], repeat=3):
        # RENDER OBJECT
        glLoadIdentity()
        pos = -camera.position.T
        glMultMatrixd(rot) # Rotate object
        glTranslate(OBJECT_POSITION[0] * i, OBJECT_POSITION[1] * j, OBJECT_POSITION[2] * k) # Move object away from camera
        # glTranslate(*OBJECT_POSITION ) # Move object away from camera
        glTranslate(*pos.T) # TODO: fix this
        glCallList(obj.gl_list)

    glfw.swap_buffers(window) # draw the current frame

    screenshot = glReadPixels(0,0,*buffer_size,GL_BGR,GL_UNSIGNED_BYTE)
    # glReadBuffer(GL_BACK)
    snapshot = Image.frombuffer("RGB",buffer_size,screenshot,"raw", "RGB", 0, 0)
    snapshot = np.array(snapshot)
    snapshot = cv2.flip(snapshot,0)

    return snapshot

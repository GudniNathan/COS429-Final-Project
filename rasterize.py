"""
This module contains functions that create images of a given 3d object 
from a given camera perspective.
"""

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from objloader import *
import sys
from dataclasses import dataclass, asdict
import glfw
import cv2


@dataclass
class Camera:
    rx: float
    ry: float
    tx: float
    ty: float
    tz: float

    def update(self, new):
        for key, value in new.items():
            if hasattr(self, key):
                setattr(self, key, value)

@dataclass
class Control:
    rotate: bool
    move: bool

def init(focal_distance, principal_point, video_size=(800, 600)):
    glfw.init()
    viewport = video_size
    # glfw.window_hint(glfw.SAMPLES, 4)
    clock = pygame.time.Clock()
    window = glfw.create_window(*viewport, "OpenGL window", None, None)
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
    return window, obj, clock, Camera(0,0,0,0,0)

def main():
    window, obj, clock, camera = init(300, (400, 300), (800, 600))
    z_dist = 20
    camera = Camera(0, 0, 0, 0, z_dist)
    control = Control(False, False)
    path = [Camera(0, 0, 0, n//100 - 2, 5) for n in range(0, 500)]
    path.reverse()
    while not glfw.window_should_close(window):
        handle_events(camera, control, path)
        draw(camera, obj, window, clock)
    glfw.terminate()


def handle_events(camera: Camera, control: Control, path: list):
    if len(path) == 0:
        sys.exit()
    camera.update(asdict(path[-1]))
    path.pop()
    # for e in pygame.event.get():
    #     if e.type == QUIT:
    #         sys.exit()
    #     elif e.type == KEYDOWN and e.key == K_ESCAPE:
    #         sys.exit()
        # elif e.type == MOUSEBUTTONDOWN:
        #     if e.button == 4: camera.zpos = max(1, camera.zpos-1)
        #     elif e.button == 5: camera.zpos += 1
        #     elif e.button == 1: control.rotate = True
        #     elif e.button == 3: control.move = True
        # elif e.type == MOUSEBUTTONUP:
        #     if e.button == 1: control.rotate = False
        #     elif e.button == 3: control.move = False
        # elif e.type == MOUSEMOTION:
        #     i, j = e.rel
        #     if control.rotate:
        #         camera.rx += i
        #         camera.ry += j
        #     if control.move:
        #         camera.tx += i / 20.
        #         camera.ty -= j / 20.


def draw(camera: Camera, obj, window, clock, frame=None):
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # If frame is not None, draw the frame as the background
    if frame is not None:
        glLoadIdentity()
        glWindowPos2i(0, 0)
        window_size = glfw.get_window_size(window)
        frame = np.flip(frame, axis=0)
        frame = np.concatenate((frame, np.zeros((frame.shape[0], 1), dtype=np.uint8)), axis=1)
        glDrawPixels(*window_size, GL_LUMINANCE, GL_UNSIGNED_BYTE, frame)
        # clear the depth buffer so that the frame is not occluded
        glClear(GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    rot = cv2.Rodrigues(camera.rotation)[0]
    axis = [rot[2][1] - rot[1][2], rot[0][2] - rot[2][0], rot[1][0] - rot[0][1]]
    if np.linalg.norm(axis) != 0:
        axis = axis / np.linalg.norm(axis)
    angle = np.arccos((np.trace(rot) - 1) / 2)
    # RENDER OBJECT
    pos = ((camera.position.T / 10) + [0, -10, 0])[0]
    # swap y and z
    pos[1], pos[2] = pos[2], pos[1]
    glTranslate(*pos.T) # TODO: fix this
    glRotate(angle * 180 / np.pi, *axis)
    glCallList(obj.gl_list)

    glfw.swap_buffers(window) # draw the current frame
    clock.tick(60) # limit to 60 fps

if __name__ == '__main__':
    main()

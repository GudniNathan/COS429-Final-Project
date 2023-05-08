"""Reads a video along with ground-truth data and rasterizes the object in the video."""

import os
import shutil
import ffmpeg
import cv2
import numpy as np
import glfw
import sys
import math

from rasterize import init, draw
from settings import *

def euler_from_quaternion(x, y, z, w):
    """Convert a quaternion to euler angles."""
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = (math.atan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    Y = (math.asin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = (math.atan2(t3, t4))

    return X, Y, Z


def main():
    # clear the images folder
    try:
        shutil.rmtree(IMAGES_FOLDER)
    except:
        pass
    os.mkdir(IMAGES_FOLDER)


    # load the video frames into the images folder
    ( ffmpeg.input(VIDEO_FILE_PATH)
        # .filter('fps', fps='1/60')
        .output(f'{IMAGES_FOLDER}/image%d.png',
                start_number=0)
        .overwrite_output()
        .run()
    )
    video_resolution = ffmpeg.probe(VIDEO_FILE_PATH)['streams'][0]['width'], ffmpeg.probe(VIDEO_FILE_PATH)['streams'][0]['height']
    video_resolution = np.array(video_resolution)
    video_frame_count = int(ffmpeg.probe(VIDEO_FILE_PATH)['streams'][0]['nb_frames'])

    # Read the ground-truth data
    with open(GROUNDTRUTH_FILE_PATH, 'r') as f:
        lines = f.readlines()
        lines = [line.strip().split() for line in lines]
        lines = [[float(x) for x in line] for line in lines]
        lines = np.array(lines)
    
    # Initialize rasterizer module
    window, obj, clock, object_transform = init(CAMERA_FOCAL_LENGTH, CAMERA_PRINCIPAL_POINT, video_resolution)

    _, tx0, ty0, tz0, qx0, qy0, qz0, qw0 = lines[0]

    # Draw the first frame
    line_number = 0
    for frame_number in range(0, video_frame_count, SKIP_FRAMES):
        # Load the next frame of the video
        image = cv2.imread(f'{IMAGES_FOLDER}/image{frame_number}.png', cv2.IMREAD_GRAYSCALE)
        if image is None:
            break
    
        _, tx, ty, tz, qx, qy, qz, qw = lines[frame_number]
        # Convert the quaternion to euler angles
        rx, ry, rz = euler_from_quaternion(qx, qy, qz, qw)
        tx -= tx0
        ty -= ty0
        tz -= tz0

        scaling_factor = 30
        # calibrate the images
        object_transform.position = np.array([tx, -ty, -tz]) * scaling_factor

        print(object_transform.position)
        # object_transform.rotation = np.array([0., 0., 0.])
        object_transform.rotation = np.array([rx, rz, -ry])

        draw(object_transform, obj, window, clock, image)
        clock.tick(20)

if __name__ == "__main__":
    main()

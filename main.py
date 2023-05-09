# Author: Gudni Nathan Gunnarsson
# Date: 05.03.2023

# Standard library imports
import os
import shutil

# Third party imports
import ffmpeg
import cv2
import numpy as np

import glfw
from PIL import Image
from OpenGL.GL import *

# Local imports
from settings import *
from extrinsic_calibration import calibrate
import rasterize

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

    frame_number = SKIP_START
    # Load the first frame of the video
    image1 = cv2.imread(f'{IMAGES_FOLDER}/image{frame_number}.png', cv2.IMREAD_COLOR)
    
    total_Rotation = np.array(OBJECT_ROTATION)
    total_Translation = np.array(OBJECT_POSITION)[:, np.newaxis]

    # Initialize rasterizer module
    window, obj, clock, camera = rasterize.init(CAMERA_FOCAL_LENGTH, CAMERA_PRINCIPAL_POINT, video_resolution)
    camera.position = total_Translation
    camera.rotation = total_Rotation

    # Resize image to fit the framebuffer
    image1_resized = cv2.resize(image1, rasterize.buffer_size)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width, height = glfw.get_window_size(window)
    if not os.path.exists(os.path.dirname(OUTPUT_FILE_PATH)):
        os.mkdir(os.path.dirname(OUTPUT_FILE_PATH))
    out = cv2.VideoWriter(OUTPUT_FILE_PATH,fourcc, 20.0, (width,height))

    # Draw the first frame
    snapshot = rasterize.draw(camera, obj, window, clock, image1_resized)
    out.write(snapshot)

    timestamps = []
    with open(GROUNDTRUTH_FILE_PATH, "r") as truth_file:
        lines = truth_file.readlines()
        timestamps = [line.split()[0] for line in lines]

    pred = []
    points3D = np.array([])
    matches = np.array([])
    for i in range(SKIP_START + 1, video_frame_count, SKIP_FRAMES):
        frame_number = i
        rasterize.handle_events(window)

        # Load the next frame of the video
        image2 = cv2.imread(f'{IMAGES_FOLDER}/image{frame_number}.png', cv2.IMREAD_COLOR)
        if image2 is None:
            break

        # Resize image to fit the framebuffer
        image2_resized = cv2.resize(image2, rasterize.buffer_size)

        # calibrate the images
        R, t, points3D, matches = calibrate(
            image1, image2, 
            focal_length=CAMERA_FOCAL_LENGTH,
            principal_point=CAMERA_PRINCIPAL_POINT,
            last_frame_points3D=points3D,
            last_frame_matches=matches
        )

        # Combine the rotation and translation
        R = cv2.Rodrigues(R)[0]
        cv2.composeRT(total_Rotation, total_Translation, R, t, total_Rotation, total_Translation)

        # Update the position and rotation of the object
        camera.position = total_Translation
        camera.rotation = total_Rotation

        # Print the rotation and translation
        print(f"Rotation: {total_Rotation}")
        print(f"Translation: {total_Translation}")

        # Draw the object
        snapshot = rasterize.draw(camera, obj, window, clock, image2_resized)
        out.write(snapshot)
        # cv2.imwrite("test.jpg", snapshot)

        tx, ty, tz = (total_Translation[0][0], -total_Translation[2][0], -total_Translation[1][0])
        rot = rasterize.rotation_vector_to_matrix(total_Rotation)
        qx, qy, qz, qw = rasterize.matrix_to_quaternion(rot)
        timestamp = timestamps[frame_number] if frame_number < len(timestamps) else timestamps[-1]
        pred.append(f"{timestamp} {tx} {ty} {tz} {qx} {qy} {qz} {qw}\n")

        # Load the next frame of the video
        image1 = image2
        clock.tick(60)

    with open(PREDICTED_FILE_PATH, "w+") as pred_file:
        pred_file.writelines(pred)

    out.release()
    
    shutil.rmtree(IMAGES_FOLDER)


if __name__ == "__main__":
    main()
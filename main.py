# Author: Gudni Nathan Gunnarsson
# Date: 05.03.2023

# Standard library imports
import os
import shutil

# Third party imports
import ffmpeg
import cv2
import numpy as np

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
    image1 = cv2.imread(f'{IMAGES_FOLDER}/image{frame_number}.png', cv2.IMREAD_GRAYSCALE)
    
    total_Rotation = np.array(OBJECT_ROTATION)
    total_Translation = np.array(OBJECT_POSITION)[:, np.newaxis]

    # Initialize rasterizer module
    window, obj, clock, camera, framebuffer_size = rasterize.init(CAMERA_FOCAL_LENGTH, CAMERA_PRINCIPAL_POINT, video_resolution)
    camera.position = total_Translation
    camera.rotation = total_Rotation

    # Resize image to fit the framebuffer
    image1_resized = cv2.resize(image1, framebuffer_size)

    # Draw the first frame
    rasterize.draw(camera, obj, window, clock, image1_resized)

    for i in range(SKIP_START + 1, video_frame_count, SKIP_FRAMES):
        frame_number = i
        # Load the next frame of the video
        image2 = cv2.imread(f'{IMAGES_FOLDER}/image{frame_number}.png', cv2.IMREAD_GRAYSCALE)
        if image2 is None:
            break

        # Resize image to fit the framebuffer
        image2_resized = cv2.resize(image2, framebuffer_size)

        # calibrate the images
        R, t = calibrate(image1, image2, focal_length=CAMERA_FOCAL_LENGTH, principal_point=CAMERA_PRINCIPAL_POINT)


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
        rasterize.draw(camera, obj, window, clock, image2_resized)

        # Load the next frame of the video
        image1 = image2
    
    shutil.rmtree(IMAGES_FOLDER)


if __name__ == "__main__":
    main()
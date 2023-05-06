
# This file contains all the settings.
# Update this file to change the settings of the program.
VIDEO_FILE_PATH = "videos/minecraft_3.mp4"
OUTPUT_FILE_PATH = "output/minecraft_2.mp4"

IMAGES_FOLDER = "images"

# CAMERA_FOCAL_LENGTH = 525
# CAMERA_PRINCIPAL_POINT = (319.5, 239.5)

CAMERA_FOCAL_LENGTH = 200
CAMERA_PRINCIPAL_POINT = (426, 240)


# The number of frames to skip between each frame.
SKIP_FRAMES = 3

# The number of frames to skip at the beginning of the video.
SKIP_START = 3

# The position of the 3d object, relative to the camera at frame 0.
# Note that the camera is at (0, 0, 0) and is looking at (0, 0, -1).
OBJECT_POSITION = (0., 0., -5.)

# The rotation of the 3d object, relative to the camera at frame 0.
OBJECT_ROTATION = [0., 0., 0.]
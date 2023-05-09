
# This file contains all the settings.
# Update this file to change the settings of the program.
VIDEO_FILE_PATH = "videos/desk_1.mp4"
OUTPUT_FILE_PATH = "output/desk_1.mp4"
GROUNDTRUTH_FILE_PATH = "videos/desk_1_groundtruth_interpolated.txt"
PREDICTED_FILE_PATH = "videos/desk_1_predicted.txt"

IMAGES_FOLDER = "images"

CAMERA_FOCAL_LENGTH = 525
CAMERA_PRINCIPAL_POINT = (319.5, 239.5)

# CAMERA_FOCAL_LENGTH = 200
# CAMERA_PRINCIPAL_POINT = (928//2, 566//2)




# The number of frames to skip between each frame.
SKIP_FRAMES = 5

# The number of frames to skip at the beginning of the video.
SKIP_START = 5

# The position of the 3d object, relative to the camera at frame 0.
# Note that the camera is at (0, 0, 0) and is looking at (0, 0, -1).
# OBJECT_POSITION = (0., 0., -20.)
OBJECT_POSITION = (20., 20., 20.)

# The rotation of the 3d object, relative to the camera at frame 0.
OBJECT_ROTATION = [0., 0., 0.]
# OBJECT_ROTATION = [-2.2655618753458273, -0.05973019018791575, 0.981780539125668]

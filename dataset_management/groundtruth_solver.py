import numpy as np
# So the dataset we are using is somewhat annoying. The ground truth is not
# given per frame, but per second. So we need to interpolate the ground truth
# between the seconds. We do this by picking the nearest neighbor ground truth
# for each frame.
GROUNDTRUTH_FILE_PATH = "dataset_management/desk_1_groundtruth.txt"
FRAME_DATA_FILE_PATH = "dataset_management/desk_1_rgb.txt"

# Load the groundtruth file:
with open(GROUNDTRUTH_FILE_PATH, 'r') as f:
    lines = f.readlines()
    lines = [line.strip().split() for line in lines]
    lines = [[float(x) for x in line] for line in lines]
    # round to 6 decimal places
    lines = [[round(x, 6) for x in line] for line in lines]
    lines = np.array(lines)

# Load the frame data file:
with open(FRAME_DATA_FILE_PATH, 'r') as f:
    lines2 = f.readlines()
    lines2 = [line.strip().split() for line in lines2]
    lines2 = [float(line[0]) for line in lines2]
    lines2 = np.array(lines2)

# Interpolate the ground truth for each frame:
groundtruth = []
groundtruth_index = 0
for i in range(len(lines2)):
    while lines2[i] > lines[groundtruth_index][0]:
        groundtruth_index += 1
    groundtruth.append(lines[groundtruth_index])
groundtruth = np.array(groundtruth)

# Save the interpolated ground truth:
np.savetxt("desk_1_groundtruth_interpolated.txt", groundtruth)


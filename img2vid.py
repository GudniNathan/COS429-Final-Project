"""This script will convert a folder of images into a video."""
import os
import shutil
import ffmpeg

IMAGES_FOLDER = "images"
OUTPUT_FOLDER = "videos"

# Create the output folder if it doesn't exist
if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)

# Scan the folder for images, sort them by name
images = [img for img in os.listdir(IMAGES_FOLDER) if img.endswith(".png")]
images.sort()

# Rename images to this format: %05d.{png, jpg, ...}
patt = "%05d"
extension = images[0].split(".")[-1]
for i, img in enumerate(images):
    new_name = (f"{IMAGES_FOLDER}/"+ "{:" + patt[1:] + "}." + extension).format(i)
    os.rename(f"{IMAGES_FOLDER}/{img}", new_name)

# User input for the frame rate, file name
fps = int(input("Enter the frame rate: "))
file_name = input("Enter the file name: ")

# If file is missing extension, add .mp4
if "." not in file_name:
    file_name += ".mp4"

# Use ffmpeg to create the video
(
    ffmpeg.input(f"{IMAGES_FOLDER}/{patt}.png", framerate=fps, start_number=0)
    .output(f"{OUTPUT_FOLDER}/{file_name}")
    .overwrite_output()
    .run()
)

# Delete the images folder
shutil.rmtree(IMAGES_FOLDER)
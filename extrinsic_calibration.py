"""Extrinsic calibration module.
This module will contain functions that will be used to calibrate the 
extrinsic parameters of the camera (pose).
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt

def calibrate(image1, image2, focal_length=300.0, principal_point=(400.0, 300.0)):
    """Determine the position and orientation difference between two images.
    Args
        image1: The first image.
        image2: The second image.

    Returns
    -------
        The calibration matrix between the two images.

    """

    # Recipe:
    # 1. Find the keypoints and descriptors of image1.
    # 2. Find the keypoints and descriptors of image2.
    # 3. Match the descriptors of image1 and image2.
    # 4. Find the fundamental matrix from the matches.
    # That's it!

    # 1. Find the keypoints and descriptors of image1.
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(image1, None)

    # 2. Find the keypoints and descriptors of image2.
    kp2, des2 = sift.detectAndCompute(image2, None)

    # 3. Match the descriptors of image1 and image2.
    # bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # matches = bf.match(des1, des2)
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1,des2,k=2)

    # Apply ratio test
    good = []
    for m,n in matches:
        if m.distance < 0.75*n.distance:
            good.append([m])
    
    if len(good) < 4:
        return np.identity(3), np.zeros((3, 1))

    # 4. Find the fundamental matrix from the matches.
    # decompose the matches into their respective points
    points1 = np.float32([kp1[m[0].queryIdx].pt for m in good])
    points2 = np.float32([kp2[m[0].trainIdx].pt for m in good])
    
    # mat, mask = cv2.findFundamentalMat(points1, points2, cv2.FM_RANSAC)

    # intrinsic_matrix = np.array([[focal_length, 0, principal_point[0]],
    #                              [0, focal_length, principal_point[1]],
    #                              [0, 0, 1]])
    
    E = cv2.findEssentialMat(points1, points2, focal_length, principal_point, cv2.RANSAC, 0.999, 1.0)[0]

    retval, R, t, mask = cv2.recoverPose(E, points1, points2, focal=focal_length, pp=principal_point)

    # Triangulate points
    projMatr = np.hstack((np.identity(3), np.zeros((3, 1))))
    points4D = cv2.triangulatePoints(projMatr, projMatr, points1, points2)

    return R, t

def main():
    """Main function."""
    # load the images
    image1 = cv2.imread('images/image2.png', cv2.IMREAD_GRAYSCALE)
    image2 = cv2.imread('images/image1.png', cv2.IMREAD_GRAYSCALE)

    # calibrate the images
    R, t = calibrate(image1, image2)

    # print the calibration matrix
    print(R)
    print(t)

if __name__ == '__main__':
    main()
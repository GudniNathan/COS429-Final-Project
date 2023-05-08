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
    # Track:
    # 1. Find the keypoints and descriptors of image1.
    # 2. Find the keypoints and descriptors of image2.
    # 3. Match the descriptors of image1 and image2.
    # 4. Find the essential matrix from the matches.
    # 5. Recover pose from the essential matrix.
    # Trace:
    # 1. Do stereo calibration
    # 2. Stereo rectify the images
    # 3. Triangulate points
    # 4. Feature match 3d points
    # 5. solvePnP
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

    intrinsic_matrix = np.array([[focal_length, 0, principal_point[0]],
                                 [0, focal_length, principal_point[1]],
                                 [0, 0, 1]])
    
    E = cv2.findEssentialMat(points1, points2, focal_length, principal_point, cv2.RANSAC, 0.999, 1.0)[0]

    retval, R, t, mask = cv2.recoverPose(E, points1, points2, focal=focal_length, pp=principal_point)

    # Do stereo calibration
    # retval, intrinsic_matrix, distCoeffs, rvecs, tvecs = cv2.calibrateCamera([points1], [points2], image1.shape[::-1], None, None)


    # Stereo rectify the images
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(intrinsic_matrix, np.zeros((5, 1)), intrinsic_matrix, np.zeros((5, 1)), image1.shape[::-1], R, t, alpha=0.0)

    # Undistort the images
    # map1x, map1y = cv2.initUndistortRectifyMap(intrinsic_matrix, np.zeros((5, 1)), R1, P1, image1.shape[::-1], cv2.CV_32FC1)
    # map2x, map2y = cv2.initUndistortRectifyMap(intrinsic_matrix, np.zeros((5, 1)), R2, P2, image1.shape[::-1], cv2.CV_32FC1)

    # image1 = cv2.remap(image1, map1x, map1y, cv2.INTER_LINEAR)
    # image2 = cv2.remap(image2, map2x, map2y, cv2.INTER_LINEAR)

    # plt.imshow(image1)
    # plt.show()
    # plt.imshow(image2)
    # plt.show()

    # Find the disparity
    stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
    disparity = stereo.compute(image1, image2)

    # plt.imshow(disparity)
    # plt.show()

    # Find the depth
    depth = cv2.reprojectImageTo3D(disparity, Q)


    # Find the rotation and translation



    # Triangulate points
    projMatr = np.hstack((np.identity(3), np.zeros((3, 1))))
    # points4D = cv2.triangulatePoints(projMatr, projMatr, points1, points2)

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
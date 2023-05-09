"""Extrinsic calibration module.
This module will contain functions that will be used to calibrate the 
extrinsic parameters of the camera (pose).
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt

last_magnitude = 0.1
def calibrate(image1, image2, focal_length=300.0, principal_point=(400.0, 300.0), last_frame_points3D=np.zeros(0), last_frame_matches=np.zeros(0)):
    """Determine the position and orientation difference between two images.
    Args
        image1: The first image.
        image2: The second image.
        last_frame_points3D: the 3D points triangulated from the last pair of images

    Returns
    -------
        The rotation and translation between the two images.
    """
    global last_magnitude
    image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    # Flip the images
    image1 = cv2.flip(image1, 0)
    image2 = cv2.flip(image2, 0)

    # 1. Find the keypoints and descriptors of image1.
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(image1, None)

    # 2. Find the keypoints and descriptors of image2.
    kp2, des2 = sift.detectAndCompute(image2, None)

    # 3. Match the descriptors of image1 and image2.
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
    
    intrinsic_matrix = np.array([[focal_length, 0, principal_point[0]],
                                 [0, focal_length, principal_point[1]],
                                 [0, 0, 1]])
    
    E = cv2.findEssentialMat(points1, points2, focal_length, principal_point, cv2.RANSAC, 0.999, 1.0)[0]

    retval, R, t, mask = cv2.recoverPose(E, points1, points2, focal=focal_length, pp=principal_point)

    return R, t, last_frame_points3D, good

    # Stereo rectify the images
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(intrinsic_matrix, np.zeros((5, 1)), intrinsic_matrix, np.zeros((5, 1)), image1.shape[::-1], R, t, alpha=0.0)


    # Find the rotation and translation

    # Triangulate points in 3D
    proj1 = np.hstack((np.eye(3), np.zeros((3, 1))))
    proj2 = np.hstack((R, t))
    points4D = cv2.triangulatePoints(proj1, proj2, points1.T, points2.T)
    points3D = points4D[:3,:] / points4D[3,:]
    points3D = points3D.T
    original_3D_points = points3D

    if last_frame_points3D.size == 0:
        last_frame_points3D = points3D
        last_frame_matches = good
        points0 = points1
    else:
        points0 = np.float32([kp1[m[0].trainIdx].pt for m in last_frame_matches])

    # Get the intersection of points0 and points1
    intersection = points0[np.isin(points0, points1).all(axis=1)]
    intersection2 = points1[np.isin(points1, points0).all(axis=1)]

    # Remove duplicate points
    intersection = np.unique(intersection, axis=0, return_index=True)[1]
    intersection2 = np.unique(intersection2, axis=0, return_index=True)[1]


    assert len(intersection) == len(intersection2)
    

    # Get the corresponding 3d points from the last frame
    last_frame_points3D = last_frame_points3D[intersection]
    points3D = points3D[intersection2]
    # Find the keypoints that were matched in both the last frame and this frame
    # points0 = points0[np.isin(points0, points1).all(axis=1)]

    

    # use estimateAffine3D for feature matching 3d
    retval, affine_transform, inliers = cv2.estimateAffine3D(last_frame_points3D, points3D)

    # If there are no or few inliers, then just return the rotation and translation or something
    if np.sum(inliers) <= 6 or retval == 0:
        return R, t, original_3D_points, good

    # Get all the inliers, multiply them by the affine transform, and then use them to find the rotation and translation
    points3D = points3D[inliers[:, 0] == 1]
    rotatation = affine_transform[:, :3]
    translation = affine_transform[:, 3] 
    points3D = points3D.dot(rotatation.T) + translation

    
    # 5. solvePnP
    # retval, rvec, tvec = cv2.solvePnP(points3D, points2[intersection2][inliers[:, 0] == 1], intrinsic_matrix, np.zeros((5, 1)))


    return R, t, original_3D_points, good

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
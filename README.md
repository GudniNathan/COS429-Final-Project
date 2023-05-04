# COS429-Final-Project
 
To install requirements, please run:
```conda env create -f environment.yml```

Then activate the new environment:
```conda activate COS429-Final-Project```

If you need to update the environment, run:
```conda env update --file environment.yml --prune```

## Attribution
"Rubberduckie" model by aerojockey via opengameart.
https://opengameart.org/content/rubber-duckie


extract SIFT keypoints
match
find essential matrix
extract pose

stereoRectify
extract depth from stereo image
feature matching (find 3d points)
Perspective-n-Point, to find camera pose

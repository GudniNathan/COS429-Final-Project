# COS429-Final-Project
Authors: Guðni Nathan Gunnarsson, Rishi Mago, & Fairuz Ishraque.

This codebase implements simple AR for videos using visual odometry. Please see our report for more details.

Before using this application, please configure settings.py to use your video of choice, and set any other variables.
 
To install requirements, please run:
```conda env create -f environment.yml```

Then activate the new environment:
```conda activate COS429-Final-Project```

If you need to update the environment, run:
```conda env update --file environment.yml --prune```

To run the application use:
```python main.py```
You can also visualize the ground truth data directly:
```python groundtruth.py```

## Attribution
"Rubberduckie" model by aerojockey via opengameart.
https://opengameart.org/content/rubber-duckie


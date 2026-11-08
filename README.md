# Automatic Georeferencing System Using Local Feature-Based Image Matching

Here a system was designed to identify corresponding features between a reference image and UAV aerial images, estimate a homography transformation, and use the transformation to project selected aerial-image locations onto the reference image. The projected image coordinates are then used to estimate the corresponding geographic latitude and longitude. An interactive graphical user interface was developed using Python and Tkinter to allow users to load images, select locations, perform feature matching, estimate homography, and visualize projected geographic coordinates.

## Objectives

The project involves the following tasks:

1. Load a reference image and UAV payload camera images.
2. Develop a graphical interface for viewing the reference and aerial images.
3. Allow users to select any pixel or target in an aerial image and record its pixel coordinates.
4. Extract keypoints and descriptors from the reference and selected aerial images.
5. Implement different feature detection and descriptor methods.
6. Estimate the homography matrix using RANSAC.
7. Project selected aerial-image pixel coordinates onto the reference image.
8. Estimate latitude and longitude through interpolation of the projected reference-image coordinates.
9. Display the projected location and geographic coordinates.
10. Allow users to load different aerial images and select arbitrary pixels interactively.

## Methodology

The implementation follows a feature-based image matching pipeline:

1. Reference and aerial image acquisition.
2. Image preprocessing and resizing.
3. Keypoint detection and descriptor extraction.
4. Feature descriptor matching.
5. Homography estimation using RANSAC.
6. Pixel coordinate transformation.
7. Geographic coordinate estimation.
8. Projected location visualization.

## Implemented Feature Detection Methods

The application provides three selectable methods:

- **SIFT:** Scale-Invariant Feature Transform.
- **ORB:** Oriented FAST and Rotated BRIEF.
- **Harris:** Harris Corner Detection, with nearest-keypoint matching for correspondence estimation.
<img width="1424" height="732" alt="image" src="https://github.com/user-attachments/assets/8d119811-1406-4d4a-858c-de04b1a33b86" />

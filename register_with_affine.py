#Script requires fixed and moving landmarks as .csv files
#requires path to moving image, and output path for saving

import numpy as np
import pandas as pd
import os
from skimage import transform
from skimage import io
import tifffile

#reading coordinates
def read_points(filename):
    df = pd.read_csv(filename)
    points = df[['axis-1', 'axis-0']].values
    return points

fixed_points = read_points("path/to/fixed_landmarks.csv")
moving_points = read_points("path/to/moving_landmarks.csv")

#calculating the affine transformation
def calculate_affine_transform(fixed_points, moving_points, results_file_path):
    fixed_points = np.array(fixed_points)
    moving_points = np.array(moving_points)

    tform = transform.AffineTransform()
    tform.estimate(moving_points, fixed_points)

    affine_matrix = tform.params

    #calculate residual error
    transformed_points = tform(moving_points)
    residuals = np.sqrt(np.sum((transformed_points - fixed_points)**2, axis=1))
    mean_error = np.mean(residuals)
    max_error = np.max(residuals)

    print(f"Mean registration error: {mean_error:.2f} pixels")
    print(f"Max registration error: {max_error:.2f} pixels")
    print(f"\nAffine transformation matrix:")
    print(affine_matrix)
    # Save results to file
    with open(results_file_path, "w") as f:
        f.write(f"Mean registration error: {mean_error:.2f} pixels\n")
        f.write(f"Max registration error: {max_error:.2f} pixels\n")
    
    print(f"\nResults saved to: {results_file_path}")
    return affine_matrix

affine_matrix = calculate_affine_transform(fixed_points, moving_points, results_file_path = "path/to/save/registration_results.txt")


#applying the affine transformation
def apply_affine_registration(input_path, affine_matrix, output_path):
    moving_image = tifffile.imread(input_path)
    
    # Create transform object from your matrix
    tform = transform.AffineTransform(matrix=affine_matrix)
    
    # Apply transformation
    registered_image = transform.warp(
        moving_image,
        tform.inverse,  # warp uses inverse mapping
        output_shape=moving_image.shape,
        preserve_range=True
    ).astype(moving_image.dtype)
    
    tifffile.imwrite(output_path, registered_image, photometric='minisblack')
    return registered_image


input = "path/to/image.ome.tif"
output_path = "path/to/registered_image.ome.tif"

#Final usage
affine_matrix = calculate_affine_transform(fixed_points, moving_points, results_file_path = "path/to/save/registration_results.txt")
apply_affine_registration(input, affine_matrix, output_path)
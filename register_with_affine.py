#Script requires fixed and moving landmarks as .csv files
#requires path to moving image, and output path for saving

import numpy as np
import pandas as pd
from skimage import transform
from skimage import io
import tifffile

#reading coordinates
def read_points(filename):
    df = pd.read_csv(filename)
    points = df[['axis-1', 'axis-0']].values
    return points

fixed_points = read_points("D:/Dom/Fibrosis project/4th year data/xen_pheno_registration/systematising landmarks/Landmark csvs/50gt_xen_roi1.csv")
moving_points = read_points("D:/Dom/Fibrosis project/4th year data/xen_pheno_registration/systematising landmarks/Landmark csvs/50gt_pheno_roi1.csv")

#calculating the affine transformation
def calculate_affine_transform(fixed_points, moving_points):
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
    
    return affine_matrix

affine_matrix = calculate_affine_transform(fixed_points, moving_points)


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


input = "C:/Users/dbuxton/Desktop/reg_virtual_stack_test/input/pheno_C12.ome.tif"
output_path ="C:/Users/dbuxton/Desktop/reg_virtual_stack_test/input/pheno_C12_R.ome.tif"

#Final usage
apply_affine_registration(input, affine_matrix, output_path)
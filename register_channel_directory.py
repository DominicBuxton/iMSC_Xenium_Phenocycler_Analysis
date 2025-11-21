#This script uses a premade landmarks file to register a channel from an image in which one channel has been manually registered
#It will output a spatialdata object containing all the channels you added, with an aligned coordinate system.

##paths for testing
#fixed_sd_path = "D:/Dom/Fibrosis Project/4th year data - update location/xen_pheno_registration/xen_dapi_sd.zarr"
#moving_directory_path = "D:/Dom/Fibrosis project/4th year data - update location/pheno_xen_fullres_images/testfolder"
#fixed_landmarks_path = "D:/Dom/Fibrosis Project/4th year data - update location/xen_pheno_registration/xen_landmarks.csv"
#moving_landmarks_path = "D:/Dom/Fibrosis Project/4th year data - update location/xen_pheno_registration/pheno_landmarks.csv"

import spatialdata
import sopa
import napari
from os import listdir
from pathlib import Path
import pandas as pd
import numpy as np
from spatialdata.models import PointsModel
from spatialdata.transformations import Identity

print("Requirements: spatialdata object to register to; channel_image.ome.tif files in a single folder; one landmarks.csv file for both images (you only need 2  regardless of the no. of channels you are aligning)")
print("Enter path to spatialdata object you wish to register your channel image to")
fixed_sd_path = input()

print("Enter path to folder containing the images you would like to register")
moving_directory_path = input()


print("Enter paths to landmarks for fixed image")
fixed_landmarks_path = input()
print("Enter path to moving image landmarks")
moving_landmarks_path = input()

print("Paths added")
print("Fixed image path:", fixed_sd_path)
print("channel paths", moving_directory_path)
print("Landmark paths", [fixed_landmarks_path, moving_landmarks_path])



##read in fixed_sd, create points layers from landmarks, add points layer to fixed_sd

#reading the fixed spatial object
fixed_sd = spatialdata.read_zarr(fixed_sd_path)

#doing the generic landmark preparation (so it doesn't have to run for every for loop)
# Read your CSV file
fixed_landmarks_df = pd.read_csv(fixed_landmarks_path)
moving_landmarks_df = pd.read_csv(moving_landmarks_path)

# Extract coordinates (axis-1 = y, axis-2 = x)
# SpatialData expects coordinates in (y, x) order for 2D points
fixed_coords = fixed_landmarks_df[['axis-2', 'axis-1']].values
moving_coords = moving_landmarks_df[['axis-2', 'axis-1']].values

# Create a DataFrame in the format expected by PointsModel
# PointsModel expects columns: ['x', 'y'] or ['z', 'y', 'x'] for 3D
fixed_points_df = pd.DataFrame({
    'y': fixed_landmarks_df['axis-1'].values,
    'x': fixed_landmarks_df['axis-2'].values
})

moving_points_df = pd.DataFrame({
    'y': moving_landmarks_df['axis-1'].values,
    'x': moving_landmarks_df['axis-2'].values
})

# Create the points element with transformation to global coordinate system
fixed_points_element = PointsModel.parse(
    fixed_points_df,
    transformations={"global": Identity()}
)

moving_points_element = PointsModel.parse(
    moving_points_df,
    transformations={"global": Identity()}
)
#add fixed points layer to fixed sd
fixed_sd.points['fixed_landmarks'] = fixed_points_element

#save location input
#save path = D:/Dom/Fibrosis project/4th year data - update location/pheno_xen_fullres_images/testsavepath
print("Enter path where you would like to save your objects")
save_path = input()



##register each channel as a separate object one at a time

#making a dictionary of channel names and images
channel_paths = dict()
for channel in listdir(moving_directory_path):
    #get name and path as a dictionary
    name = Path(channel).stem
    full_path = moving_directory_path + "/" + channel
    channel_paths[name] = full_path


#registering and saving each file
for name, path in channel_paths.items():
    #read image as a spatialdata object
    moving_sd = sopa.io.ome_tif(path, as_image = False)

    # Add points layers to SpatialData objects
    moving_sd.points['moving_landmarks'] = moving_points_element 

    #getting and adding affine transformations
    from spatialdata.transformations import (
        align_elements_using_landmarks,
        get_transformation_between_landmarks,
    )

    fixed_image_name = list(fixed_sd.images.keys())[1] # note this assumes that the main image of the fixed SD is the 2nd in alphabetical order...I realise this ain't great
    moving_image_name = list(moving_sd.images.keys())[0]


    affine = align_elements_using_landmarks(
        references_coords=fixed_sd["fixed_landmarks"], 
        moving_coords=moving_sd["moving_landmarks"],
        reference_element=fixed_sd[fixed_image_name], #needs to be named correctly
        moving_element=moving_sd[moving_image_name], 
        reference_coordinate_system="global",
        moving_coordinate_system="global",
        new_coordinate_system="aligned",
    )
    print("aligned channel")

    save_sd_path = save_path + "/" + name + ".zarr"
    moving_sd.write(save_sd_path, overwrite = True)
    moving_sd.write_transformations
    print("channel", list(channel_paths.keys()).index(name), "saved with transformations to", save_sd_path)


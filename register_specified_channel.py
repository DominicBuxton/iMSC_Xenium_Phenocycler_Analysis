#This script uses a premade landmarks file to register a channel from an image in which one channel has been manually registered
#It will output a spatialdata object containing all the channels you added, with an aligned coordinate system.

##paths for testing
#fixed_sd_path = "D:/Dom/Fibrosis Project/4th year data - update location/xen_pheno_registration/xen_dapi_sd.zarr"
#channel_paths = {"C1": "D:/Dom/Fibrosis project/4th year data - update location/pheno_xen_fullres_images/pheno_C1.ome.tif",
#                   "C2": "D:/Dom/Fibrosis project/4th year data - update location/pheno_xen_fullres_images/pheno_C1.ome.tif"}
#fixed_landmarks_path = "D:/Dom/Fibrosis Project/4th year data - update location/xen_pheno_registration/xen_landmarks.csv"
#moving_landmarks_path = "D:/Dom/Fibrosis Project/4th year data - update location/xen_pheno_registration/pheno_landmarks.csv"

import spatialdata
import sopa
import napari


print("Requirements: spatialdata object to register to; channel_image.ome.tif files; one landmarks.csv file for both images (you only need 2  regardless of the no. of channels you are aligning)")
print("Enter path to spatialdata object you wish to register your channel image to")
fixed_sd_path = input()

channel_paths = dict()
def add_cpath():
    print("Enter channel name or done")
    key = input()
    if key == 'done':
        print("Channel paths added")
    else:
        print("Enter path")
        cpath = input()
        channel_paths[key] = cpath
        add_cpath()

print("enter path(s) to channels, one at a time. Type 'done' when finished")
add_cpath()

print("Enter paths to landmarks for fixed image")
fixed_landmarks_path = input()
print("Enter path to moving image landmarks")
moving_landmarks_path = input()

print("Paths added")
print("Fixed image path:", fixed_sd_path)
print("channel paths", channel_paths)
print("Landmark paths", [fixed_landmarks_path, moving_landmarks_path])

#making a dictionary of channel names and images
#first read images in as spatialdata objects
moving_sds = dict()
for name, path in channel_paths.items():
    sd = sopa.io.ome_tif(path, as_image = False)
    moving_sds[name] = sd

#then take the image data from these objects and 
moving_images = dict()
for name, sd in moving_sds.items():
    imagename = list(sd.images.keys())[0]
    
    moving_images[name] = sd.images[imagename]
del moving_sds #save RAM by not having a bunch of sds in memory

#making a spatialdata object with all your channel images
from spatialdata import SpatialData

moving_sd = SpatialData(images = moving_images) 

#reading the fixed spatial object
fixed_sd = spatialdata.read_zarr(fixed_sd_path)

##alignment using landmarks files

#adding the landmarks to the spatial objects
import pandas as pd
import numpy as np
from spatialdata.models import PointsModel
from spatialdata.transformations import Identity

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

# Add points layers to SpatialData objects
fixed_sd.points['fixed_landmarks'] = fixed_points_element
moving_sd.points['moving_landmarks'] = moving_points_element 

#getting and adding affine transformations
from spatialdata.transformations import (
    align_elements_using_landmarks,
    get_transformation_between_landmarks,
)

#affine = get_transformation_between_landmarks(
#    references_coords=fixed_sd[name], moving_coords=moving_sd[name]
#)
fixed_image_name = list(fixed_sd.images.keys())[1] # note this assumes that the main image of the fixed SD is the 2nd in alphabetical order...I realise this ain't great
moving_image_name = list(moving_sd.images.keys())[0]


affine = align_elements_using_landmarks(
    references_coords=fixed_sd["fixed_landmarks"], 
    moving_coords=moving_sd["moving_landmarks"],
    reference_element=fixed_sd[fixed_image_name], #needs to be named correctly
    moving_element=moving_sd[moving_image_name], #needs correct name, only needs first channel
    reference_coordinate_system="global",
    moving_coordinate_system="global",
    new_coordinate_system="aligned",
)


#add the rest of the channels to the moving_sd aligned system
for name, image in moving_sd.images.items():
    if name == moving_image_name:
        continue
    else:
        aligned_moving_sd = moving_sd.transform_element_to_coordinate_system(name, 'aligned', maintain_positioning = False) #transform the new image to the aligned coordinate system
        moving_sd.images[name] = aligned_moving_sd #add the aligned image to fixed_sd

#napari viewer option
from napari_spatialdata import Interactive
Interactive([fixed_sd, moving_sd]).run()

#save option
def save_option():
    print("Would you like to save these aligned channels as a spatialobject? Alignments will be lost if you do not save")
    print("If yes, enter the desired absolute save path, with .zarr at the end")
    print("If no, enter 'no'\n -----------------------------------------")
    input3 = input()
    if input3 !='no':
        moving_sd.write(input3)
        moving_sd.write_transformations
        
    else:
        print("Object not saved...")
save_option()





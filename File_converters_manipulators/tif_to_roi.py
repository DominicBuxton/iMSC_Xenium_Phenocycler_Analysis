"""
Script for the conversion of a segmentation.tif file, where each cell is a unique grayscale value, to an imageJ.ROI.zip folder, containing the boundaries of each cell. 
Requires: folder with Segmentation masks. 
Outputs: roi.zip files with the same name and location as the input files. 
"""

from pathlib import Path
import numpy as np
from tifffile import imread
from roifile import ImagejRoi, roiwrite
from skimage.measure import find_contours

seg_path = Path("/path/to/folder/with/segmentationMasks")
seg_list = list(seg_path.glob("*.tif"))

for image_path in seg_list:
    label_img = imread(image_path)
    labels = np.unique(label_img)
    labels = labels[labels != 0]

    rois = []

    for label_id in labels:
        mask = label_img == label_id

        contours = find_contours(mask.astype(float), level=0.5)
        if not contours:
            continue

        # pick largest contour
        contour = max(contours, key=lambda x: x.shape[0])

        # convert (row, col) → (x, y)
        contour_xy = np.fliplr(contour)

        roi = ImagejRoi.frompoints(contour_xy)
        roi.name = f"cell_{label_id}"
        rois.append(roi)

    output_path = image_path.with_suffix(".zip")
    roiwrite(output_path, rois)

    print(f"Saved {len(rois)} ROIs → {output_path}")
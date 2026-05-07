"""
geojson_to_roi.py
-----------------
Convert a GeoJSON file to an ImageJ .roi file.

Dependencies:
    pip install roifile numpy
"""

import json
from pathlib import Path

import numpy as np
from roifile import ImagejRoi


# ── Configuration 

INPUT_PATH  = Path("/path/to/GeoJson/File.geojson") #path to .geojson file
OUTPUT_PATH = INPUT_PATH.with_suffix(".roi")  #output path, by default same folder as .geojson input. 


# ── Conversion 
def GeoJson_to_ImgJ_ROI(INPUT_PATH):
    INPUT_PATH = Path(INPUT_PATH)
    OUTPUT_PATH = INPUT_PATH.with_suffix(".roi")
    with open(INPUT_PATH) as f:
        gj = json.load(f)

    # Unwrap FeatureCollection → Feature
    gtype = gj.get("type")
    if gtype == "FeatureCollection":
        features = gj.get("features", [])
        if len(features) > 1:
            print(f"Warning: {len(features)} features found; using the first one.")
        feature = features[0]
    elif gtype == "Feature":
        feature = gj
    elif gtype == "Polygon":
        feature = {"id": INPUT_PATH.stem, "geometry": gj, "properties": {}}
    else:
        raise ValueError(f"Unsupported GeoJSON type: '{gtype}'")

    # Extract outer ring (holes are ignored)
    geom = feature["geometry"]
    ring = geom["coordinates"][0]
    pts  = ring[:-1] if ring[0] == ring[-1] else ring   # drop closing duplicate

    def _extract_xy(p):
        # Unwrap any extra nesting until we reach a coordinate pair
        while isinstance(p[0], (list, tuple, np.ndarray)):
            p = p[0]
        return p[0], p[1]

    points = np.array([_extract_xy(p) for p in pts], dtype=np.float32)

    # ROI name: prefer Feature.id, then properties.name/label, then filename stem
    props = feature.get("properties") or {}
    name  = (feature.get("id")
            or props.get("name")
            or props.get("label")
            or INPUT_PATH.stem)

    # Build and save the ROI - looping over a folder with multiple GeoJsons

    roi = ImagejRoi.frompoints(points, name=str(name))
    roi.tofile(OUTPUT_PATH)

    print(f"Saved: {OUTPUT_PATH}")
    print(f"  ROI name : {name}")
    print(f"  Points   : {len(points)}")
    print(f"  Bounds   : x=[{points[:,0].min():.2f}, {points[:,0].max():.2f}]"
        f"  y=[{points[:,1].min():.2f}, {points[:,1].max():.2f}]")


##USAGE ACROSS A FOLDER WITH GEOJSONS
folder = Path("/path/to/folder")

converted_files = []
failed_files = []

for file in folder.glob('*.geojson'):
    print(f"Converting {file} to .roi")
    try: 
        GeoJson_to_ImgJ_ROI(INPUT_PATH = file)
        converted_files.append(Path(file).name)
    except:
        print(f"Not able to convert {file}")
        failed_files.append(Path(file).name)

print(f"Successfully printed {len(converted_files)} files")
for file in converted_files:
    print(file)

if len(failed_files) > 0:
    print("!Files failed to convert!")
    for file in failed_files:
        print(file)

#USAGE FOR A SINGLE FILE   
#GeoJson_to_ImgJ_ROI("/path/to/geojson")
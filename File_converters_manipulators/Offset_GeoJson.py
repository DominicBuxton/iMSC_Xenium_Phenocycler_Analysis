"""
Offset_GeoJson.py
Reassigns coordinates of a geojson shape based on locations of crop. 
For example, change location of a shape mapped to a whole slide image to a crop containing just the section of interest.

Requires: Geojson to move, (x,y) offset of the crop, width and height of the crop
-----------------------------
"""

import json
import sys
from copy import deepcopy
from pathlib import Path
import pandas as pd


# ---------------------------------------------------------------------------
# CONFIG — EDIT THESE VALUES
# ---------------------------------------------------------------------------

INPUT_PATH  = "whole_slide_annotations.geojson"
OUTPUT_PATH = "cropped_annotations.geojson"

X_OFFSET = 3000
Y_OFFSET = 10000
WIDTH    = 2048
HEIGHT   = 2048


# ---------------------------------------------------------------------------
# Coordinate transformation
# ---------------------------------------------------------------------------

try:
    import numpy as np
except ImportError:
    np = None


def json_default(obj):
    if np is not None:
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

def translate_ring(ring, x_offset, y_offset):
    return [[pt[0] - x_offset, pt[1] - y_offset] + pt[2:] for pt in ring]


def translate_polygon(coordinates, x_offset, y_offset):
    return [translate_ring(ring, x_offset, y_offset) for ring in coordinates]


def translate_geometry(geometry, x_offset, y_offset):
    if geometry is None:
        return None

    geom = deepcopy(geometry)
    gtype = geom["type"]

    if gtype == "Polygon":
        geom["coordinates"] = translate_polygon(geom["coordinates"], x_offset, y_offset)
    elif gtype == "MultiPolygon":
        geom["coordinates"] = [
            translate_polygon(poly, x_offset, y_offset)
            for poly in geom["coordinates"]
        ]
    elif gtype == "Point":
        pt = geom["coordinates"]
        geom["coordinates"] = [pt[0] - x_offset, pt[1] - y_offset] + pt[2:]
    elif gtype == "MultiPoint":
        geom["coordinates"] = [
            [pt[0] - x_offset, pt[1] - y_offset] + pt[2:]
            for pt in geom["coordinates"]
        ]
    elif gtype == "LineString":
        geom["coordinates"] = translate_ring(geom["coordinates"], x_offset, y_offset)
    elif gtype == "MultiLineString":
        geom["coordinates"] = [
            translate_ring(line, x_offset, y_offset)
            for line in geom["coordinates"]
        ]
    else:
        print(f"Warning: unsupported geometry type '{gtype}' — left unchanged.",
              file=sys.stderr)

    return geom


# ---------------------------------------------------------------------------
# Bounding-box overlap check
# ---------------------------------------------------------------------------

def ring_bbox(ring):
    xs = [pt[0] for pt in ring]
    ys = [pt[1] for pt in ring]
    return min(xs), min(ys), max(xs), max(ys)


def geometry_bbox(geometry):
    gtype = geometry["type"]

    if gtype == "Polygon":
        return ring_bbox(geometry["coordinates"][0])
    elif gtype == "MultiPolygon":
        bboxes = [ring_bbox(poly[0]) for poly in geometry["coordinates"]]
    elif gtype == "Point":
        pt = geometry["coordinates"]
        return pt[0], pt[1], pt[0], pt[1]
    elif gtype == "MultiPoint":
        bboxes = [(pt[0], pt[1], pt[0], pt[1]) for pt in geometry["coordinates"]]
    elif gtype == "LineString":
        return ring_bbox(geometry["coordinates"])
    elif gtype == "MultiLineString":
        bboxes = [ring_bbox(line) for line in geometry["coordinates"]]
    else:
        return None

    return (
        min(b[0] for b in bboxes),
        min(b[1] for b in bboxes),
        max(b[2] for b in bboxes),
        max(b[3] for b in bboxes),
    )


def overlaps_crop(geometry, x_offset, y_offset, width, height):
    bbox = geometry_bbox(geometry)
    if bbox is None:
        return True

    min_x, min_y, max_x, max_y = bbox
    return not (
        max_x < x_offset or min_x > x_offset + width or
        max_y < y_offset or min_y > y_offset + height
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def reproject(input_path, output_path, x_offset, y_offset, width, height):
    with open(input_path, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    if geojson.get("type") != "FeatureCollection":
        sys.exit("Error: input GeoJSON must be a FeatureCollection.")

    features_in = geojson.get("features", [])
    features_out = []
    dropped = 0

    for feature in features_in:
        geometry = feature.get("geometry")

        if geometry is None:
            features_out.append(deepcopy(feature))
            continue

        if not overlaps_crop(geometry, x_offset, y_offset, width, height):
            dropped += 1
            continue

        new_feature = deepcopy(feature)
        new_feature["geometry"] = translate_geometry(geometry, x_offset, y_offset)
        features_out.append(new_feature)

    output = {
        "type": "FeatureCollection",
        "features": features_out,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=json_default)

    kept = len(features_out)
    print(f"Done. {kept} feature(s) kept, {dropped} dropped (outside crop).")
    print(f"Output written to: {output_path}")

#USAGE FOR ONE FILE
"""reproject(
    input_path=INPUT_PATH,
    output_path=OUTPUT_PATH,
    x_offset=X_OFFSET,
    y_offset=Y_OFFSET,
    width=WIDTH,
    height=HEIGHT,
)"""


#USAGE FOR A WHOLE SECTION

section = 'M3'
#defining files to convert
paths = [Path(fr"D:\Dom\Psoriasis project\4th year data\Second Round Data\Xenium outputs - second round\output-XETG00160__0093234__ctrl__20260211__140710\Compartment segmentations\Dorsal dermis {section}.geojson"),
         Path(fr"D:\Dom\Psoriasis project\4th year data\Second Round Data\Xenium outputs - second round\output-XETG00160__0093234__ctrl__20260211__140710\Compartment segmentations\Ventral dermis {section}.geojson"),
         Path(fr"D:\Dom\Psoriasis project\4th year data\Second Round Data\Xenium outputs - second round\output-XETG00160__0093234__ctrl__20260211__140710\Compartment segmentations\Dorsal epidermis {section}.geojson"),
         Path(fr"D:\Dom\Psoriasis project\4th year data\Second Round Data\Xenium outputs - second round\output-XETG00160__0093234__ctrl__20260211__140710\Compartment segmentations\Ventral epidermis {section}.geojson"),
         Path(fr"D:\Dom\Psoriasis project\4th year data\Second Round Data\Xenium outputs - second round\output-XETG00160__0093234__ctrl__20260211__140710\Compartment segmentations\Cartilage {section}.geojson"),
    ]

#reading the crop dimensions 
df = pd.read_csv(r"D:\Dom\Psoriasis project\4th year data\Second Round Data\Xenium outputs - second round\output-XETG00160__0093234__ctrl__20260211__140710\FMCtrl_BBox_values.csv")

section_num = 5 #0-indexed! 

X_OFFSET = df['BX'][section_num]
Y_OFFSET = df['BY'][section_num]
WIDTH = df['Width'][section_num]
HEIGHT = df['Height'][section_num]

for file in paths:
    new_file_name = f'cropped_{file.name}'
    OUTPUT_PATH = file.parent.parent.joinpath('Compartment segmentations - Cropped').joinpath(new_file_name)

    reproject(
        input_path = file,
        output_path = OUTPUT_PATH,
        x_offset=X_OFFSET,
        y_offset=Y_OFFSET,
        width=WIDTH,
        height=HEIGHT,
    )

"""
ImgJ_ROI_to_GeoJSON.py
----------------------
Convert an ImageJ .roi file (or a .zip of multiple .roi files) to a GeoJSON
file compatible with QuPath.
 
Output format matches QuPath's own GeoJSON export:
  - FeatureCollection of Features
  - MultiPolygon geometry  (coordinates: [[[[x, y], ...]]])
  - Integer pixel coordinates
  - properties: {"objectType": "annotation", "name": <roi name>}
 
Geometry is validated and repaired via Shapely before export, which prevents
QuPath's JTS "Reduction failed / invalid input" error caused by
self-intersections or duplicate points in the original ROI.
 
Dependencies:
    pip install roifile numpy shapely
"""
 
import json
import uuid
import zipfile
from pathlib import Path
 
import numpy as np
from roifile import ImagejRoi
from shapely.geometry import mapping
from shapely.geometry import Polygon as ShapelyPolygon
 
 
# ── Configuration ─────────────────────────────────────────────────────────────
 
INPUT_PATH  = Path("/path/to/ImageJ/File.roi")   # .roi or .zip of .roi files
OUTPUT_PATH = INPUT_PATH.with_suffix(".geojson")  # same folder by default
 
 
# ── Helpers ───────────────────────────────────────────────────────────────────
 
def _roi_to_shapely(roi: ImagejRoi) -> ShapelyPolygon:
    """
    Read an ROI's coordinates and return a valid Shapely Polygon.
 
    Steps:
      1. Extract integer pixel coordinates from the ROI (channel info is ignored).
      2. Remove consecutive duplicate points (common artefact in traced ROIs).
      3. Build a Shapely Polygon and call .buffer(0) to fix any
         self-intersections — the same JTS engine QuPath uses internally,
         so anything that passes here will pass QuPath's importer.
    """
    xy = roi.coordinates()          # ndarray (N, 2): [[x, y], ...]
    if xy is None or len(xy) == 0:
        raise ValueError(f"ROI '{roi.name}' has no coordinate data.")
 
    pts = xy.astype(int).tolist()
 
    # Remove consecutive duplicates (keeps first occurrence of each run)
    deduped = [pts[0]]
    for p in pts[1:]:
        if p != deduped[-1]:
            deduped.append(p)
    # Also remove closing duplicate if present before we hand to Shapely
    if len(deduped) > 1 and deduped[0] == deduped[-1]:
        deduped = deduped[:-1]
 
    if len(deduped) < 3:
        raise ValueError(f"ROI '{roi.name}' has fewer than 3 unique points after deduplication.")
 
    poly = ShapelyPolygon(deduped)
 
    if not poly.is_valid:
        poly = poly.buffer(0)       # standard JTS fix for self-intersections
 
    if poly.is_empty:
        raise ValueError(f"ROI '{roi.name}' produced an empty geometry after repair.")
 
    return poly
 
 
def _shapely_to_feature(poly: ShapelyPolygon, name: str) -> dict:
    """
    Convert a Shapely Polygon (or MultiPolygon after buffer(0)) to a
    QuPath-compatible GeoJSON Feature with integer coordinates.
 
    QuPath expects MultiPolygon regardless of whether there is one or
    several polygons, so we always wrap in that type.
    """
    geom = mapping(poly)            # GeoJSON-like dict from Shapely
    gtype = geom["type"]
 
    def _int_coords(coords):
        """Recursively convert all coordinates to plain Python ints."""
        if isinstance(coords[0], (list, tuple)):
            return [_int_coords(c) for c in coords]
        return [int(coords[0]), int(coords[1])]
 
    if gtype == "Polygon":
        # Wrap single polygon into MultiPolygon format: [[ring, ...]]
        mp_coords = [[_int_coords(ring) for ring in geom["coordinates"]]]
    elif gtype == "MultiPolygon":
        mp_coords = [
            [_int_coords(ring) for ring in polygon]
            for polygon in geom["coordinates"]
        ]
    else:
        raise ValueError(f"Unexpected Shapely geometry type after repair: {gtype}")
 
    geometry = {
        "type":        "MultiPolygon",
        "coordinates": mp_coords,
    }
 
    properties = {
        "objectType": "annotation",
        "name":       name,
    }
 
    return {
        "type":       "Feature",
        "id":         str(uuid.uuid4()),
        "geometry":   geometry,
        "properties": properties,
    }
 
 
# ── Core conversion ───────────────────────────────────────────────────────────
 
def ImgJ_ROI_to_GeoJSON(input_path, output_path=None) -> Path:
    """
    Convert a single .roi file or a .zip bundle of .roi files to a
    QuPath-compatible GeoJSON FeatureCollection.
 
    Returns the Path of the written .geojson file.
    """
    input_path  = Path(input_path)
    output_path = Path(output_path) if output_path else input_path.with_suffix(".geojson")
 
    suffix = input_path.suffix.lower()
 
    # ── Read ROI(s) ───────────────────────────────────────────────────────────
    if suffix == ".roi":
        rois = [ImagejRoi.fromfile(input_path)]
    elif suffix == ".zip":
        rois = []
        with zipfile.ZipFile(input_path) as zf:
            roi_names = [n for n in zf.namelist() if n.lower().endswith(".roi")]
            if not roi_names:
                raise ValueError(f"No .roi entries found inside '{input_path}'.")
            for name in roi_names:
                with zf.open(name) as fh:
                    rois.append(ImagejRoi.frombytes(fh.read()))
    else:
        raise ValueError(f"Unsupported file type: '{suffix}'. Expected .roi or .zip.")
 
    # ── Build GeoJSON ─────────────────────────────────────────────────────────
    features = []
    skipped  = []
 
    for roi in rois:
        try:
            poly    = _roi_to_shapely(roi)
            feature = _shapely_to_feature(poly, name=roi.name)
            features.append(feature)
 
            # Diagnostic output
            ring = feature["geometry"]["coordinates"][0][0]
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            validity = "valid" if poly.is_valid else "repaired"
            print(f"  [{roi.name}]  {validity}  points={len(ring) - 1}"
                  f"  x=[{min(xs)}, {max(xs)}]  y=[{min(ys)}, {max(ys)}]")
 
        except Exception as exc:
            print(f"  Warning: skipping ROI '{roi.name}': {exc}")
            skipped.append(roi.name)
 
    if not features:
        raise RuntimeError("No ROIs could be converted (all were skipped).")
 
    geojson = {
        "type":     "FeatureCollection",
        "features": features,
    }
 
    output_path.write_text(json.dumps(geojson, indent=2), encoding="utf-8")
 
    print(f"\nSaved : {output_path}")
    print(f"  Features : {len(features)}")
    if skipped:
        print(f"  Skipped  : {len(skipped)} — {skipped}")
 
    return output_path
 
 
# ── Batch conversion ──────────────────────────────────────────────────────────
 
def convert_folder(folder, pattern="*.roi"):
    """
    Convert every .roi (or .zip) file in *folder* to GeoJSON.
    Call twice with different patterns if you need both .roi and .zip.
    """
    folder = Path(folder)
    converted_files = []
    failed_files    = []
 
    for file in folder.glob(pattern):
        print(f"\nConverting {file.name} …")
        try:
            ImgJ_ROI_to_GeoJSON(input_path=file)
            converted_files.append(file.name)
        except Exception as exc:
            print(f"  ERROR: {exc}")
            failed_files.append(file.name)
 
    print(f"\nSuccessfully converted {len(converted_files)} file(s):")
    for f in converted_files:
        print(f"  {f}")
 
    if failed_files:
        print(f"\n! {len(failed_files)} file(s) failed to convert:")
        for f in failed_files:
            print(f"  {f}")
 


# ── Single file ───────────────────────────────────────────────────────────
# ImgJ_ROI_to_GeoJSON("/path/to/file.roi")
# ImgJ_ROI_to_GeoJSON("/path/to/bundle.zip")          # zip of .roi files

# ── Whole folder ─────────────────────────────────────────────────────────
# convert_folder("/path/to/folder", pattern="*.roi")
# convert_folder("/path/to/folder", pattern="*.zip")

# ── Default: run on INPUT_PATH defined at the top ─────────────────────────
#ImgJ_ROI_to_GeoJSON(INPUT_PATH, OUTPUT_PATH)


#usage for my files, ignore
from pathlib import Path
parent_dir = Path(r"D:\Dom\Psoriasis project\4th year data\Second Round Data\Registered Images - second round")
EnFace_dirs = parent_dir.glob("*_EnFace*") 

for dir in EnFace_dirs:
    convert_folder(dir, pattern="*.roi")
    print(f'saved dermis for {dir.name}')
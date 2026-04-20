from __future__ import annotations

import numpy as np
import pandas as pd
import tifffile as tif
from skimage.draw import polygon


# =========================
# Set these values manually
# =========================
PARQUET_PATH = r"D:\Dom\Psoriasis project\4th year data\Second Round Data\Xenium outputs - second round\output-XETG00160__0093234__D10imq__20260211__140710\cell_boundaries.parquet"
OUTPUT_TIF = r"D:\Dom\Psoriasis project\4th year data\cellpose training\Crops_Round2\Final Choices\masks\Xenium_masks\D10-2_cell_labels_xen.tif"

# ROI origin in pixels, measured from the top-left corner of the full image
X_OFFSET_PX = 37930
Y_OFFSET_PX = 14066

# Xenium pixel size
PIXEL_SIZE_UM = 0.2125

# Output window size in pixels
ROI_SIZE = 750


def rasterize_cell_boundaries_to_mask(
    df: pd.DataFrame,
    x_offset_px: int,
    y_offset_px: int,
    roi_size: int,
    pixel_size_um: float,
) -> np.ndarray:
    """
    Convert cell boundary polygons to a label mask for one ROI.

    Assumptions:
    - vertex_x and vertex_y are in micrometers
    - x_offset_px and y_offset_px are pixel coordinates from the top-left of the full image
    - rows belonging to the same cell_id are already in boundary order
    """
    required_cols = {"cell_id", "vertex_x", "vertex_y", "label_id"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    mask = np.zeros((roi_size, roi_size), dtype=np.uint32)

    # ROI bounds in full-image pixel coordinates
    x0 = x_offset_px
    y0 = y_offset_px
    x1 = x0 + roi_size
    y1 = y0 + roi_size

    # Convert all coordinates from micrometers to full-image pixel coordinates
    df = df.copy()
    df["x_px"] = df["vertex_x"] / pixel_size_um
    df["y_px"] = df["vertex_y"] / pixel_size_um

    # Group by cell and draw each polygon into the ROI mask
    for cell_id, g in df.groupby("cell_id", sort=False):
        label_id = int(g["label_id"].iloc[0])
        if label_id == 0:
            continue

        # Polygon vertices in ROI-local pixel coordinates
        x = g["x_px"].to_numpy() - x0
        y = g["y_px"].to_numpy() - y0

        # Quick bbox rejection
        if x.max() < 0 or x.min() >= roi_size or y.max() < 0 or y.min() >= roi_size:
            continue

        # Rasterize polygon into ROI
        rr, cc = polygon(y, x, shape=mask.shape)
        mask[rr, cc] = label_id

    return mask


# =========================
# Run extraction
# =========================
df = pd.read_parquet(PARQUET_PATH)

roi_mask = rasterize_cell_boundaries_to_mask(
    df=df,
    x_offset_px=X_OFFSET_PX,
    y_offset_px=Y_OFFSET_PX,
    roi_size=ROI_SIZE,
    pixel_size_um=PIXEL_SIZE_UM,
)

tif.imwrite(OUTPUT_TIF, roi_mask)

print(f"Saved {OUTPUT_TIF}")
print(f"Mask shape: {roi_mask.shape}")
print(f"Mask dtype: {roi_mask.dtype}")
import tifffile
import zarr
import numpy as np
import pandas as pd
from pathlib import Path
from skimage.transform import resize

# ── Config ────────────────────────────────────────────────────────────────────

IMG_PATH = r"D:\Dom\JB00313_RBLA_msSkin_Xen1_R1_28-05-26\Scan1\JB00313_RBLA_msSkin_Xen1_R1_28-05-26_Scan1.er.qptiff"
COORDS_CSV = r"D:\Dom\Psoriasis project\4th year data\Second Round Data\Registered Images - second round\crop_coords_pheno_unregistered.xlsx"
RESULTS_DIR = Path(r"D:\Dom\Psoriasis project\4th year data\Second Round Data\Registered Images - second round")

SKIP_SECTIONS = {'Ctrl_F1', 'Ctrl_F2', 'Ctrl_F3', 'Ctrl_M1', 'Ctrl_M2', 'Ctrl_M3'}

# ── Load coords ───────────────────────────────────────────────────────────────

coords_df = pd.read_excel(COORDS_CSV, header=2, usecols=range(5))
coords_df.columns = ['section', 'x', 'y', 'width', 'height']

# ── Open qptiff lazily ────────────────────────────────────────────────────────

store = tifffile.imread(IMG_PATH, aszarr=True)
z = zarr.open(store, mode='r')
img_array = z['0']  # full resolution: (39, 46800, 23040) uint16
print(f"Image shape: {img_array.shape}, dtype: {img_array.dtype}")

# ── Process each section ──────────────────────────────────────────────────────

for _, row in coords_df.iterrows():
    try:
        section = str(row['section'])

        if section in SKIP_SECTIONS:
            print(f"Skipping {section}")
            continue

        x, y, w, h = int(row['x']), int(row['y']), int(row['width']), int(row['height'])
        print(f"Processing {section}: x={x}, y={y}, w={w}, h={h}")

        # ── Crop ──────────────────────────────────────────────────────────────────
        crop = np.array(img_array[:, y:y+h, x:x+w])   # materialise just this region
        print(f"  crop shape: {crop.shape}  (expected C,{h},{w})")

        # ── Rotate 180° (no mirror) ───────────────────────────────────────────────
        crop = np.rot90(crop, k=2, axes=(1, 2))

        # ── Get target dimensions from dapi.tif ───────────────────────────────────
        dapi_path = RESULTS_DIR / section / "dapi.tif"
        with tifffile.TiffFile(str(dapi_path)) as dapi_tif:
            dapi_page = dapi_tif.pages[0]
            target_h = dapi_page.shape[0]
            target_w = dapi_page.shape[1]

        # ── Rescale to match dapi.tif dimensions if needed ────────────────────────
    # ── Rescale to match dapi.tif dimensions if needed ────────────────────────
        if (crop.shape[1], crop.shape[2]) != (target_h, target_w):

            if crop.shape[1] == 0 or crop.shape[2] == 0:
                raise ValueError(
                    f"{section}: cropped region is empty (shape={crop.shape}). "
                    f"Check that x={x}, y={y}, w={w}, h={h} are within "
                    f"image bounds {img_array.shape[1:]} (H, W)."
                )

            if target_h == 0 or target_w == 0:
                raise ValueError(
                    f"{section}: target dimensions from dapi.tif are zero "
                    f"(target_h={target_h}, target_w={target_w})."
                )

            resized_channels = []
            for c in range(crop.shape[0]):
                ch_resized = resize(
                    crop[c],
                    (target_h, target_w),
                    order=1,               # bilinear
                    preserve_range=True,
                    anti_aliasing=True
                )
                ch_resized = np.clip(np.round(ch_resized), 0, 65535).astype(img_array.dtype)
                resized_channels.append(ch_resized)
            crop = np.stack(resized_channels, axis=0)

        # ── Save ──────────────────────────────────────────────────────────────────
        out_path = RESULTS_DIR / section / "pheno_channels.tiff"
        out_path.parent.mkdir(parents=True, exist_ok=True)

        tifffile.imwrite(
            str(out_path),
            crop,                          # (C, H, W) uint16
            imagej=True,
            photometric='minisblack',
            metadata={'axes': 'CYX'}
        )
        print(f"  ✓ Saved → {out_path}  shape={crop.shape}")

    except ValueError as e:
        print(f'Failed: {e}')

store.close()
print("Done.")
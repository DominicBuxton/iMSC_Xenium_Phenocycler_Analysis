import os
import numpy as np
import tifffile as tif

def create_xen_all(folder):
    """
    For a given folder, creates a three-channel image containing:
      Ch1: DAPI
      Ch2: ATP_Cadherin_CD45
      Ch3: Cytoplasm stains (18s_RNA + AlphaSMA_Vimentin, clipped to dtype max)
      default_save_path is 'folder/Path/xen_all.ome.tif'
    """
    dapi = tif.imread(os.path.join(folder, 'dapi.tif'))
    RNA  = tif.imread(os.path.join(folder, '18s_RNA.tif'))
    AV   = tif.imread(os.path.join(folder, 'AlphaSMA_Vimentin.tif'))
    ACC  = tif.imread(os.path.join(folder, 'ATP_Cadherin_CD45.tif'))

    # Add cytoplasmic stains, clipping at the dtype maximum to avoid overflow
    cyto = np.clip(RNA.astype(np.uint32) + AV.astype(np.uint32),
                   0, np.iinfo(RNA.dtype).max).astype(RNA.dtype)

    # Stack into (3, y, x) 
    multichannel = np.stack([dapi, ACC, cyto], axis=0)

    save_path = os.path.join(folder, "xen_all.tiff")

    tif.imwrite(
        save_path,
        multichannel,
        imagej=True,          # writes ImageJ-compatible metadata
        metadata={'axes': 'CYX'}
    )

parent_folder = path/to/files
for folder in os.listdir(parent_folder):
    folder_path = os.path.join(parent_folder, folder)
    create_xen_all(folder_path)


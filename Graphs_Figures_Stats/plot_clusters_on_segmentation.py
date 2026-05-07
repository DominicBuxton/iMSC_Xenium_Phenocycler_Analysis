"""
Colour segmentation.tif file by cell type assignment
"""

import anndata
import pandas as pd
import numpy as np
import tifffile
import colorsys
from PIL import Image, ImageDraw, ImageFont

def generate_distinct_cluster_colours_rgb(df, cluster_col="cluster"):
    """Returns a dict mapping cluster -> (R, G, B) tuple directly."""
    clusters = df[cluster_col].unique()
    n = len(clusters)
    
    cluster_rgb = {}
    for i, cluster in enumerate(clusters):
        hue = i / n
        r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
        cluster_rgb[cluster] = (int(r * 255), int(g * 255), int(b * 255))
    
    return cluster_rgb

def colour_segmentation(seg_paths, df, cluster_col="cluster", cell_id_col="cell_id", region_col="unique_region", background_colour=(0, 0, 0)):
    """
    seg_paths        : list of paths to segmentation .tif files
    df               : DataFrame with cell ID, cluster, and region columns
    cluster_col      : name of the cluster column
    cell_id_col      : name of the cell ID column
    region_col       : name of the column defining image origin (0-indexed integers)
    background_colour: RGB tuple for background (cell ID == 0)
    """
    cluster_rgb = generate_distinct_cluster_colours_rgb(df, cluster_col)
    rgb_images = []

    for region_idx, seg_path in enumerate(seg_paths):
        seg = tifffile.imread(seg_path)
        region_df = df[df[region_col] == region_idx]

        # Build LUT
        max_id = int(seg.max())
        lut = np.zeros((max_id + 1, 3), dtype=np.uint8)
        lut[0] = background_colour

        for _, row in region_df.iterrows():
            cell_id = int(row[cell_id_col])
            if cell_id <= max_id:
                lut[cell_id] = cluster_rgb[row[cluster_col]]

        rgb_images.append(lut[seg])

    return rgb_images


def save_cluster_legend(cluster_rgb, output_path, title="Cluster Key"):
    """
    Saves a legend image mapping cluster labels to their colours.
    
    cluster_rgb : dict mapping cluster -> (R, G, B) tuple
    output_path : path to save the legend .png
    title       : title displayed at the top of the legend
    """
    # Layout constants
    swatch_size = 40
    padding = 10
    font_size = 28
    title_height = 50
    row_height = swatch_size + padding
    img_width = 300
    img_height = title_height + (row_height * len(cluster_rgb)) + padding

    img = Image.new("RGB", (img_width, img_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Try to use a nicer font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
        title_font = ImageFont.truetype("arial.ttf", font_size + 4)
    except:
        font = ImageFont.load_default()
        title_font = font

    # Draw title
    draw.text((padding, padding), title, fill=(0, 0, 0), font=title_font)

    # Draw each cluster row
    for i, (cluster, rgb) in enumerate(sorted(cluster_rgb.items(), key=lambda x: str(x[0]))):
        y = title_height + i * row_height

        # Colour swatch
        draw.rectangle(
            [padding, y, padding + swatch_size, y + swatch_size],
            fill=rgb
        )

        # Cluster label
        draw.text(
            (padding + swatch_size + padding, y + swatch_size // 4),
            f"Cluster {cluster}",
            fill=(0, 0, 0),
            font=font
        )

    img.save(output_path)
    print(f"Legend saved to: {output_path}")

def highlight_clusters(seg_paths, df, highlight, cluster_col="cluster", cell_id_col="cell_id", region_col="unique_region", background_colour=(0, 0, 0), grey=(100, 100, 100)):
    """
    seg_paths     : list of paths to segmentation .tif files
    df            : DataFrame with cell ID, cluster, and region columns
    highlight     : list of cluster labels to highlight
    cluster_col   : name of the cluster column
    cell_id_col   : name of the cell ID column
    region_col    : name of the column defining image origin (0-indexed integers)
    background_colour : RGB tuple for background (cell ID == 0)
    grey          : RGB tuple for non-highlighted cells
    """
    cluster_rgb = generate_distinct_cluster_colours_rgb(df, cluster_col)
    rgb_images = []

    for region_idx, seg_path in enumerate(seg_paths):
        seg = tifffile.imread(seg_path)
        region_df = df[df[region_col] == region_idx]

        max_id = int(seg.max())
        lut = np.zeros((max_id + 1, 3), dtype=np.uint8)
        lut[0] = background_colour

        for _, row in region_df.iterrows():
            cell_id = int(row[cell_id_col])
            if cell_id <= max_id:
                if row[cluster_col] in highlight:
                    lut[cell_id] = cluster_rgb[row[cluster_col]]
                else:
                    lut[cell_id] = grey

        rgb_images.append(lut[seg])

    print(f'Highlighted Cluster{highlight}')

    return rgb_images

# --- Run it ---

#creation of df
adata = anndata.read_h5ad(r"D:\Dom\SpaceC test\outputs\Added_WT_M\doubleZ_clusters_minMark.h5ad")
data = {"cell_id":adata.obs['CellID'].astype(int), 'cluster': adata.obs['leiden_0.24'], 'unique_region':adata.obs['unique_region'].astype(int)}
df = pd.DataFrame(data)

seg_paths = [
    r"D:\Dom\Psoriasis project\4th year data\CellTune\CellTune_Data\Images\Background Subtract\registered images - Background Subtract 25\R2r1\segmentation_labels.tiff",
    r"D:\Dom\Psoriasis project\4th year data\CellTune\CellTune_Data\Images\Background Subtract\registered images - Background Subtract 25\R3r1\segmentation_labels.tiff",
    r"D:\Dom\Psoriasis project\4th year data\CellTune\CellTune_Data\Images\Background Subtract\registered images - Background Subtract 25\R3r2\segmentation_labels.tiff",
    r"D:\Dom\Psoriasis project\4th year data\CellTune\CellTune_Data\Images\Background Subtract\registered images - Background Subtract 25\R4r1\segmentation_labels.tiff",
    r"D:\Dom\Psoriasis project\4th year data\CellTune\CellTune_Data\Images\Background Subtract\registered images - Background Subtract 25\R4r2\segmentation_labels.tiff",
    r"D:\Dom\Psoriasis project\4th year data\CellTune\CellTune_Data\Images\Background Subtract\registered images - Background Subtract 25\R5r1\segmentation_labels.tiff",
    r"D:\Dom\Psoriasis project\4th year data\CellTune\CellTune_Data\Images\Background Subtract\registered images - Background Subtract 25\R5r2\segmentation_labels.tiff",
    r"D:\Dom\Psoriasis project\4th year data\CellTune\CellTune_Data\Images\Background Subtract\registered images - Background Subtract 25\R6r1\segmentation_labels.tiff",
    r"D:\Dom\Psoriasis project\4th year data\CellTune\CellTune_Data\Images\Background Subtract\registered images - Background Subtract 25\R6r2\segmentation_labels.tiff",
    r"D:\Dom\Psoriasis project\4th year data\CellTune\CellTune_Data\Images\Background Subtract\registered images - Background Subtract 25\R7r2\segmentation_labels.tiff",
    r"D:\Dom\Psoriasis project\4th year data\CellTune\CellTune_Data\Images\Background Subtract\registered images - Background Subtract 25\R8r2\segmentation_labels.tiff",
]

#rgb_images = colour_segmentation(seg_paths, df)
rgb_images = highlight_clusters(seg_paths, df, highlight = ['13'])


# Save as PNG
replacement_key = [
    # old_name: new_name
    'WT_F',
    'D3_F',
    'D3_M',
    'D7_F',
    'D7_M',
    'D10_F',
    'D10_M',
    'D7_F2',
    'D7_M2',
    'D7_M3',
    'WT_M'
]
output_dir = "D:\\Dom\\SpaceC test\\outputs\\Added_WT_M\\Coloured_segmentation\\cluster13"
for image, name in zip(rgb_images, replacement_key): 
    Image.fromarray(image).save(f"{output_dir}/{name}_cluster.png")

#saving the cluster key
#cluster_rgb = generate_distinct_cluster_colours_rgb(df)
#save_cluster_legend(cluster_rgb, f"{output_dir}\\cluster_legend.png")
#shebang thing
#double check paths

import spatialdata as sd
from spatialdata_io import xenium
from pathlib import Path

xeniums_folders = Path("/users/kir-hallou/pnq824/archive/dom_pheno_xen/xenium_reseg")
samples_list = ['D3IMQ', 'D7IMQ', 'D10IMQ', 'EF1_Ctrl', 'EF1_D10', 'EF2_Ctrl', 'EF2_D10']

#debug portion - removing cell artefacts from import segmentation algorithm
import pandas as pd
from pathlib import Path 

for dir in samples_list:
    boundaries_file = xeniums_folders / (dir + '_reseg')/'Outs' /"nucleus_boundaries.parquet" #change from cells to nucleus 
    df = pd.read_parquet(boundaries_file)
    print(f'{dir} shape is {df.shape}')

    vertex_counts = df.groupby('cell_id').size()
    valid_cells = vertex_counts[vertex_counts >=4].index #remove any cells that have fewer than 4 vertices, they cause an error with the spatialdata reader
    df_clean = df[df['cell_id'].isin(valid_cells)]
    print(f'cleaned shape is {df_clean.shape}, removed : {df.shape[0]-df_clean.shape[0]}')

    df_clean.to_parquet(boundaries_file)

for dir in samples_list:
    boundaries_file = xeniums_folders / (dir + '_reseg')/'Outs' /"cell_boundaries.parquet" #change from cells to nucleus 
    df = pd.read_parquet(boundaries_file)
    print(f'{dir} shape is {df.shape}')

    vertex_counts = df.groupby('cell_id').size()
    valid_cells = vertex_counts[vertex_counts >=4].index #remove any cells that have fewer than 4 vertices, they cause an error with the spatialdata reader
    df_clean = df[df['cell_id'].isin(valid_cells)]
    print(f'cleaned shape is {df_clean.shape}, removed : {df.shape[0]-df_clean.shape[0]}')

    df_clean.to_parquet(boundaries_file)
#============================================END OF DEBUG==========================================================================



for dir in samples_list: 
        xenium_path = xeniums_folders / (dir + '_reseg') / 'outs'
        sdata = xenium(xenium_path,
                cells_boundaries = True,
                cells_table = True,
                nucleus_labels = True,
                cells_labels = True,
                nucleus_boundaries = True            
                ) 

        zarr_path = xeniums_folders/"xenium_sdata_zarrs" /(dir + ".zarr")
        sdata.write(zarr_path)

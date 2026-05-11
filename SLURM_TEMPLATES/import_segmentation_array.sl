#!/bin/bash -e

#SBATCH --job-name      xeniumranger_import_segmentation
#SBATCH --nodes         1
#SBATCH --array         0-7
#SBATCH --ntasks        1
#SBATCH --cpus-per-task 2
#SBATCH --mem           8G
#SBATCH --time          04:00:00
#SBATCH --partition     short
#SBATCH --output        slurmlogs/xeniumranger_%A_%a.out



module load XeniumRanger/4.0.0 

WORKDIR="/users/kir-hallou/pnq824/archive/dom_pheno_xen"  # set this

#Condition names --> label the xenium bundle and the segmentation files for each job
CONDITIONS=(Ctrl D3IMQ D7IMQ D10IMQ EF1_Ctrl EF2_Ctrl EF1_D10 EF2_D10)

CONDITION=${CONDITIONS[$SLURM_ARRAY_TASK_ID]}

xeniumranger import-segmentation \
    --id="${CONDITION}_reseg" \
    --xenium-bundle="${WORKDIR}/original_Xenium_outputs/${CONDITION}" \
    --nuclei="${WORKDIR}/cellpose_xen_segmentations/${CONDITION}_nuclear_labels.tif" \
    --cells="${WORKDIR}/cellpose_xen_segmentations/${CONDITION}_cell_labels.tif" \
    --jobmode="/gpfs3/well/kir-hallou/projects/archive/10x_template/slurm.template" \
    --mempercore=8 \
    --maxjobs=50 \
    --jobinterval=10000 \
    --disable-ui true
#!/bin/bash -e

#SBATCH --job-name      xeniumranger_ctrl
#SBATCH --nodes         1
#SBATCH --ntasks        1
#SBATCH --cpus-per-task 2
#SBATCH --mem           8G
#SBATCH --time          04:00:00
#SBATCH --partition     short
#SBATCH -output         slurmlogs/xeniumranger_%j.out

mkdir -p logs

module load XeniumRanger/4.0.0 

WORKDIR="/users/kir-hallou/pnq824/archive/dom_pheno_xen"  # set this

xeniumranger import-segmentation \
    --id=Ctrl \
    --xenium-bundle="${WORKDIR}/output-XETG00160__0093234__ctrl__20260211__140710" \
    --nuclei="${WORKDIR}/cellpose_xen_segmentations/Ctrl_nuclear_labels.tif" \
    --cells="${WORKDIR}/cellpose_xen_segmentations/Ctrl_cell_labels.tif" \
    --jobmode="/gpfs3/well/kir-hallou/projects/archive/10x_template/slurm.template" \
    --mempercore=8 \
    --maxjobs=50 \
    --jobinterval=10000 \
    --disable-ui true
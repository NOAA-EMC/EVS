#!/bin/ksh
#*************************************************************************************************
# Purpose:  Run NAEFS  prep job
#             1. Retrieve bias-corrected GEFS and CMCE member files 
#                to form smaller grib2 files
#             2. Stored the smaller grib files in prep/global_ens/atmos.YYYYMMDD/gefs_bc, 
#                and prep/global_ens/atmos.YYYYMMDD/cmce_bc
#
# Last updated 11/15/2023: by  Binbin Zhou, Lynker@EMC/NCEP
#************************************************************************************************
set -x

export WORK=$DATA

cd $WORK

export get_gefs_bc_apcp24h=${get_gefs_bc_apcp24h:-'yes'}
export get_model_bc=${get_model_bc:-'yes'}

export vday=$INITDATE

export run_mpi=${run_mpi:-'yes'}
export CLIMO=$FIXevs/climos/atmos
export MASKS=$FIXevs/mask

export gefs_mbrs=30

#get ensemble member data by sequentially (non-mpi) or mpi run
$USHevs/global_ens/evs_naefs_atmos_prep.sh
export err=$?; err_chk

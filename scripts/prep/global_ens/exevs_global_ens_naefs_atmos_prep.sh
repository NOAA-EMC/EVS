#!/bin/ksh
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

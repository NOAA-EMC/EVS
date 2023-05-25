#!/bin/ksh
set -x

export WORK=$DATA

cd $WORK

export MET_bin_exec='bin'
export log_met_output_to_metplus=''
export metplus_verbosity=2
export met_verbosity=2

export get_gefs_bc_apcp24h=${get_gefs_bc_apcp24h:-'yes'}
export get_model_bc=${get_model_bc:-'yes'}

export vday=$INITDATE

export run_mpi=${run_mpi:-'yes'}
export CLIMO=$FIXevs/climos/atmos
export MASKS=$FIXevs/mask

export COMOUT_gefs_bc=${COMOUT}.${INITDATE}/gefs_bc
export COMOUT_cmce_bc=${COMOUT}.${INITDATE}/cmce_bc
mkdir -p $COMOUT_gefs_bc
mkdir -p $COMOUT_cmce_bc

#get ensemble member data by sequentail(non-mpi) or mpi run
$USHevs/global_ens/evs_naefs_atmos_prep.sh

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0

#!/bin/ksh
set -x

export WORK=$DATA

cd $WORK

export MET_bin_exec='bin'
export log_met_output_to_metplus=''
export metplus_verbosity=2
export met_verbosity=2

export vday=$INITDATE

export run_mpi=${run_mpi:-'yes'}

export COMIN_gefs=${COMIN}/${STEP}/${COMPONENT}/atmos.${INITDATE}/gefs
export COMIN_cmce=${COMIN}/${STEP}/${COMPONENT}/atmos.${INITDATE}/cmce


export COMOUT_gefs=${COMIN}/${STEP}/${COMPONENT}/headline.${INITDATE}/gefs
export COMOUT_cmce=${COMIN}/${STEP}/${COMPONENT}/headline.${INITDATE}/cmce

mkdir -p $COMOUT_gefs $COMOUT_cmce

#get ensemble member data by sequentail(non-mpi) or mpi run
$USHevs/${COMPONENT}/evs_get_gens_headline_data.sh


msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0

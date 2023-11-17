#!/bin/ksh
set -x

export WORK=$DATA

cd $WORK

export vday=$INITDATE

export run_mpi=${run_mpi:-'yes'}

export gefs_number=30

#get ensemble member data sequentially (non-mpi) or mpi run
$USHevs/${COMPONENT}/evs_get_gens_headline_data.sh
export err=$?; err_chk

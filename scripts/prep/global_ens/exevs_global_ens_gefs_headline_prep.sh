#!/bin/ksh
set -x

export WORK=$DATA

cd $WORK

export vday=$INITDATE

export run_mpi=${run_mpi:-'yes'}






#get ensemble member data by sequentail(non-mpi) or mpi run
$USHevs/${COMPONENT}/evs_get_gens_headline_data.sh

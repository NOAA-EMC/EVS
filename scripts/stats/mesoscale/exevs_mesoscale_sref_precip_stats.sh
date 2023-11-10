#!/bin/ksh
#################################################################
# Purpose:   Setup some paths and run sref precip stat ush scripts
#
# Last updated 10/27/2023: by  Binbin Zhou, Lynker@EMC/NCEP
##################################################################
#
set -x

export WORK=$DATA
cd $WORK

export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}

export PRECIP_CONF=$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS

$USHevs/mesoscale/evs_sref_precip.sh 
export err=$?; err_chk



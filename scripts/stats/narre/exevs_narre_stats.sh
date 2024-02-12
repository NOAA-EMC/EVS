#!/bin/ksh
#################################################################
# Purpose:   Setup some paths and run narre stat ush scripts
#
# Last updated 10/27/2023: by  Binbin Zhou, Lynker@EMC/NCEP  
################################################################
set -x

export WORK=$DATA
cd $WORK

export run_mpi=${run_mpi:-'yes'}
export stats=${stats:-'yes'}
export gather=${gather:-'yes'}

export GRID2OBS_CONF=$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS

#********************************************************
## Check input forecsat and validation data availability
## ******************************************************
$USHevs/narre/check_files_existing.sh
export err=$?; err_chk

if [ $stats = yes ] ; then
 $USHevs/narre/evs_narre_stats.sh  
 export err=$?; err_chk
fi



#!/bin/ksh
#################################################################
# Purpose:   Setup some paths and run sref precip stat ush scripts
#
# Last updated 10/27/2023: by  Binbin Zhou, Lynker@EMC/NCEP
##################################################################
#
set -x
export machine=${machine:-"WCOSS2"} 
export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH
export WORK=$DATA
cd $WORK

export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}

export PRECIP_CONF=$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS

#********************************************
# Check the input data files availability
# ******************************************
$USHevs/mesoscale/evs_check_sref_files.sh
export err=$?; err_chk

if [ -e $DATA/ccpa.missing ] || [ -e $DATA/sref_mbrs.missing ] ; then
 echo "EXIT: Either ccpa or sref members are missing! Terminate $jobid!"
 exit
else 
  $USHevs/mesoscale/evs_sref_precip.sh 
  export err=$?; err_chk
fi


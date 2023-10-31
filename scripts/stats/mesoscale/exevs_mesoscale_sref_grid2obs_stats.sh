#!/bin/ksh
#################################################################
# Purpose:   Setup some paths and run sref grid2obs stat ush scripts
#
# Last updated 10/27/2023: by  Binbin Zhou, Lynker@EMC/NCEP
#################################################################
#
set -x

export WORK=$DATA
cd $WORK

export MET_bin_exec='bin'

export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}
export just_cnv=${just_cnv:-'no'} 

export GRID2OBS_CONF=$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS


msg="$job HAS BEGUN"
postmsg "$msg"

#******************************************************************************
# The method in ceiling and vis (cnv) job is to deal with the conditional mean
#  (1) First average hits, false alarms, etc in the categoery table
#      over all times to get averaged CTC
#  (2) Then use METplus to generate the stat files based on the averaged
#      CTC
#*****************************************************************************
if [ $just_cnv = yes ] ; then
  $USHevs/mesoscale/evs_sref_cnv.sh
  export err=$?; err_chk
else
  $USHevs/mesoscale/evs_sref_grid2obs.sh
  export err=$?; err_chk
fi

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$msg"

exit 

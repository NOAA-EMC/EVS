#!/bin/ksh
#################################################################
# Script Name: verf_g2g_reflt.sh.sms $vday $vcyc
# Purpose:   To run grid-to-grid verification on reflectivity
#
# Log History:  Julia Zhu -- 2010.04.28 
################################################################
set -x

export WORK=$DATA
cd $WORK

export MET_bin_exec='bin'

export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}
export just_cnv=${just_cnv:-'no'} 

export GRID2OBS_CONF=$PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS


msg="$job HAS BEGUN"
postmsg "$jlogfile" "$msg"

if [ $just_cnv = yes ] ; then
  $USHevs/mesoscale/evs_sref_cnv.sh
else
  $USHevs/mesoscale/evs_sref_grid2obs.sh
fi

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0

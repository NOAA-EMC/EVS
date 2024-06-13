#!/bin/ksh
#################################################################
# Purpose:   Setup some paths and run sref grid2obs stat ush scripts
#
# Last updated 
#               04/10/2024: Add restart capability, Binbin Zhou, Lynker@EMC/NCEP
#                           Combine cnv into grid2obs job
#               10/27/2023: Binbin Zhou, Lynker@EMC/NCEP
#################################################################
#
set -x
export machine=${machine:-"WCOSS2"} 
export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH
export WORK=$DATA
cd $WORK

export MET_bin_exec='bin'

export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}
export just_cnv=${just_cnv:-'no'} 

export GRID2OBS_CONF=$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS

export COMOUTrestart=$COMOUTsmall/restart
if [ ! -d $COMOUTrestart ] ; then
  mkdir -p $COMOUTrestart
fi

#********************************************
# Check the input data files availability
# ******************************************

$USHevs/mesoscale/evs_check_sref_files.sh
export err=$?; err_chk


#***********************************************************************************
# The method in ceiling and vis (cnv) job is to deal with the conditional mean
#  (1) First average hits, false alarms, etc in the categoery table
#      over all times to get averaged CTC (runevs_sref_cnv.sh)
#  (2) After sref_cnv.sh is finished, run evs_sref_grid2obs.sh by using
#        METplus to generate the stat files based on the averaged CTC
#
#For visibility and ceiling (c and v, or cnv), the computation of CTC mean metrics 
#is tricky. Computation CTC  ensemble mean could be misleading in case of clear sky. 
#In clear sky, there is no value for  cnv,  so the models define them to be very large 
#arbitrary values. In this case, if first averaging CTC over forecast times and then 
#averaging over members to get metrics (as current METplus does) could be wrong  
#(e.g. got unexpected low ETS).  After discussing with Logan, we  decided that first  
#averaging CTC among the members, then averaging over forecast times to get CTC
#metrics. The results are much better. So for sref, first run cnv job. After it is
#finished, run grid2obs job. In global_ens, both are combined together in grid2obs.
#*****************************************************************************

if [ -e $DATA/prepbufr.missing ] || [ -e $DATA/sref_mbrs.missing ]; then
  echo "WARNING: either prepbufr or sref members are missing"
else

  if [ ! -e $COMOUTrestart/evs_sref_cnv.completed ] ; then
    $USHevs/mesoscale/evs_sref_cnv.sh
    export err=$?; err_chk
  fi

   $USHevs/mesoscale/evs_sref_grid2obs.sh
   export err=$?; err_chk

fi


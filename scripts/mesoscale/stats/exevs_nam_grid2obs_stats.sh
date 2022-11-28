#!/bin/sh
###############################################################################
# Name of Script: exevs_nam_grid2obs_stats.sh 
# Purpose of Script: This script generates grid-to-observations
#                    verification statistics using METplus for the
#                    atmospheric component of NAM models
# Log history:
###############################################################################


set -x

export VERIF_CASE_STEP_abbrev="g2os"

# Set run mode
if [ $RUN_ENVIR = nco ]; then
    export evs_run_mode="production"
    source $config
else
    export evs_run_mode=$evs_run_mode
fi
echo "RUN MODE:$evs_run_mode"

# Make directory
mkdir -p ${VERIF_CASE}_${STEP}


mkdir -p $DATA/logs
mkdir -p $DATA/stat

export OBSDIR=OBS
export fcstmax=48

export model1=`echo $MODELNAME | tr a-z A-Z`
echo $model1

#run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/GridStat_fcstHYSPLIT_obsMYDUST.conf $PARMevs/metplus_config/machine.conf

echo $cyc

if [ $cyc = 00 ] || [ $cyc = 06 ] || [ $cyc = 12 ] || [ $cyc = 18 ]
then
  run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PB2NC_obsRAOB.conf 
  run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstMESOSCALE_obsRAOB.conf
  #run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstMESOSCALE_obsRAOB.conf $PARMevs/metplus_config/machine.conf
  mkdir -p $COMOUTsmall
  cp $DATA/grid_stat/$MODELNAME/* $COMOUTsmall
fi


if [ $cyc = 23 ]
then
   mkdir -p $COMOUTfinal
   run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstMESOSCALE_obsRAOB_GatherByDay.conf $PARMevs/metplus_config/machine.conf
fi


exit

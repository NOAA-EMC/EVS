#!/bin/sh
###############################################################################
# Name of Script: exevs_rap_grid2obs_stats.sh 
# Purpose of Script: This script generates grid-to-observations
#                    verification statistics using METplus for the
#                    atmospheric component of RAP models
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
export model0=`echo $MODELNAME | tr A-Z a-z`
echo $model1


for WVAR in $VAR_NAME_LIST; do
  # select var to work on
  export VAR_NAME=${WVAR}
  # Verification Var
  source ${USHevs}/mesoscale/run_var_${model0}.sh
  
  for VHOUR in $VHOUR_LIST; do
    export VHOUR=$VHOUR
    cyc=$VHOUR
    
    if [ $cyc = 00 ] || [ $cyc = 06 ] || [ $cyc = 12 ] || [ $cyc = 18 ];  then
      run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PB2NC_obsRAOB.conf 
      # export err=$?; err_chk

      run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstMESOSCALE_obsRAOB.conf
      # export err=$?; err_chk
    fi
    
    if [ $cyc = 23 ];  then
      mkdir -p $COMOUTfinal
      run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstMESOSCALE_obsRAOB_GatherByDay.conf 
      # export err=$?; err_chk
    fi
  done
done

# Copy output files into the correct EVS COMOUT directory
  if [ $SENDCOM = YES ]; then
    for MODEL_DIR_PATH in $MET_PLUS_OUT/gather_small/stat_analysis/$MODELNAME; do
        MODEL_DIR=$(echo ${MODEL_DIR_PATH##*/})
        mkdir -p $COMOUT/$MODEL_DIR
        for FILE in $MODEL_DIR_PATH/*; do
            cp -v $FILE $COMOUT/$MODEL_DIR/.
        done
    done
    for MODEL_DIR_PATH in $MET_PLUS_OUT/raob/point_stat/$MODELNAME; do
        MODEL_DIR=$(echo ${MODEL_DIR_PATH##*/})
        mkdir -p $COMOUTsmall/$MODEL_DIR
        for FILE in $MODEL_DIR_PATH/*; do
            cp -v $FILE $COMOUTsmall/$MODEL_DIR/.
        done
    done
  fi

exit

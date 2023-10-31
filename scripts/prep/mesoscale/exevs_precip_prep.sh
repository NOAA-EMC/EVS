#!/bin/sh
###############################################################################
# Name of Script: exevs_mesoscale_precip_prep.sh 
# Purpose of Script: This script does the prep work for the
#                    precipitation of the mesoscale models
# Log history:
###############################################################################

set -x

# Set run mode
export evs_run_mode=$evs_run_mode
source $config

# Make directory
mkdir -p $DATA/${COMPONENT}.${VDATE}

python ${USHevs}/${COMPONENT}/${COMPONENT}_${VERIF_CASE}_prep.py
export err=$?; err_chk
 
# Copy output files into the correct EVS COMOUT directory
#  if [ $SENDCOM = YES ]; then
#    for MODEL_DIR_PATH in $MET_PLUS_OUT/gather_small/stat_analysis/$MODELNAME*; do
#        MODEL_DIR=$(echo ${MODEL_DIR_PATH##*/})
#        mkdir -p $COMOUT/$MODEL_DIR
#        for FILE in $MODEL_DIR_PATH/*; do
#            cp -v $FILE $COMOUT/$MODEL_DIR/.
#        done
#    done
#    for MODEL_DIR_PATH in $MET_PLUS_OUT/raob/point_stat/$MODELNAME*; do
#        MODEL_DIR=$(echo ${MODEL_DIR_PATH##*/})
#        mkdir -p $COMOUTsmall/$MODEL_DIR
#        for FILE in $MODEL_DIR_PATH/*; do
#            cp -v $FILE $COMOUTsmall/$MODEL_DIR/.
#        done
#    done
#  fi

exit

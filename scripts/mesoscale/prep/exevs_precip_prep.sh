#!/bin/sh
###############################################################################
# Name of Script: exevs_precip_precip.sh 
# Purpose of Script: This script does the prep work for the
#                    precipitation of the mesoscale models
# Log history:
###############################################################################

set -x

# Set run mode
if [ $RUN_ENVIR = nco ]; then
    export evs_run_mode="production"
    source $config
else
    export evs_run_mode=$evs_run_mode
fi
echo "RUN MODE:$evs_run_mode"

# Make directory
mkdir -p $DATA/${COMPONENT}.${VDATE}

python ${USHevs}/${COMPONENT}/${COMPONENT}_${VERIF_CASE}_prep.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran ${USHevs}/${COMPONENT}/${COMPONENT}_${VERIF_CASE}_prep.py"

 
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

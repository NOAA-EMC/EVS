#!/bin/sh
###############################################################################
# Name of Script: exevs_rap_precip_stats.sh 
# Purpose of Script: This script generates precipitation
#                    verification statistics using METplus for the
#                    atmospheric component of RAP models
# Log history:
###############################################################################

set -x

export VERIF_CASE_STEP_abbrev="precips"

# Set run mode
if [ $RUN_ENVIR = nco ]; then
    export evs_run_mode="production"
    source $config
else
    export evs_run_mode=$evs_run_mode
fi
echo "RUN MODE:$evs_run_mode"

# Make directory
mkdir -p $DATA/logs
mkdir -p $DATA/confs
mkdir -p $DATA/data
mkdir -p $DATA/tmp
mkdir -p $DATA/jobs
mkdir -p $DATA/${MODELNAME}.${VDATE}

# Get RAP, MRMS, and CCPA data
python $USHevs/mesoscale/mesoscale_precip_get_data.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran mesoscale_precip_get_data.py"

# Send for missing files
export maillist=${maillist:-'geoffrey.manikin@noaa.gov,mallory.row@noaa.gov'}
for FILE in $DATA/mail_*; do
    $FILE
done

# What jobs to run
#if [ $cyc = 23 ]; then
#    JOB_GROUP_list="assemble_data generate_stats gather_stats"
#else
#    JOB_GROUP_list="assemble_data generate_stats"
#fi

# Create and run job scripts
#for group in $JOB_GROUP_list; do
#    export JOB_GROUP=$group
#    mkdir -p $DATA/jobs/$JOB_GROUP
#    echo "Creating and running jobs for precip stats: ${JOB_GROUP}"
#    python $USHevs/mesoscale/mesoscale_precip_get_data_create_job_scripts.py
#    status=$?
#    [[ $status -ne 0 ]] && exit $status
#    [[ $status -eq 0 ]] && echo "Succesfully ran mesoscale_precip_get_data_create_job_scripts.py"
#done

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

#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_atmos_grid2grid_stats.sh 
# Purpose of Script: This script generates long term
#                    verification statistics for the atmospheric component
#                    of global deterministic models
# Log history:
###############################################################################

set -x

# Set run mode
if [ $RUN_ENVIR = nco ]; then
    export evs_run_mode="production"
else
    export evs_run_mode=$evs_run_mode
fi
echo "RUN MODE:$evs_run_mode"
if [ $evs_run_mode = production ] && [ $envir = prod ]; then
    echo "exevs_global_det_atmos_grid2grid_stats.sh does run in production; exit"
    exit 0
fi

# Make monthly stats
python $USHevs/global_det/global_det_atmos_stats_long_term_monthly.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_stats_long_term_monthly.py"
echo

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    for MODEL_PATH in $DATA/monthly/grid2grid/monthly_means/*; do
        MODEL_SUBDIR=$(echo ${MODEL_PATH##*/})
        mkdir -p $COMOUTmonthlystats/$MODEL_SUBDIR
        for FILE in $DATA/monthly/grid2grid/monthly_means/$MODEL_SUBDIR/*; do
            cp -v $FILE $COMOUTmonthlystats/$MODEL_SUBDIR/.
        done
    done
fi

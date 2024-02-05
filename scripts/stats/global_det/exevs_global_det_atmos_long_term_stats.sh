#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_atmos_long_term_stats.sh
# Developers: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det atmos stats step
#                    for the long-term verification. It uses EMC-developed python
#                    scripts to generate averages from METplus stats files.
#                    This is not run in operations.
###############################################################################

set -x

echo "RUN MODE:$evs_run_mode"
if [ $evs_run_mode = production ] && [ $envir = prod ]; then
    err_exit "exevs_global_det_atmos_long_term_stats.sh does run in production"
fi

# Make stats
python $USHevs/global_det/global_det_atmos_stats_long_term.py
export err=$?; err_chk

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    for MODEL_PATH in $DATA/monthly/grid2grid/monthly_means/*; do
        MODEL_SUBDIR=$(echo ${MODEL_PATH##*/})
        mkdir -p $COMOUTmonthlystats/$MODEL_SUBDIR
        for FILE in $DATA/monthly/grid2grid/monthly_means/$MODEL_SUBDIR/*; do
            if [ -f $FILE ]; then
                cp -v $FILE $COMOUTmonthlystats/$MODEL_SUBDIR/.
            fi
        done
    done
    if [ $VDATEmm = 12 ]; then
        for MODEL_PATH in $DATA/yearly/grid2grid/yearly_means/*; do
            MODEL_SUBDIR=$(echo ${MODEL_PATH##*/})
            mkdir -p $COMOUTyearlystats/$MODEL_SUBDIR
            for FILE in $DATA/yearly/grid2grid/yearly_means/$MODEL_SUBDIR/*; do
                if [ -f $FILE ]; then
                    cp -v $FILE $COMOUTyearlystats/$MODEL_SUBDIR/.
                fi
            done
        done
    fi
fi

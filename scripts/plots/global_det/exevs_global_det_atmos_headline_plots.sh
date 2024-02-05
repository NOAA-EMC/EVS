#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_headline_plots.sh
# Developers: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det atmos plots step
#                    for the headline verification. It uses EMC-developed
#                    python scripts to do the plotting.
###############################################################################

set -x

echo "RUN MODE:$evs_run_mode"

# Create headline plots
python $USHevs/global_det/global_det_atmos_plots_headline.py
export err=$?; err_chk

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    # Make and copy tar file
    cd $DATA/images
    tar -cvf $DATA/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar *.png
    if [ -f $DATA/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar ]; then
        cp -v $DATA/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar $COMOUT/.
    fi
fi

# Cat the plotting log files
log_dir=$DATA/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
    for log_file in $log_dir/*; do
        echo "Start: $log_file"
        cat $log_file
        echo "End: $log_file"
    done
fi

if [ $SENDDBN = YES ]; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar
fi

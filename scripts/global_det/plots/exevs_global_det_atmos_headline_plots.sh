#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_headline_plots.sh
# Purpose of Script: This script generates grid-to-grid verification headline
#                    plots using python for global deterministic models
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

pwd

# Create job scripts data
python $USHevs/global_det/global_det_atmos_plots_headline.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_plots_headline.py"

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    # Make and copy tar file
    cd $DATA/images
    tar -cvf $DATA/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar *.png
    cp -v $DATA/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar $COMOUT/.
fi
cd $DATA

# Non-production jobs
if [ $evs_run_mode != "production" ]; then
    # Clean up
    if [ $KEEPDATA != "YES" ] ; then
        cd $DATAROOT
        rm -rf $DATA
    fi
fi

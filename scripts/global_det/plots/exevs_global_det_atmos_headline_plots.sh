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

# Source config
source $config

# Create headline plots
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

if [ $SENDDBN = YES ]; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar
fi

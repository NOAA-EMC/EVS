#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_atmos_long_term_plots.sh
# Developers: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det atmos plots step
#                    for the long-term verification. It uses EMC-developed
#                    python scripts to do the plotting.
###############################################################################

set -x

echo "RUN MODE:$evs_run_mode"
if [ $evs_run_mode = production ] && [ $envir = prod ]; then
    err_exit "exevs_global_det_atmos_long_term_plots.sh does run in production"
fi

# Make plots
python $USHevs/global_det/global_det_atmos_plots_long_term.py
export err=$?; err_chk

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    # Make and copy tar file
    large_tar_file=${DATA}/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATEYYYY}${VDATEmm}.tar
    if [ $VDATEmm = 12 ]; then
        tar -cvf ${large_tar_file} -C ${DATA}/${VDATEYYYY}_${VDATEmm}_ACC/images . -C ${DATA}/monthly/grid2grid/images . -C ${DATA}/yearly/grid2grid/images .
    else
        tar -cvf ${large_tar_file} -C ${DATA}/${VDATEYYYY}_${VDATEmm}_ACC/images . -C ${DATA}/monthly/grid2grid/images .
    fi
    if [ -f $large_tar_file ]; then
       cp -v $large_tar_file $COMOUT/.
    fi
fi

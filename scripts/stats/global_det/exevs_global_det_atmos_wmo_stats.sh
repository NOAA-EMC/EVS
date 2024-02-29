#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_atmos_wmo_stats.sh
# Developers: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det atmos WMO stats step.
#                    It does grid-to-grid and grid-to-observations following the
#                    WMO requirements.
###############################################################################

set -x

# Make directories
mkdir -p ${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE} ${MODELNAME}.${VDATE}
mkdir -p jobs logs tmp

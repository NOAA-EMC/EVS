#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_wmo_grid2grid_stats.sh
# Developers: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det wmo stats step
#                    for the grid-to-grid verification. It uses METplus to
#                    generate the statistics.
###############################################################################

set -x

echo "Let's make ${RUN} stats"

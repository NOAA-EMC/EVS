#!/bin/bash
###############################################################################
# Name of Script: exevs_glwu_prep.sh
# Purpose of Script: To pre-process NDBC validation data.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# convert NDBC *.txt files into a netcdf file using ASCII2NC
export RUN=ndbc
mkdir -p $COMOUTprep/$COMPONENT.$VDATE/$RUN

run_metplus.py -c $CONFIGevs/metplus_$COMPONENT.conf \
-c $CONFIGevs/grid2obs/$STEP/ASCII2NC_obsNDBC.conf

exit

################################ END OF SCRIPT ################################

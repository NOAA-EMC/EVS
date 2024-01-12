#!/bin/bash
##################################################################
# Purpose:   To run grid-to-grid verification on all global chem
#
# Log History:
#################################################################
set -x

export VDATE2=$PDYm3
export METPLUS_PATH
export RUNnow=viirs

#run Series Analysis

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/metplus_chem.conf \
-c ${CONFIGevs}/SeriesAnalysis_fcstGEFS_obsVIIRS.conf

export err=$?; err_chk

exit


#!/bin/bash
##################################################################
# Purpose:   To run grid-to-grid verification on all global chem
#
# Log History:
#################################################################
set -x

export METPLUS_PATH
export RUNnow=abi

#run Series Analysis

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/metplus_chem.conf \
-c ${CONFIGevs}/SeriesAnalysis_fcstGEFS_obsABI.conf

export err=$?; err_chk

exit


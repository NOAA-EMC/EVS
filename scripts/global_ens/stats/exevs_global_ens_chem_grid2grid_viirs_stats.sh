#!/bin/bash
##################################################################
# Purpose:   To run grid-to-grid verification on all global chem
#
# Log History:
#################################################################
set -x

export VDATE
export STEP
export VDATE=$PDYm2
export VDATE2=$PDYm3
export METPLUS_PATH
export RUNnow=viirs

#run Series Analysis

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/SeriesAnalysis_fcstGEFS_obsVIIRS.conf

#/usr/bin/env
export err=$?; err_chk
cat $pgmout

exit


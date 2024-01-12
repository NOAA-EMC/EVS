#!/bin/bash
#################################################################
# Purpose:   To run grid-to-obs verification on all global chem
#
# Log History:  
################################################################
set -x

#export METPLUS_PATH
export RUNnow=airnow
export outtyp=pm25

#run Point_Stat

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/metplus_chem.conf \
-c ${CONFIGevs}/PointStat_fcstPM25_obsAirnow.conf

exit


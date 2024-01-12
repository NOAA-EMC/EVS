#!/bin/bash
#################################################################
# Purpose:   To run grid-to-obs verification on all global chem
#
# Log History:  
################################################################
set -x

export METPLUS_PATH
export RUNnow=aeronet

#run Point_Stat

${METPLUS_PATH}/ush/run_metplus.py -c ${config_dir}/metplus_chem.conf \
-c ${config_dir}/PointStat_fcstGEFSAero_obsAeronet.conf

exit


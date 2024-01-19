#!/bin/bash
#################################################################
# Purpose:   To run grid-to-obs verification on all global chem
#
# Log History:  
################################################################
set -x

export CONFIGevs=${CONFIGevs:-${PARMevs}/${STEP}/$COMPONENT/${RUN}_${VERIF_CASE}}

export METPLUS_PATH
export RUNnow=aeronet

#run Point_Stat

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/metplus_chem.conf \
-c ${CONFIGevs}/PointStat_fcstGEFSAero_obsAeronet.conf

exit


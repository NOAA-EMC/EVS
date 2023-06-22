#!/bin/bash
#################################################################
# Purpose:   To run grid-to-obs verification on all global chem
#
# Log History:  
################################################################
set -x

#export VDATE
export STEP
export VDATE=$PDYm2
export METPLUS_PATH
export RUNnow=aeronet

 #run Point_Stat

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/PointStat_fcstGEFSAero_obsAeronet.conf

#${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
#-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/ASCII2NC_obsAeronet.conf


# sum small stat files into one big file using Stat_Analysis
mkdir -p $COMOUTfinal

#${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/StatAnalysis_Tutorial.conf \
#-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/Statanalysis_fcstGEFSAero_obsAeronet.conf

exit


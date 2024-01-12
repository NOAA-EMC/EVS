#!/bin/bash
##################################################################
# Purpose:   To run grid-to-grid verification on all global chem
#
# Log History:
#################################################################
set -x

export VDATE
export STEP
export VDATE=$PDYm3
export METPLUS_PATH
export RUNnow=geos5

 #run Grid_Stat

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/GridStat_fcstGEFS_obsGEOS5_taod.conf

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/GridStat_fcstGEFS_obsGEOS5_daod.conf

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/GridStat_fcstGEFS_obsGEOS5_ocaod.conf

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/GridStat_fcstGEFS_obsGEOS5_bcaod.conf

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/GridStat_fcstGEFS_obsGEOS5_suaod.conf

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/GridStat_fcstGEFS_obsGEOS5_ssaod.conf


#/usr/bin/env
export err=$?; err_chk
cat $pgmout

exit


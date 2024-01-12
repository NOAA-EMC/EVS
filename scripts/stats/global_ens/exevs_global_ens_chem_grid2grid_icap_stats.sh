#!/bin/bash
##################################################################
# Purpose:   To run grid-to-grid verification on all global chem
#
# Log History:
#################################################################
set -x

export VDATE
export STEP
export cyc=00
export VDATE=$PDYm3
export PDYHHm3=$($NDATE -72 $PDYHH)
echo "3 days ago $PDYHHm3"
export METPLUS_PATH
echo "metplus path $METPLUS_PATH"
echo export maskpath=$MASKS
export RUNnow=icap


#run Grid_Stat

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/GridStat_fcstGEFS_obsICAP_taod.conf

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/GridStat_fcstGEFS_obsICAP_daod.conf

#/usr/bin/env
export err=$?; err_chk
cat $pgmout

exit


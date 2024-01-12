#!/bin/bash
##################################################################
# Purpose:   To run grid-to-grid verification on all global chem
#
# Log History:
#################################################################
set -x

export cyc=00


??? PDYHH ???
export PDYHHm3=$($NDATE -72 $PDYHH)
echo "3 days ago $PDYHHm3"
export METPLUS_PATH
echo "metplus path $METPLUS_PATH"
echo export maskpath=$MASKS
export RUNnow=icap


#run Grid_Stat

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/metplus_chem.conf \
-c ${CONFIGevs}/GridStat_fcstGEFS_obsICAP_taod.conf

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/metplus_chem.conf \
-c ${CONFIGevs}/GridStat_fcstGEFS_obsICAP_daod.conf

export err=$?; err_chk

exit


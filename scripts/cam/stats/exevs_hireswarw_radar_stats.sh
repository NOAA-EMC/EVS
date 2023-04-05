#!/bin/bash
###############################################################################
# Name of Script: exevs_hireswarw_radar_stats.sh
# Contact(s):     Logan Dawson
# Purpose of Script: This script runs METplus to generate radar verifications
#                    statistics for the HiResW ARW.
# History Log:
# 01/03/2023: Initial script assembled by Logan Dawson
###############################################################################


set +x

echo
echo " ENTERING SUB SCRIPT $0 "
echo

set -x


if [ $obfound = 1 -a $fcstnum -gt 0 ] ; then


   run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/GridStat_obsMRMS_${RADAR_FIELD}.conf
   export err=$?; err_chk

else

   echo "Missing forecast or observation file(s) for ${VDATE}${cyc}. METplus will not run."

fi


if [ $SENDCOM = YES ]; then
   pass
fi


exit


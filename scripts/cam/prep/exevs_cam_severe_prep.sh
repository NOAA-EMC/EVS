#!/bin/bash
###############################################################################
# Name of Script: exevs_cam_severe_prep.sh
# Contact(s):     Logan Dawson
# Purpose of Script: This script preprocesses SPC storm reports for 
#                    CAM severe verification.
# History Log:
# 1/2023: Initial script assembled by Logan Dawson 
###############################################################################


set +x

echo 
echo " ENTERING SUB SCRIPT $0 "
echo

set -x



############################################################
# Set some other environment variables 
############################################################
export ACCUM_BEG=${ACCUM_BEG:-${REP_DATE}12}
export ACCUM_END=${ACCUM_END:-${VDATE}12}

export VERIF_GRID=G211
export VERIF_GRID_DX=81.271
export GAUSS_RAD=120


############################################################
# Check for SPC report file to process or exit gracefully
############################################################

if [ -s $COMINspc/${REP_DATE}/validation_data/weather/spc/spc_reports_${REP_DATE}.csv ]; then

   mkdir -p $COMOUTspc

   ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/Point2Grid_obsSPC_PracticallyPerfect.conf
   export err=$?; err_chk

else

   export subject="SPC LSR Data Missing for EVS ${COMPONENT}"
   export maillist=${maillist:-'logan.dawson@noaa.gov,geoffrey.manikin@noaa.gov'}
   echo "Warning: The ${REP_DATE} SPC report file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
   echo "Job Name & ID: $job $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $maillist
   exit 0

fi


if [ $SENDCOM = YES ]; then
   mkdir -p $COMOUTspc
   for FILE in $DATA/point2grid/*; do
      cp -v $FILE $COMOUTspc
   done
fi


exit


#!/bin/bash
###############################################################################
# Name of Script: exevs_cam_severe_prep.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script preprocesses SPC data (storm reports 
#                    and outlook areas) for CAM verification.
# History Log:
# 1/2023: Initial script assembled by Logan Dawson 
# 4/2023: Script updated to handle storm reports and outlook areas 
###############################################################################


set -x

echo 
echo " ENTERING SUB SCRIPT $0 "
echo

set -x


############################################################
## Copy and preprocess SPC OTLK files
#############################################################

python $USHevs/${COMPONENT}/evs_prep_spc_otlk.py
export err=$?; err_chk

# Check for output in tmp working directory before copying to COMOUT 
if [ -d $DATA/gen_vx_mask ]; then

   if [ "$(ls -A $DATA/gen_vx_mask)" ]; then

      # Copy output to $COMOUT
      if [ $SENDCOM = YES ]; then
         mkdir -p $COMOUTotlk
         for FILE in $DATA/gen_vx_mask/*; do
            cp -v $FILE $COMOUTotlk
         done
      fi

   else
      data_missing=true
   fi

else
   data_missing=true
fi


# Send missing data alert if needed
if [ $data_missing ]; then

   if [ $SENDMAIL = YES ]; then
      export subject="SPC OTLK Data Missing for EVS ${COMPONENT}"
      echo "Warning: The ${OTLK_DATE} SPC outlook file(s) is missing. METplus will not run." > mailmsg
      echo "Missing files are $COMINspc/${OTLK_DATE}/validation_data/weather/spc/day*otlk_{OTLK_DATE}*.zip" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $maillist
   fi

fi


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

   mkdir -p $COMOUTlsr

   # Run METplus
   ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/Point2Grid_obsSPC_PracticallyPerfect.conf
   export err=$?; err_chk


   # Copy output to $COMOUT
   if [ $SENDCOM = YES ]; then
      mkdir -p $COMOUTlsr
      for FILE in $DATA/point2grid/*; do
         cp -v $FILE $COMOUTlsr
      done
   fi

else

   if [ $SENDMAIL = YES ]; then
      export subject="SPC LSR Data Missing for EVS ${COMPONENT}"
      echo "Warning: The ${REP_DATE} SPC report file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
      echo "Missing file is $COMINspc/${REP_DATE}/validation_data/weather/spc/spc_reports_${REP_DATE}.csv" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $maillist
   fi

fi



exit


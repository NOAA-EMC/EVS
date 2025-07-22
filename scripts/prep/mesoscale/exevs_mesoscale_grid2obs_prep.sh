#!/bin/bash
###############################################################################
# Name of Script: exevs_cam_severe_prep.sh
# Contact(s):     Marcel G. Caron (marcel.caron@noaa.gov),
#                 Perry C. Shafran (perry.shafran@noaa.gov)
# Purpose of Script: This script preprocesses SPC data 
#                    (outlook areas) for mesoscale verification.
# History Log:
# 1/2023: Initial script assembled 
# 4/2023: Script updated to handle storm reports and outlook areas 
# 7/2025: Updated script for mesoscale
###############################################################################


set -x

echo 
echo " ENTERING SUB SCRIPT $0 "
echo

set -x
export machine=${machine:-"WCOSS2"}


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
            if [ -s "$FILE" ]; then
               cp -v $FILE $COMOUTotlk
            fi
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

   echo "WARNING: File $DCOMINspc/${OTLK_DATE}/validation_data/weather/spc/day*otlk_{OTLK_DATE}*.zip is missing"
   if [ $SENDMAIL = YES ]; then
      export subject="SPC OTLK Data Missing for EVS ${COMPONENT}"
      echo "WARNING: The ${OTLK_DATE} SPC outlook file(s) is missing. METplus will not run." > mailmsg
      echo "Missing files are $DCOMINspc/${OTLK_DATE}/validation_data/weather/spc/day*otlk_{OTLK_DATE}*.zip" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $MAILTO
   fi

fi



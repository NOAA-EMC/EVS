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

if [ -s $DCOMINspc/${REP_DATE}/validation_data/weather/spc/spc_reports_${REP_DATE}.csv ]; then

   mkdir -p $COMOUTlsr

   # Run METplus
   ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/Point2Grid_obsSPC_PracticallyPerfect.conf
   export err=$?; err_chk


   # Copy output to $COMOUT
   if [ $SENDCOM = YES ]; then
      mkdir -p $COMOUTlsr
      for FILE in $DATA/point2grid/*; do
         if [ -s "$FILE" ]; then
            cp -v $FILE $COMOUTlsr
         fi
      done
   fi

else

   echo "WARNING: File $DCOMINspc/${REP_DATE}/validation_data/weather/spc/spc_reports_${REP_DATE}.csv is missing."
   if [ $SENDMAIL = YES ]; then
      export subject="SPC LSR Data Missing for EVS ${COMPONENT}"
      echo "WARNING: The ${REP_DATE} SPC report file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
      echo "Missing file is $DCOMINspc/${REP_DATE}/validation_data/weather/spc/spc_reports_${REP_DATE}.csv" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $MAILTO
   fi

fi

# Cat the METplus log files
log_dir=$DATA/logs
if [ -d $log_dir ]; then
    log_file_count=$(find $log_dir -type f | wc -l)
    if [[ $log_file_count -ne 0 ]]; then
        log_files=("$log_dir"/*)
        for log_file in "${log_files[@]}"; do
            if [ -f "$log_file" ]; then
                echo "Start: $log_file"
                cat "$log_file"
                echo "End: $log_file"
            fi
        done
    fi
fi

exit


#!/bin/bash
###############################################################################
# Name of Script: exevs_rrfs_radar_stats.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script runs METplus to generate radar
#                    verification statistics for RRFS.
# History Log:
# 04/28/2023: Initial script assembled by Logan Dawson
###############################################################################


set +x

echo
echo " ENTERING SUB SCRIPT $0 "
echo

set -x


###################################################################
# Set some model-specific variables
###################################################################

export machine=${machine:-"WCOSS2"}
if [ ${MODELNAME} = rrfs ]; then

   fhr_min=1
   fhr_max=60
   fhr_inc=1

   export MODEL_INPUT_DIR=${COMINrrfs}
   export CONUS_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/{init?fmt=%H}/${modsys}.t{init?fmt=%2H}z.prslev.f{lead?fmt=%3H}.conus_3km.grib2

fi


###################################################################
# Check for forecast files to process
####################################################################

nfcst_ak=0
nfcst_conus=0

fhr=$fhr_min

# Loop over the available 24-h periods for each model
while [ $fhr -le $fhr_max ]; do

   export fhr

   # Define initialization date/cycle for each forecast lead
   export IDATE=`$NDATE -$fhr ${VDATE}${vhr} | cut -c 1-8`
   export INIT_HR=`$NDATE -$fhr ${VDATE}${vhr} | cut -c 9-10`

   # Define forecast filename for each model 
   if [ ${MODELNAME} = rrfs ]; then
      export conus_file=${modsys}.${IDATE}/${INIT_HR}/${modsys}.t${INIT_HR}z.prslev.f$(printf "%03d" $fhr).conus_3km.grib2
   fi

   # Check for the existence of each forecast file 
   if [ -s ${MODEL_INPUT_DIR}/${conus_file} ]; then
      echo $fhr >> $DATA/conus_fcst_list
      nfcst_conus=$((nfcst_conus+1))
      conus_fcst_found=1

   else
      echo "Missing file(s) is ${MODEL_INPUT_DIR}/${conus_file}" >> $DATA/missing_fcst_list

   fi

   fhr=$((fhr+$fhr_inc))

done


if [ $nfcst_conus = 0 ]; then
   if [ $SENDMAIL = YES ]; then
      export subject="${MODELNAME} Data Missing for EVS ${COMPONENT}"
      echo "Warning: ${MODELNAME} forecast file(s) is missing for valid date ${VDATE}${vhr}. METplus will not run." > mailmsg
      echo -e "`cat $DATA/missing_fcst_list`" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $MAILTO
   fi

# Or proceed with running METplus
else

#  export nfcst_ak
   export nfcst_conus

#  export ak_fhrs=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/ak_fcst_list`
   export conus_fhrs=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/conus_fcst_list`

   mkdir -p $DATA/grid_stat

   ############################################################
   # Check for obs files to process
   ############################################################

   DOMAINS="alaska conus"
   DOMAINS="conus"

   # Loop over domains
   for DOMAIN in ${DOMAINS}; do

      # Set list of fields based on domain
      if [ $DOMAIN = conus ]; then
         RADAR_FIELDS="REFC RETOP"
      elif [ $DOMAIN = alaska ]; then
         RADAR_FIELDS="REFC"
      fi

      # Loop over radar fields
      for RADAR_FIELD in ${RADAR_FIELDS}; do
         echo "${USHevs}/${COMPONENT}/evs_cam_stats_radar.sh $DOMAIN $RADAR_FIELD" >> $DATA/poescript
      done
   done


   ###################################################################
   # Run the command file 
   ####################################################################

   chmod 775 $DATA/poescript

   export MP_PGMMODEL=mpmd
   export MP_CMDFILE=${DATA}/poescript

   if [ $USE_CFP = YES ]; then

   #  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
      echo "running cfp"
      mpiexec -np $nproc --cpu-bind verbose,core cfp ${MP_CMDFILE} 
      export err=$?; err_chk
      echo "done running cfp"

   else

      echo "not running cfp"
      ${MP_CMDFILE} 
      export err=$?; err_chk

   fi

fi


###################################################################
# Run METplus (StatAnalysis) if GridStat output exists
###################################################################

if [ $vhr = 23 ]; then

   if [ "$(ls -A $COMOUTsmall)" ]; then

      run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstCAM_obsMRMS_gatherByDay.conf
      export err=$?; err_chk

      # Copy output to $COMOUTfinal
      if [ $SENDCOM = YES ]; then
         mkdir -p $COMOUTfinal
         for FILE in $DATA/stat_analysis/*; do
            if [ -s "$FILE" ]; then
                cp -v $FILE $COMOUTfinal
            fi
         done
      fi

   else
      echo "Missing stat output for ${VDATE}. METplus will not run."

   fi

fi

# Cat the METplus log files
log_dir="$DATA/logs"
if [ -d $log_dir ]; then
    log_file_count=$(find $log_dir -type f | wc -l)
    if [[ $log_file_count -ne 0 ]]; then
        log_files=("$log_dir"/*)
        for log_file in "$log_files[@]}"; do
            if [ -f "$log_file" ]; then
                echo "Start: $log_file"
                cat "$log_file"
                echo "End: $log_file"
            fi
        done
    fi
fi

exit

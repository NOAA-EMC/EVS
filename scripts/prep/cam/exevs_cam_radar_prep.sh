#!/bin/bash
###############################################################################
# Name of Script: exevs_cam_radar_prep.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script preprocesses MRMS radar observations for 
#                    CAM verification.
# History Log:
# 12/22/2022: Initial script assembled by Logan Dawson 
###############################################################################


set -x

echo 
echo " ENTERING SUB SCRIPT $0 "
echo

set -x
export machine=${machine:-"WCOSS2"}


############################################################
# Copy and unzip MRMS product files
############################################################
mkdir -p $COMOUTmrms

python $USHevs/${COMPONENT}/evs_prep_mrms_radar.py
export err=$?; err_chk


############################################################
# Set some other environment variables 
############################################################



############################################################
# Check for MRMS files to process or exit gracefully
############################################################

# Define domains to operate on
DOMAINS="conus alaska"

# Regrid each MRMS product
for DOMAIN in ${DOMAINS}; do

   export DOMAIN
   # Set fields to regrid based on domain
   if [ $DOMAIN = conus ]; then

      RADAR_FIELDS="REFC RETOP"
      export VERIF_GRID=G227
      export VERIF_GRID_DX=5.079
      export GAUSS_RAD=25.395
      export MAX_REGRID_WIDTH=17

   elif [ $DOMAIN = alaska ]; then

      RADAR_FIELDS="REFC"
      export VERIF_GRID=G091
      export VERIF_GRID_DX=2.976
      export GAUSS_RAD=25.395
      export MAX_REGRID_WIDTH=27

   fi


   for RADAR_FIELD in ${RADAR_FIELDS}; do

      if [ $RADAR_FIELD = REFC ]; then
         MRMS_PRODUCT=MergedReflectivityQCComposite_00.50
	 export OBS_VAR=MergedReflectivityQCComposite
      elif [ $RADAR_FIELD = REFD1 ]; then
         MRMS_PRODUCT=SeamlessHSR_00.00
      elif [ $RADAR_FIELD = RETOP ]; then
         MRMS_PRODUCT=EchoTop18_00.50
      fi

      if [ -s $DATA/MRMS_${DOMAIN}_tmp/${MRMS_PRODUCT}_${VDATE}-${vhr}0000.grib2 ]; then

	 # Run METplus
         ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/RegridDataPlane_obsMRMS_${RADAR_FIELD}.conf
         export err=$?; err_chk

	 # Copy output to $COMOUT
         if [ $SENDCOM = YES ]; then
            mkdir -p $COMOUTmrms/${DOMAIN}
            for FILE in $DATA/MRMS_${DOMAIN}/*; do
               if [ -s "$FILE" ]; then
                  cp -v $FILE $COMOUTmrms/${DOMAIN}
               fi
            done
         fi

      else

         if [ $SENDMAIL = YES ]; then
            export subject="MRMS ${MRMS_PRODUCT} Data Missing for EVS ${COMPONENT}"
            echo "WARNING: The ${MRMS_PRODUCT} file is missing for valid date ${VDATE}${vhr}. METplus will not run." > mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO
         fi

      fi	

   done

done

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


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

if [ ${MODELNAME} = rrfs ]; then

   fhr_min=1
   fhr_max=60
   fhr_inc=1

   export COMINfcst=${COMINrrfs}
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
   export IDATE=`$NDATE -$fhr ${VDATE}${cyc} | cut -c 1-8`
   export INIT_HR=`$NDATE -$fhr ${VDATE}${cyc} | cut -c 9-10`

   # Define forecast filename for each model 
   if [ ${MODELNAME} = rrfs ]; then
      export conus_file=${modsys}.${IDATE}/${INIT_HR}/${modsys}.t${INIT_HR}z.prslev.f$(printf "%03d" $fhr).conus_3km.grib2
   fi

   # Check for the existence of each forecast file 
   if [ -s $COMINfcst/${conus_file} ]; then
      echo $fhr >> $DATA/conus_fcst_list
      nfcst_conus=$((nfcst_conus+1))
      conus_fcst_found=1

   else
      echo "Missing file(s) is $COMINfcst/${conus_file}" >> $DATA/missing_fcst_list

   fi

   # Check for the existence of each forecast file 
#  if [ -s $COMINfcst/${ak_file} ]; then
#     echo $fhr >> $DATA/ak_fcst_list
#     nfcst_ak=$((nfcst_ak+1))
#     ak_fcst_found=1

#  else
#     echo "Missing file(s) is $COMINfcst/${ak_file}" >> $DATA/missing_fcst_list

#  fi

   fhr=$((fhr+$fhr_inc))

done


# Send missing data alert if any forecast files are missing
#if [ -s $DATA/missing_fcst_list ]; then
#if [ $nfcst_ak = 0 ] || [ $nfcst_conus = 0 ]; then
if [ $nfcst_conus = 0 ]; then
   export subject="${MODELNAME} Data Missing for EVS ${COMPONENT}"
   echo "Warning: ${MODELNAME} forecast file(s) is missing for valid date ${VDATE}${cyc}. METplus will not run." > mailmsg
   echo -e "`cat $DATA/missing_fcst_list`" >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $maillist

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

if [ $cyc = 23 ]; then

   if [ "$(ls -A $COMOUTsmall)" ]; then

      run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/StatAnalysis_fcstCAM_obsMRMS_gatherByDay.conf
      export err=$?; err_chk

      # Copy output to $COMOUTfinal
      if [ $SENDCOM = YES ]; then
         mkdir -p $COMOUTfinal
         for FILE in $DATA/stat_analysis/*; do
            cp -v $FILE $COMOUTfinal
         done
      fi

   else
      echo "Missing stat output for ${VDATE}12. METplus will not run."

   fi

fi


exit


#!/bin/bash

###############################################################################
# Name of Script: evs_href_stats_radar.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script runs METplus to generate radar
#                    verification statistics for HREF.
# History Log:
# 04/28/2023: Initial script assembled by Logan Dawson
###############################################################################


set -x


export DOMAIN=$1
export RADAR_FIELD=$2
export ENSPROD=$3


###################################################################
# Set some additional variables
###################################################################

if [ $DOMAIN = conus ]; then

   export DOM=$DOMAIN
   export VERIF_GRID=G227
   export NBR_WIDTH=17

   export MASK_POLY_LIST=$FIXevs/masks/Bukovsky_${VERIF_GRID}_CONUS.nc

   if [ $RADAR_FIELD = REFC ]; then
      MRMS_PRODUCT=MergedReflectivityQCComposite
      export OBS_VAR=MergedReflectivityQCComposite
   elif [ $RADAR_FIELD = RETOP ]; then
      MRMS_PRODUCT=EchoTop18
   elif [ $RADAR_FIELD = REFD1 ]; then
      MRMS_PRODUCT=SeamlessHSR
   fi

elif [ $DOMAIN = alaska ]; then

   export DOM=ak
   export VERIF_GRID=G091
   export NBR_WIDTH=27

   export MASK_POLY_LIST=$FIXevs/masks/Alaska_${VERIF_GRID}.nc

   if [ $RADAR_FIELD = REFC ]; then
      MRMS_PRODUCT=MergedReflectivityQComposite
      export OBS_VAR=MergedReflectivityQComposite
   fi

fi


if [ $ENSPROD = pmmn ]; then
   OBS_FILES="00.50"

elif [ $ENSPROD = prob ]; then
   OBS_FILES="ENS_FREQ Prob"

fi


############################################################
# Update Mask List and Include SPC OLTKs if Valid
# Mask Files Exist in COMINspcotlk
# Only for CONUS verification
############################################################

if [ $DOMAIN = conus ]; then

   export ADD_CONUS_REGIONS=True
   export ADD_CONUS_SUBREGIONS=False

   python $USHevs/${COMPONENT}/evs_stats_check_otlk.py
   export err=$?; err_chk

   if [ -s $DATA/mask_list ]; then
      export MASK_POLY_LIST=`cat $DATA/mask_list`
   fi

fi


###################################################################
# Check for forecast files to process
####################################################################

export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/ensprod/${modsys}.t{init?fmt=%2H}z.${DOM}.${ENSPROD}.f{lead?fmt=%2H}.grib2

nfcst=0
nfcst=0

fhr=$fhr_min

# Loop over the available 24-h periods for each model
while [ $fhr -le $fhr_max ]; do

   export fhr

   # Define initialization date/cycle for each forecast lead
   export IDATE=`$NDATE -$fhr ${VDATE}${cyc} | cut -c 1-8`
   export INIT_HR=`$NDATE -$fhr ${VDATE}${cyc} | cut -c 9-10`

   # Define forecast filename 
   export fcst_file=${modsys}.${IDATE}/ensprod/${modsys}.t${INIT_HR}z.${DOM}.${ENSPROD}.f$(printf "%02d" $fhr).grib2

   # Check for the existence of each forecast file 
   if [ -s $COMINfcst/${fcst_file} ]; then
      echo $fhr >> $DATA/${DOM}_${ENSPROD}_fcst_list
      nfcst=$((nfcst+1))

   else
      echo "Missing file(s) is $COMINfcst/${conus_file}" >> $DATA/missing_fcst_list

   fi

   fhr=$((fhr+$fhr_inc))

done


# Send missing data alert if any forecast files are missing
#if [ -s $DATA/missing_fcst_list ]; then
if [ $nfcst = 0 ]; then
   export subject="${MODELNAME} Data Missing for EVS ${COMPONENT}"
   echo "Warning: ${MODELNAME} forecast file(s) is missing for valid date ${VDATE}${cyc}. METplus will not run." > mailmsg
   echo -e `cat $DATA/missing_fcst_list` >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $maillist

# Or proceed with running METplus
else

   export nfcst_ak
   export nfcst_conus

   export ak_fhrs=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/ak_fcst_list`
   export conus_fhrs=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/conus_fcst_list`


fi






############################################################
# Check for obs files to process
############################################################

obs_file_found=0
   
export obs_file=mrms.${VDATE}/${DOMAIN}/${MRMS_PRODUCT}_${VDATE}-${cyc}0000.${VERIF_GRID}.nc
export OBS_INPUT_TEMPLATE=mrms.{valid?fmt=%Y%m%d}/${DOMAIN}/${MRMS_PRODUCT}_{valid?fmt=%Y%m%d}-{valid?fmt=%H}0000.${VERIF_GRID}.nc

if [ -s $COMINmrms/${obs_file} ]; then
   obs_found=1

else
   export subject="MRMS Prep Data Missing for EVS ${COMPONENT}"
   echo "Warning: The MRMS ${MRMS_PRODUCT} file is missing for valid date ${VDATE}${cyc}. METplus will not run." > mailmsg
   echo "Missing file is $COMINmrms/${obs_file}" >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $maillist

fi



######################################################################
# Run METplus (GridStat) if the forecast and observation files exist
######################################################################
 
if [ $nfcst > 0 ] && [ $obs_found = 1 ]; then

   run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/GridStat_fcstCAM_obsMRMS_${RADAR_FIELD}.conf
   export err=$?; err_chk

   # Copy output to $COMOUTsmall
   if [ $SENDCOM = YES ]; then
      for FILE in $DATA/grid_stat/*; do
         cp -v $FILE $COMOUTsmall
      done
   fi

else
   echo "Missing fcst or obs file(s) for ${VDATE}${cyc}. METplus will not run."

fi


exit

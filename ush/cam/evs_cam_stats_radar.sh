#!/bin/bash

##################################################################################
# Name of Script: evs_cam_stats_radar.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script runs METplus to generate radar
#                    verification statistics for deterministic and ensemble CAMs.
# History Log:
# 04/28/2023: Initial script assembled by Logan Dawson
##################################################################################


set -x

export DOMAIN=$1
export RADAR_FIELD=$2
export PROD=$3
export JOBNUM=$4


###################################################################
# Set some domain-specific variables
###################################################################

if [ $DOMAIN = conus ]; then

   export DOM=$DOMAIN
   export VERIF_GRID=G227
   export NBR_WIDTH=17

   if [ $RADAR_FIELD = REFC ]; then
      MRMS_PRODUCT=MergedReflectivityQCComposite
      export OBS_VAR=MergedReflectivityQCComposite
   elif [ $RADAR_FIELD = RETOP ]; then
      MRMS_PRODUCT=EchoTop18
   elif [ $RADAR_FIELD = REFD1 ]; then
      MRMS_PRODUCT=SeamlessHSR
   fi

   if [ -s $DATA/mask_list ]; then
      export MASK_POLY_LIST=`cat $DATA/mask_list`
   else
      export MASK_POLY_LIST=$FIXevs/masks/Bukovsky_${VERIF_GRID}_CONUS.nc
   fi

elif [ $DOMAIN = alaska ]; then

   export DOM=ak
   export VERIF_GRID=G091
   export NBR_WIDTH=27

   if [ $RADAR_FIELD = REFC ]; then
      MRMS_PRODUCT=MergedReflectivityQComposite
      export OBS_VAR=MergedReflectivityQComposite
   fi

   export MASK_POLY_LIST=$FIXevs/masks/Alaska_${VERIF_GRID}.nc

fi


###################################################################
# Set some model-specific variables
###################################################################

if [ ${MODELNAME} = hireswarw ]; then

   fhr_min=1
   fhr_max=48
   fhr_inc=1

   export COMINfcst=${COMINhiresw}
   export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/${modsys}.t{init?fmt=%2H}z.arw_5km.f{lead?fmt=%2H}.${DOM}.grib2

elif [ ${MODELNAME} = hireswarwmem2 ]; then

   fhr_min=1
   fhr_max=48
   fhr_inc=1

   export COMINfcst=${COMINhiresw}
   export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/${modsys}.t{init?fmt=%2H}z.arw_5km.f{lead?fmt=%2H}.${DOM}mem2.grib2

elif [ ${MODELNAME} = hireswfv3 ]; then

   fhr_min=1
   fhr_max=60
   fhr_inc=1

   export COMINfcst=${COMINhiresw}
   export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/${modsys}.t{init?fmt=%2H}z.fv3_5km.f{lead?fmt=%2H}.${DOM}.grib2

elif [ ${MODELNAME} = href ]; then

   if [ $PROD = pmmn ]; then
      export ENSPROD=pmmn
   elif [ $PROD = ppf ] || [ $PROD = prob ]; then
      export ENSPROD=prob
   fi

   fhr_min=1
   fhr_max=48
   fhr_inc=1

   export COMINfcst=${COMINhref}
   export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/ensprod/${modsys}.t{init?fmt=%2H}z.${DOM}.${ENSPROD}.f{lead?fmt=%2H}.grib2

elif [ ${MODELNAME} = hrrr ]; then

   fhr_min=0
   fhr_max=48
   fhr_inc=1

   export COMINfcst=${COMINhrrr}
   if [ $DOMAIN = alaska ]; then
      export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/${DOMAIN}/${modsys}.t{init?fmt=%2H}z.wrfprsf{lead?fmt=%2H}.${DOM}.grib2
   elif [ $DOMAIN = conus ]; then
      export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/${DOMAIN}/${modsys}.t{init?fmt=%2H}z.wrfprsf{lead?fmt=%2H}.grib2
   fi

elif [ ${MODELNAME} = namnest ]; then

   fhr_min=0
   fhr_max=60
   fhr_inc=1

   export COMINfcst=${COMINnam}
   export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/${modsys}.t{init?fmt=%2H}z.${DOMAIN}nest.hiresf{lead?fmt=%2H}.tm00.grib2

elif [ ${MODELNAME} = rrfs ]; then

   fhr_min=0
   fhr_max=60
   fhr_inc=1

   export COMINfcst=${COMINrrfs}
   export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/{init?fmt=%H}/${modsys}.t{init?fmt=%2H}z.prslev.f{lead?fmt=%3H}.conus_3km.grib2

fi


###################################################################
# Check for forecast files to process
####################################################################

nfcst=0

fhr=$fhr_min

# Loop over the available 24-h periods for each model
while [ $fhr -le $fhr_max ]; do

   export fhr

   # Define initialization date/cycle for each forecast lead
   export IDATE=`$NDATE -$fhr ${VDATE}${cyc} | cut -c 1-8`
   export INIT_HR=`$NDATE -$fhr ${VDATE}${cyc} | cut -c 9-10`

   # Define forecast filename for each model 
   if [ ${MODELNAME} = hireswarw ]; then
      export fcst_file=${modsys}.${IDATE}/${modsys}.t${INIT_HR}z.arw_5km.f$(printf "%02d" $fhr).${DOM}.grib2
   elif [ ${MODELNAME} = hireswarwmem2 ]; then
      export fcst_file=${modsys}.${IDATE}/${modsys}.t${INIT_HR}z.arw_5km.f$(printf "%02d" $fhr).${DOM}mem2.grib2
   elif [ ${MODELNAME} = hireswfv3 ]; then
      export fcst_file=${modsys}.${IDATE}/${modsys}.t${INIT_HR}z.fv3_5km.f$(printf "%02d" $fhr).${DOM}.grib2
   elif [ ${MODELNAME} = href ]; then
      export fcst_file=${modsys}.${IDATE}/ensprod/${modsys}.t${INIT_HR}z.${DOM}.${ENSPROD}.f$(printf "%02d" $fhr).grib2
   elif [ ${MODELNAME} = hrrr ]; then
      if [ $DOMAIN = alaska ]; then
         export fcst_file=${modsys}.${IDATE}/${DOMAIN}/${modsys}.t${INIT_HR}z.wrfprsf$(printf "%02d" $fhr).${DOM}.grib2
      elif [ $DOMAIN = conus ]; then
         export fcst_file=${modsys}.${IDATE}/${DOMAIN}/${modsys}.t${INIT_HR}z.wrfprsf$(printf "%02d" $fhr).grib2
      fi
   elif [ ${MODELNAME} = namnest ]; then
      export fcst_file=${modsys}.${IDATE}/${modsys}.t${INIT_HR}z.${DOMAIN}nest.hiresf$(printf "%02d" $fhr).tm00.grib2
   elif [ ${MODELNAME} = rrfs ]; then
      export fcst_file=${modsys}.${IDATE}/${INIT_HR}/${modsys}.t${INIT_HR}z.prslev.f$(printf "%03d" $fhr).conus_3km.grib2
   fi

   # Check for the existence of each forecast file 
   if [ -s $COMINfcst/${fcst_file} ]; then
      echo $fhr >> $DATA/job${JOBNUM}_fcst_list
      nfcst=$((nfcst+1))

   else
      echo "Missing file is $COMINfcst/${fcst_file}\n" >> $DATA/job${JOBNUM}_missing_fcst_list

   fi

   fhr=$((fhr+$fhr_inc))

done


# Send missing data alert if any forecast files are missing
#if [ -s $DATA/job${JOBNUM}_missing_fcst_list ]; then
if [ $nfcst = 0 ]; then
   export subject="${DOM} ${MODELNAME} Data Missing for EVS ${COMPONENT}"
   echo "Warning: ${DOM} ${MODELNAME} forecast files are missing for valid date ${VDATE}${cyc}. METplus will not run." > mailmsg
   echo -e "`cat $DATA/job${JOBNUM}_missing_fcst_list`" >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $maillist

fi


############################################################
# Check for obs files to process
############################################################

obs_file_found=0
  
if [ $PROD = ppf ]; then
   OBS_PROD="Prob"
elif [ $PROD = prob ]; then
   OBS_PROD="ENS_FREQ"
else
   OBS_PROD="00.50"
fi


export obs_file=mrms.${VDATE}/${DOMAIN}/${MRMS_PRODUCT}_${OBS_PROD}_${VDATE}-${cyc}0000.${VERIF_GRID}.nc
export OBS_INPUT_TEMPLATE=mrms.{valid?fmt=%Y%m%d}/${DOMAIN}/${MRMS_PRODUCT}_${OBS_PROD}_{valid?fmt=%Y%m%d}-{valid?fmt=%H}0000.${VERIF_GRID}.nc

if [ -s $COMINmrms/${obs_file} ]; then
   obs_found=1

else
   export subject="MRMS Prep Data Missing for EVS ${COMPONENT}"
   echo "Warning: The MRMS ${MRMS_PRODUCT} file is missing for valid date ${VDATE}${cyc}. METplus will not run." > mailmsg
   echo "Missing file is $COMINmrms/${obs_file}" >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $maillist

fi


#########################################################################
# Run METplus (GridStat or EnsembleStat) if the fcst and obs files exist
#########################################################################

if [ $nfcst -ge 1 ] && [ $obs_found = 1 ]; then

   export fhrs=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/job${JOBNUM}_fcst_list`

   if [ $PROD = det ] || [ $PROD = pmmn ]; then

      if [ $MODELNAME = href ]; then
         export MODEL=${MODELNAME}_pmmn
      else
         export MODEL=${MODELNAME}
      fi

      run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/GridStat_fcstCAM_obsMRMS_${RADAR_FIELD}.conf
      export err=$?; err_chk

   elif [ $PROD = ens ]; then

      export MODEL=${MODELNAME}

      run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/EnsembleStat_fcstHREF_obsMRMS_${RADAR_FIELD}.conf
      export err=$?; err_chk

   elif [ $PROD = ppf ]; then

      export MODEL=${MODELNAME}_prob

      run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/GridStat_fcstHREFPPF_obsMRMS_${RADAR_FIELD}.conf
      export err=$?; err_chk

   elif [ $PROD = prob ]; then

      export MODEL=${MODELNAME}_prob

      run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/GridStat_fcstHREFPROB_obsMRMS_${RADAR_FIELD}.conf
      export err=$?; err_chk

   fi

else
   echo "Missing fcst or obs file(s) for ${VDATE}${cyc}. METplus will not run."

fi


exit

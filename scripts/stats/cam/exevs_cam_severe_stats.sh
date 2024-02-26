#!/bin/bash
###############################################################################
# Name of Script: exevs_cam_severe_stats.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script runs METplus to generate severe 
#                    verification statistics for HREF and deterministic CAMs.
# History Log:
# 04/20/2023: Initial script assembled by Logan Dawson
###############################################################################


set -x

echo
echo " ENTERING SUB SCRIPT $0 "
echo

set -x
export machine=${machine:-"WCOSS2"}


############################################################
# Check for obs files to process
############################################################

obs_lsr_found=0
obs_ppf_found=0

export obs_lsr_file=spc_lsr.${REP_DATE}/spc.lsr.${REP_DATE}12_${VDATE}12.G211.nc
export obs_ppf_file=spc_lsr.${REP_DATE}/spc.ppf.${REP_DATE}12_${VDATE}12.G211.nc

if [ -s $EVSINspclsr/${obs_lsr_file} ]; then
   obs_lsr_found=1

else
   if [ $SENDMAIL = YES ]; then
      export subject="SPC LSR Prep Data Missing for EVS ${COMPONENT}"
      echo "Warning: The ${REP_DATE} SPC LSR file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
      echo "Missing file is $EVSINspclsr/${obs_lsr_file}" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $MAILTO
   else
      echo "WARNING: The ${REP_DATE} SPC LSR file is missing for valid date ${VDATE}. METplus will not run."
   fi

fi

if [ -s $EVSINspclsr/${obs_ppf_file} ]; then
   obs_ppf_found=1

else
   if [ $SENDMAIL = YES ]; then
      export subject="SPC LSR Prep Data Missing for EVS ${COMPONENT}"
      echo "Warning: The ${REP_DATE} SPC PPF file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
      echo "Missing file is $EVSINspclsr/${obs_ppf_file}" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $MAILTO
   else
      echo "WARNING: The ${REP_DATE} SPC PPF file is missing for valid date ${VDATE}. METplus will not run."
   fi

fi


############################################################
# Define Mask List and Include SPC OLTKs if Valid
# Mask Files Exist in EVSINspcotlk
############################################################

export VERIF_GRID=G211
export ADD_CONUS_REGIONS=False
export ADD_CONUS_SUBREGIONS=False

python $USHevs/${COMPONENT}/evs_cam_stats_check_otlk.py
export err=$?; err_chk

if [ -s $DATA/mask_list ]; then
   export MASK_POLY_LIST=`cat $DATA/mask_list`
else
   export MASK_POLY_LIST=$FIXevs/masks/Bukovsky_${VERIF_GRID}_CONUS.nc
fi


###################################################################
# Set some model-specific variables
####################################################################

if [ ${MODELNAME} = hireswarw ] || [ ${MODELNAME} = hireswarwmem2 ] || [ ${MODELNAME} = href ]; then
   fhr_min=24
   fhr_max=48
   fhr_inc=12

elif [ ${MODELNAME} = hireswfv3 ]; then
   fhr_min=24
   fhr_max=60
   fhr_inc=12

elif [ ${MODELNAME} = hrrr ]; then
   fhr_min=24
   fhr_max=48
   fhr_inc=6

elif [ ${MODELNAME} = namnest ] || [ ${MODELNAME} = rrfs ] || [ ${MODELNAME} = refs ]; then
   fhr_min=24
   fhr_max=60
   fhr_inc=6

fi


###################################################################
# Check for forecast files to process
####################################################################

nfcst=0

fhr=$fhr_min


# Loop over the available 24-h periods for each model
while [ $fhr -le $fhr_max ]; do

   export fhr

   # Define accumulation begin/end time
   export ACCUM_BEG=${REP_DATE}12
   export ACCUM_END=${VDATE}12
   export IDATE=`$NDATE -$fhr ${VDATE}12 | cut -c 1-8`
   export INIT_HR=`$NDATE -$fhr ${VDATE}12 | cut -c 9-10`

   export fcst_file=${modsys}.${IDATE}/${MODELNAME}.t${INIT_HR}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr}.nc
   export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/${MODELNAME}.t{init?fmt=%2H}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f{lead?fmt=%2H}.nc

   if [ -s $EVSINfcst/${fcst_file} ]; then
      echo $fhr >> $DATA/fcst_list
      nfcst=$((nfcst+1))
      fcst_found=1

   else
      echo "WARNING: Missing file is $EVSINfcst/${fcst_file}\n" >> $DATA/missing_fcst_list

   fi

   fhr=$((fhr+$fhr_inc))

done


# Send missing data alert if any forecast files are missing
if [ -s $DATA/missing_fcst_list ]; then
   if [ $SENDMAIL = YES ]; then
      export subject="${MODELNAME} SSPF Prep Data Missing for EVS ${COMPONENT}"
      echo "Warning: ${MODELNAME} SSPF forecast file(s) is missing for valid date ${VDATE}12. METplus will not run." > mailmsg
      echo -e "`cat $DATA/missing_fcst_list`" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $MAILTO
   fi

fi


######################################################################
# Run METplus (GridStat) if the forecast and observation files exist
######################################################################
 
if [ $nfcst -ge 1 ] && [ $obs_lsr_found = 1 ]; then

   export fhrs=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/fcst_list`

   run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/GridStat_fcstSSPF_obsLSR.conf
   export err=$?; err_chk

else
   echo "Missing fcst or LSR obs file(s) for ${VDATE}12. METplus will not run."

fi


######################################################################
# Run METplus (GridStat) if the forecast and observation files exist
######################################################################

if [ $nfcst -ge 1 ] && [ $obs_ppf_found = 1 ]; then

   export fhrs=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/fcst_list`

   run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/GridStat_fcstSSPF_obsPPF.conf
   export err=$?; err_chk

else
   echo "Missing fcst or LSR obs file(s) for ${VDATE}12. METplus will not run."

fi


###################################################################
# Run METplus (StatAnalysis) if GridStat output exists
###################################################################

if [ -d $DATA/grid_stat ]; then

   if [ "$(ls -A $DATA/grid_stat)" ]; then

      run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstSSPF_obsLSR_gatherByDay.conf
      export err=$?; err_chk

      # Copy output to $COMOUT
      if [ $SENDCOM = YES ]; then
         mkdir -p $COMOUTfinal
         for FILE in $DATA/stat_analysis/*; do
            if [ -s "$FILE" ]; then
               cp -v $FILE $COMOUTfinal
            fi
         done
      fi

   else
      echo "Missing stat output for ${VDATE}12. METplus will not run."

   fi

else
   echo "Missing stat output for ${VDATE}12. METplus will not run."

fi

# Cat the METplus log files
log_dir="$DATA/logs"
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


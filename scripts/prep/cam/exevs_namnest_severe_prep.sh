#!/bin/bash
###############################################################################
# Name of Script: exevs_namnest_severe_prep.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script preprocesses NAM Nest UH data for 
#                    CAM severe verification.
# History Log:
# 3/2023: Initial script assembled by Logan Dawson 
###############################################################################


set -x

echo 
echo " ENTERING SUB SCRIPT $0 "
echo

set -x


############################################################
# Define surrogate severe settings
############################################################

export machine=${machine:-"WCOSS2"}
export VERIF_GRID=G211
export VERIF_GRID_DX=81.271
export GAUSS_RAD=120


############################################################
# Set some model-specific environment variables 
############################################################

export MODEL_INPUT_DIR=${COMINnam}
export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/${modsys}.t{init?fmt=%2H}z.conusnest.hiresf{lead?fmt=%2H}.tm00.grib2


export MXUPHL25_THRESH1=100.0


if [ $vhr -eq 00 ];then
   nloop=2
   fhr_beg1=12
   fhr_end1=36
   fhr_beg2=36
   fhr_end2=60

elif [ $vhr -eq 06 ]; then
   nloop=2
   fhr_beg1=6
   fhr_end1=30
   fhr_beg2=30
   fhr_end2=54

elif [ $vhr -eq 12 ]; then
   nloop=2
   fhr_beg1=0
   fhr_end1=24
   fhr_beg2=24
   fhr_end2=48

elif [ $vhr -eq 18 ]; then
   nloop=1
   fhr_beg1=18
   fhr_end1=42

else
   err_exit "Current vhr is unsupported"

fi


###################################################################
# Check for forecast files to process
###################################################################
k=0
min_file_req=24

# Do one or more loops depending on number of 24-h periods
while [ $k -lt $nloop ]; do

nfiles=0
i=1

   if [ $k -eq 0 ]; then
      fhr=$fhr_beg1
      fhr_end=$fhr_end1
   elif [ $k -eq 1 ]; then
      fhr=$fhr_beg2
      fhr_end=$fhr_end2
   fi
   export fhr
   export fhr_end

   # Define accumulation begin/end time
   export ACCUM_BEG=${ACCUM_BEG:-`$NDATE $fhr ${IDATE}${vhr}`}
   export ACCUM_END=${ACCUM_END:-`$NDATE $fhr_end ${IDATE}${vhr}`}

   # Increment fhr by 1 at the start of loop for each 24-h period
   # Correctly skips initial file (F00, F12, F24) that doesn't include necessary data
   if [ $i -eq 1 ]; then
      fhr=$((fhr+1))
   fi

   # Search for required forecast files
   while [ $i -le $min_file_req ]; do

      export fcst_file=${MODEL_INPUT_DIR}/${modsys}.${IDATE}/${modsys}.t${vhr}z.conusnest.hiresf$(printf "%02d" $fhr).tm00.grib2

      if [ -s $fcst_file ]; then
         echo "File number $i found"
         nfiles=$((nfiles+1))
      else
         echo "WARNING: $fcst_file is missing"
      fi
   
      fhr=$((fhr+1))
      i=$((i+1))

   done


   ###################################################################
   # Run METplus if all forecast files exist or exit gracefully
   ###################################################################

   if [ $nfiles -eq $min_file_req ]; then

      echo "Found all $nfiles forecast files. Generating ${MODELNAME} SSPF for ${vhr}Z ${IDATE} cycle at F${fhr_end}"

      ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/GenEnsProd_fcstCAM_MXUPHL_SurrogateSevere.conf
      export err=$?; err_chk

      # Copy final output to $COMOUT
      if [ $SENDCOM = YES ]; then
         mkdir -p $COMOUT/${modsys}.${IDATE}
         for FILE in $DATA/pcp_combine/${modsys}.${IDATE}/*; do
            if [ -s "$FILE" ]; then
               cp -v $FILE $COMOUT/${modsys}.${IDATE}
            fi
         done
         for FILE in $DATA/sspf/${modsys}.${IDATE}/*; do
            if [ -s "$FILE" ]; then
               cp -v $FILE $COMOUT/${modsys}.${IDATE}
            fi
         done
      fi


   else

      echo "WARNING: Only $nfiles ${MODELNAME} forecast files found for ${vhr}Z ${IDATE} cycle. $min_file_req files are required."
      if [ $SENDMAIL = YES ]; then
         export subject="${MODELNAME} Forecast Data Missing for EVS ${COMPONENT}"
         echo "WARNING: Only $nfiles ${MODELNAME} forecast files found for ${vhr}Z ${IDATE} cycle. $min_file_req files are required. METplus will not run." > mailmsg
         echo "Job ID: $jobid" >> mailmsg
         cat mailmsg | mail -s "$subject" $MAILTO
      fi

   fi


   k=$((k+1))

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

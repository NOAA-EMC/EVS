#!/bin/bash
###############################################################################
# Name of Script: evs_rrfs_severe_prep.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script preprocesses RRFS UH data for 
#                    CAM severe verification.
# History Log:
# 5/1/2023: Script assembled by Logan Dawson to handle all ensemble data
###############################################################################


set -x

export MEMNUM=$1
export JOBNUM=$2


############################################################
# Set some model-specific environment variables 
############################################################

export MODEL_INPUT_DIR=${COMINrrfs}

if [ $MEMNUM = ctl ]; then
   export MODEL_INPUT_TEMPLATE=rrfs.{init?fmt=%Y%m%d}/{init?fmt=%2H}/${MODELNAME}.t{init?fmt=%2H}z.prslev.f{lead?fmt=%3H}.conus_3km.grib2
else
   export MODEL_INPUT_TEMPLATE=refs.{init?fmt=%Y%m%d}/{init?fmt=%2H}/${MEMNUM}/${MODELNAME}.t{init?fmt=%2H}z.prslev.f{lead?fmt=%3H}.conus_3km.grib2
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
   export ACCUM_BEG=${ACCUM_BEG:-`$NDATE $fhr ${IDATE}${cyc}`}
   export ACCUM_END=${ACCUM_END:-`$NDATE $fhr_end ${IDATE}${cyc}`}

   # Increment fhr by 1 at the start of loop for each 24-h period
   # Correctly skips initial file (F00, F12, F24) that doesn't include necessary data
   if [ $i -eq 1 ]; then
      fhr=$((fhr+1))
   fi

   # Search for required forecast files
   while [ $i -le $min_file_req ]; do

      if [ $MEMNUM = ctl ]; then
         export fcst_file=rrfs.${IDATE}/${cyc}/${MODELNAME}.t${cyc}z.prslev.f$(printf "%03d" $fhr).conus_3km.grib2
      else
         export fcst_file=refs.${IDATE}/${cyc}/${MEMNUM}/${MODELNAME}.t${cyc}z.prslev.f$(printf "%03d" $fhr).conus_3km.grib2
      fi

      if [ -s ${MODEL_INPUT_DIR}/$fcst_file ]; then
         echo "File number $i found"
         nfiles=$((nfiles+1))
      else
         echo "$fcst_file is missing"
      fi
   
      fhr=$((fhr+1))
      i=$((i+1))

   done


   ###################################################################
   # Run METplus if all forecast files exist or exit gracefully
   ###################################################################

   if [ $nfiles -eq $min_file_req ]; then

      echo "Found all $nfiles forecast files. Generating ${MODELNAME} SSPF for ${cyc}Z ${IDATE} cycle at F${fhr_end}"

      ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/GenEnsProd_fcstRRFS_MXUPHL_SurrogateSevere.conf
      export err=$?; err_chk

   else

      export subject="${MODELNAME} ${MEMNUM} Forecast Data Missing for EVS ${COMPONENT}"
      echo "Warning: Only $nfiles ${MODELNAME} ${MEMNUM} forecast files found for ${cyc}Z ${IDATE} cycle. $min_file_req files are required. METplus will not run." > mailmsg${JOBNUM}
      echo "Job ID: $jobid" >> mailmsg${JOBNUM}
      cat mailmsg${JOBNUM} | mail -s "$subject" $maillist

   fi


   k=$((k+1))

done



exit

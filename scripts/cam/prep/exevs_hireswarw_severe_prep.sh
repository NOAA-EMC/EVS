#!/bin/bash
###############################################################################
# Name of Script: exevs_hireswarw_severe_prep.sh
# Contact(s):     Logan Dawson
# Purpose of Script: This script preprocesses HiResW ARW UH data for 
#                    CAM severe verification.
# History Log:
# 3/2023: Initial script assembled by Logan Dawson 
###############################################################################


set +x

echo 
echo " ENTERING SUB SCRIPT $0 "
echo

set -x



############################################################
# Set some model-specific environment variables 
############################################################

export COMINfcst=${COMINhiresw}
export MODEL_INPUT_TEMPLATE=${modsys}.{init?fmt=%Y%m%d}/${modsys}.t{init?fmt=%2H}z.arw_5km.f{lead?fmt=%2H}.conus.grib2

export MXUPHL25_THRESH1=75.0


############################################################
# Define surrogate severe settings
############################################################

export VERIF_GRID=G211
export VERIF_GRID_DX=81.271
export GAUSS_RAD=120


############################################################
# Set some model-specific environment variables 
############################################################
export ACCUM_BEG=${ACCUM_BEG:-$PDYm1}12
export ACCUM_END=${ACCUM_END:-$PDY}12

if [ $cyc -eq 00 ];then
   nloop=1
   fhr_beg1=13
   fhr_end1=36

elif [ $cyc -eq 12 ]; then
   nloop=2
   fhr_beg=1
   fhr_end1=24
   fhr_beg2=25
   fhr_end2=48

fi


###################################################################
# Check for forecast files to process
###################################################################
k=0
fhr=$fhr_beg


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


   while [ $i -le 24 ]; do

      export fcst_file=$COMINfcst/${modsys}.${IDATE}/${modsys}.t${cyc}z.arw_5km.f$(printf "%02d" $fhr).conus.grib2

      if [ -e $fcst_file ]; then
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

   if [ $nfiles -eq 24 ]; then

      echo "Found all files. Generating ${MODELNAME} SSPF for ${cyc}Z ${IDATE} cycle at F${fhr_end}"
      ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/GenEnsProd_fcstCAM_MXUPHL_SurrogateSevere.conf
      export err=$?; err_chk

   else

      export subject="${MODELNAME} data missing for ${cyc}Z ${IDATE} cycle"
      export maillist=${maillist:-'logan.dawson@noaa.gov'}
      echo "Warning: Some ${MODELNAME} files are missing from ${cyc}Z ${IDATE} cycle. Only ${nfiles} files found. METplus will not run.">>mailmsg
      echo "Job ID: $jobid">>mailmsg
      cat mailmsg | mail -s "$subject" $maillist

   fi

   k=$((k+1))

done


if [ $SENDCOM = YES ]; then
   mkdir -p $COMOUT/${modsys}.${IDATE}
   for FILE in $DATA/pcp_combine/${modsys}.${IDATE}/*; do
      cp -v $FILE $COMOUT/${modsys}.${IDATE}
   done
   for FILE in $DATA/sspf/${modsys}.${IDATE}/*; do
      cp -v $FILE $COMOUT/${modsys}.${IDATE}
   done
fi


exit


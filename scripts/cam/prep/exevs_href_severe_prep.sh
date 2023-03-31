#!/bin/bash
###############################################################################
# Name of Script: exevs_href_severe_prep.sh
# Contact(s):     Logan Dawson
# Purpose of Script: This script preprocesses HREF SSPFs for 
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

export ACCUM_BEG=${ACCUM_BEG:-$PDYm1}12
export ACCUM_END=${ACCUM_END:-$PDY}12

export COMINfcst=${DATA}/mem_files
mkdir -p ${COMINfcst}

export COMINmem1=${COMOUT}/hiresw.${PDYm1}
export COMINmem2=${COMOUT}/hiresw.${PDYm1}
export COMINmem3=${COMOUT}/hiresw.${PDYm1}
export COMINmem4=${COMOUT}/hrrr.${PDYm1}
export COMINmem5=${COMOUT}/nam.${PDYm1}


# Define settings for 00Z HREF time-lagged members
if [ $cyc -eq 00 ];then

   nloop=1

   export COMINmem6=${COMOUT}/hiresw.${PDYm2}
   export COMINmem7=${COMOUT}/hiresw.${PDYm2}
   export COMINmem8=${COMOUT}/hiresw.${PDYm2}
   export COMINmem9=${COMOUT}/hrrr.${PDYm2}
   export COMINmem10=${COMOUT}/nam.${PDYm2}

   export cyc_lag6=18
   export cyc_lag12=12

   fhr_end=36
   fhr_end1_lag6=42
   fhr_end1_lag12=48

# Define settings for 12Z HREF time-lagged members
elif [ $cyc -eq 12 ]; then

   nloop=2

   export COMINmem6=${COMOUT}/hiresw.${PDYm1}
   export COMINmem7=${COMOUT}/hiresw.${PDYm1}
   export COMINmem8=${COMOUT}/hiresw.${PDYm1}
   export COMINmem9=${COMOUT}/hrrr.${PDYm1}
   export COMINmem10=${COMOUT}/nam.${PDYm1}

   export cyc_lag6=06
   export cyc_lag12=00

   fhr_end1=24
   fhr_end1_lag6=30
   fhr_end1_lag12=36
   
   fhr_end2=48
   fhr_end2_lag6=54
   fhr_end2_lag12=60

else

   echo "The current cyc, $cyc, is not supported for $MODELNAME. Exiting"
   exit 1

fi


###################################################################
# Check for forecast files to process
###################################################################
k=0


while [ $k -lt $nloop ]; do

nfiles=0
i=1

   # Define settings for first and second 24-h periods
   # Only valid for 12Z HREF
   if [ $k -eq 0 ]; then
      export fhr_end=$fhr_end1
      export fhr_end_lag6=$fhr_end1_lag6
      export fhr_end_lag12=$fhr_end1_lag12
   elif [ $k -eq 1 ]; then
      export fhr_end=$fhr_end2
      export fhr_end_lag6=$fhr_end2_lag6
      export fhr_end_lag12=$fhr_end2_lag12
   fi


   # Loop over all members to check that they exist
   while [ $i -le 10 ]; do

      # Define path to forecast file for each member
      if [ $i -eq 1 ]; then
         export fcst_file=${COMINmem1}/hireswarw.t${cyc}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
      elif [ $i -eq 2 ]; then
         export fcst_file=${COMINmem2}/hireswarwmem2.t${cyc}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
      elif [ $i -eq 3 ]; then
         export fcst_file=${COMINmem3}/hireswfv3.t${cyc}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
      elif [ $i -eq 4 ]; then
         export fcst_file=${COMINmem4}/hrrr.t${cyc}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
      elif [ $i -eq 5 ]; then
         export fcst_file=${COMINmem5}/namnest.t${cyc}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
      elif [ $i -eq 6 ]; then
         export fcst_file=${COMINmem6}/hireswarw.t${cyc_lag12}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag12}.nc
      elif [ $i -eq 7 ]; then
         export fcst_file=${COMINmem7}/hireswarwmem2.t${cyc_lag12}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag12}.nc
      elif [ $i -eq 8 ]; then
         export fcst_file=${COMINmem8}/hireswfv3.t${cyc_lag12}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag12}.nc
      elif [ $i -eq 9 ]; then
         export fcst_file=${COMINmem9}/hrrr.t${cyc_lag6}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag6}.nc
      elif [ $i -eq 10 ]; then
         export fcst_file=${COMINmem10}/namnest.t${cyc_lag6}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag6}.nc
      fi

      # Copy the member files to working directory if they exist
      if [ -e $fcst_file ]; then
         echo "File found for member $i. Copying to working directory."
         cp -v $fcst_file $COMINfcst
         nfiles=$((nfiles+1))
      else
         echo "File not found for member $i. METplus will not run without X members available."
      fi
   
      fhr=$((fhr+1))
      i=$((i+1))

   done


   ###################################################################
   # Run METplus if all forecast files exist or exit gracefully
   ###################################################################

   if [ $nfiles -gt 7 ]; then

      echo "Found enough files to run. Generating ${MODELNAME} SSPF for ${cyc}Z ${IDATE} cycle at F${fhr_end}"
      ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/GenEnsProd_fcstHREF_MXUPHL_SurrogateSevere.conf
      export err=$?; err_chk

   else

      export subject="${MODELNAME} data missing for ${cyc}Z ${IDATE} cycle"
      export maillist=${maillist:-'logan.dawson@noaa.gov'}
      echo "Warning: More than 3 ${MODELNAME} member files are missing from ${cyc}Z ${IDATE} cycle. Only ${nfiles} member files found. METplus will not run.">>mailmsg
      echo "Job ID: $jobid">>mailmsg
      cat mailmsg | mail -s "$subject" $maillist

   fi

   k=$((k+1))

done


if [ $SENDCOM = YES ]; then
   mkdir -p $COMOUT/${modsys}.${IDATE}
   for FILE in $DATA/sspf/${modsys}.${IDATE}/*; do
      cp -v $FILE $COMOUT/${modsys}.${IDATE}
   done
fi


exit


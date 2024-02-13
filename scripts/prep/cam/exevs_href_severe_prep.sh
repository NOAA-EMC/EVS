#!/bin/bash
###############################################################################
# Name of Script: exevs_href_severe_prep.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script preprocesses HREF SSPFs for 
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
## Define surrogate severe settings
#############################################################

export machine=${machine:-"WCOSS2"}
export VERIF_GRID=G211
export VERIF_GRID_DX=81.271
export GAUSS_RAD=120


############################################################
# Set some model-specific environment variables 
############################################################

export MODEL_INPUT_DIR=${DATA}/mem_files
mkdir -p ${MODEL_INPUT_DIR}


# Define settings for 00Z HREF time-lagged members
if [ $vhr -eq 00 ];then

   nloop=1

   export IDATE_lag=${IDATE_lag:-`$NDATE -12 ${IDATE}${vhr} | cut -c 1-8`}

   export MEM1_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE}
   export MEM2_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE}
   export MEM3_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE}
   export MEM4_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hrrr.${IDATE}
   export MEM5_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/nam.${IDATE}
   export MEM6_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE_lag}
   export MEM7_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE_lag}
   export MEM8_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE_lag}
   export MEM9_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hrrr.${IDATE_lag}
   export MEM10_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/nam.${IDATE_lag}

   export cyc_lag6=18
   export cyc_lag12=12

   fhr_beg1=12
   fhr_end1=36
   fhr_end1_lag6=42
   fhr_end1_lag12=48

# Define settings for 12Z HREF time-lagged members
elif [ $vhr -eq 12 ]; then

   nloop=2

   export MEM1_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE}
   export MEM2_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE}
   export MEM3_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE}
   export MEM4_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hrrr.${IDATE}
   export MEM5_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/nam.${IDATE}
   export MEM6_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE}
   export MEM7_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE}
   export MEM8_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hiresw.${IDATE}
   export MEM9_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/hrrr.${IDATE}
   export MEM10_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/nam.${IDATE}

   export cyc_lag6=06
   export cyc_lag12=00

   fhr_beg1=00
   fhr_end1=24
   fhr_end1_lag6=30
   fhr_end1_lag12=36
   
   fhr_beg2=24
   fhr_end2=48
   fhr_end2_lag6=54
   fhr_end2_lag12=60

else

   err_exit "The current vhr, $vhr, is not supported for $MODELNAME. Exiting"

fi


###################################################################
# Check for forecast files to process
###################################################################
k=0
min_file_req=7

while [ $k -lt $nloop ]; do

nfiles=0
i=1

   # Define settings for first and second 24-h periods
   # Only valid for 12Z HREF
   if [ $k -eq 0 ]; then
      export fhr_beg=$fhr_beg1
      export fhr_end=$fhr_end1
      export fhr_end_lag6=$fhr_end1_lag6
      export fhr_end_lag12=$fhr_end1_lag12

   elif [ $k -eq 1 ]; then
      export fhr_beg=$fhr_beg2
      export fhr_end=$fhr_end2
      export fhr_end_lag6=$fhr_end2_lag6
      export fhr_end_lag12=$fhr_end2_lag12
      
   fi

   # Define accumulation begin/end time
   export ACCUM_BEG=`$NDATE $fhr_beg ${IDATE}${vhr}`
   export ACCUM_END=`$NDATE $fhr_end ${IDATE}${vhr}`


   # Loop over all members to check that they exist
   while [ $i -le 10 ]; do

      # Define path to forecast file for each member
      if [ $i -eq 1 ]; then
	 export mem1=hireswarw.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM1_INPUT_DIR}/${mem1}

      elif [ $i -eq 2 ]; then
	 export mem2=hireswarwmem2.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM2_INPUT_DIR}/${mem2}

      elif [ $i -eq 3 ]; then
	 export mem3=hireswfv3.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM3_INPUT_DIR}/${mem3}

      elif [ $i -eq 4 ]; then
	 export mem4=hrrr.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM4_INPUT_DIR}/${mem4}

      elif [ $i -eq 5 ]; then
	 export mem5=namnest.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM5_INPUT_DIR}/${mem5}

      elif [ $i -eq 6 ]; then
	 export mem6=hireswarw.t${cyc_lag12}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag12}.nc
         export fcst_file=${MEM6_INPUT_DIR}/${mem6}

      elif [ $i -eq 7 ]; then
	 export mem7=hireswarwmem2.t${cyc_lag12}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag12}.nc
         export fcst_file=${MEM7_INPUT_DIR}/${mem7}

      elif [ $i -eq 8 ]; then
	 export mem8=hireswfv3.t${cyc_lag12}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag12}.nc
         export fcst_file=${MEM8_INPUT_DIR}/${mem8}

      elif [ $i -eq 9 ]; then
	 export mem9=hrrr.t${cyc_lag6}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag6}.nc
         export fcst_file=${MEM9_INPUT_DIR}/${mem9}

      elif [ $i -eq 10 ]; then
	 export mem10=namnest.t${cyc_lag6}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag6}.nc
         export fcst_file=${MEM10_INPUT_DIR}/${mem10}

      fi

      # Copy the member files to working directory if they exist
      if [ -s $fcst_file ]; then
         echo "File found for member $i. Copying to working directory."
         cpreq -v $fcst_file ${MODEL_INPUT_DIR}
         nfiles=$((nfiles+1))
      else
         echo "Forecast file $fcst_file not found for member $i." >> missing_file_list
      fi
   
      fhr=$((fhr+1))
      i=$((i+1))

   done


   ###################################################################
   # Run METplus if all forecast files exist or exit gracefully
   ###################################################################

   if [ $nfiles -ge $min_file_req ]; then
      if [ "$nfiles" -eq "7" ]; then
         export mems="$mem1, $mem2, $mem3, $mem4, $mem5, $mem8, $mem10"
         export nmem="7"
         export ens_thresh="1.0"
      else
         export mems="$mem1, $mem2, $mem3, $mem4, $mem5, $mem6, $mem7, $mem8, $mem9, $mem10"
         export nmem="10"
         export ens_thresh="0.7"
      fi
      echo "Found $nfiles forecast files. Generating ${MODELNAME} SSPF for ${vhr}Z ${IDATE} cycle at F${fhr_end}"
      ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/GenEnsProd_fcstHREF_MXUPHL_SurrogateSevere.conf
      export err=$?; err_chk

      if [ $SENDCOM = YES ]; then
         mkdir -p $COMOUT/${modsys}.${IDATE}
         for FILE in $DATA/sspf/${modsys}.${IDATE}/*; do
            cpreq -v $FILE $COMOUT/${modsys}.${IDATE}
         done
      fi

   else

      if [ $SENDMAIL = YES ]; then
         export subject="${MODELNAME} Forecast Data Missing for EVS ${COMPONENT}"
         echo "WARNING: Only $nfiles ${MODELNAME} forecast files found for ${vhr}Z ${IDATE} cycle. At least $min_file_req files are required. METplus will not run." > mailmsg
         echo -e "`cat missing_file_list`" >> mailmsg
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


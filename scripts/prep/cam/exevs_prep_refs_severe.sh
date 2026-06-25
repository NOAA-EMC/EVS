#!/bin/bash
###############################################################################
# Name of Script: exevs_prep_refs_severe.sh
# Contact(s):     Marcel Caron (marcel.caron@noaa.gov)
# Purpose of Script: This script preprocesses REFS SSPFs for 
#                    CAM severe verification.
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


# Define settings for 00Z REFS time-lagged members
if [ $vhr -eq 00 ];then

   nloop=2

   export IDATE_lag=${IDATE_lag:-`$NDATE -12 ${INITDATE}${vhr} | cut -c 1-8`}

   export MEM1_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM2_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM3_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM4_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM5_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM6_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM7_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/hrrr
   export MEM8_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${IDATE_lag}/rrfs
   export MEM9_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${IDATE_lag}/rrfs
   export MEM10_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${IDATE_lag}/rrfs
   export MEM11_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${IDATE_lag}/rrfs
   export MEM12_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${IDATE_lag}/rrfs
   export MEM13_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${IDATE_lag}/rrfs
   export MEM14_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${IDATE_lag}/hrrr

   export cyc_lag6=18

   fhr_beg1=12
   fhr_end1=36
   fhr_end1_lag6=42

   fhr_beg2=36
   fhr_end2=60
   fhr_end2_lag6=66 # these members won't exist, but we only need 6 members

# Define settings for 06Z REFS time-lagged members
elif [ $vhr -eq 06 ]; then

   nloop=2

   export MEM1_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM2_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM3_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM4_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM5_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM6_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM7_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/hrrr
   export MEM8_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM9_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM10_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM11_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM12_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM13_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM14_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/hrrr

   export cyc_lag6=00

   fhr_beg1=06
   fhr_end1=30
   fhr_end1_lag6=36

   fhr_beg2=30
   fhr_end2=54
   fhr_end2_lag6=60
   
# Define settings for 12Z REFS time-lagged members
elif [ $vhr -eq 12 ]; then

   nloop=2

   export MEM1_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM2_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM3_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM4_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM5_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM6_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM7_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/hrrr
   export MEM8_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM9_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM10_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM11_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM12_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM13_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM14_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/hrrr

   export cyc_lag6=06

   fhr_beg1=00
   fhr_end1=24
   fhr_end1_lag6=30
   
   fhr_beg2=24
   fhr_end2=48
   fhr_end2_lag6=54

# Define settings for 18Z REFS time-lagged members
elif [ $vhr -eq 18 ]; then

   nloop=1

   export MEM1_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM2_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM3_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM4_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM5_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM6_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM7_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/hrrr
   export MEM8_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM9_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM10_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM11_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM12_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM13_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/rrfs
   export MEM14_INPUT_DIR=${COMIN}/${STEP}/${COMPONENT}/${RUN}.${INITDATE}/hrrr

   export cyc_lag6=12

   fhr_beg1=18
   fhr_end1=42
   fhr_end1_lag6=48

else

   err_exit "The current vhr, $vhr, is not supported for $MODELNAME. Exiting"

fi


###################################################################
# Check for forecast files to process
###################################################################
k=0

while [ $k -lt $nloop ]; do

nfiles=0
i=1

   # Define settings for first and second 24-h periods
   # Only valid for 12Z REFS
   if [ $k -eq 0 ]; then
      export fhr_beg=$fhr_beg1
      export fhr_end=$fhr_end1
      export fhr_end_lag6=$fhr_end1_lag6

   elif [ $k -eq 1 ]; then
      export fhr_beg=$fhr_beg2
      export fhr_end=$fhr_end2
      export fhr_end_lag6=$fhr_end2_lag6
      
   fi

   # Define accumulation begin/end time
   export ACCUM_BEG=`$NDATE $fhr_beg ${INITDATE}${vhr}`
   export ACCUM_END=`$NDATE $fhr_end ${INITDATE}${vhr}`


   # Loop over all members to check that they exist
   while [ $i -le 14 ]; do

      # Define path to forecast file for each member
      if [ $i -eq 1 ]; then
	 export mem1=rrfs.m000ctl.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM1_INPUT_DIR}/${mem1}

      elif [ $i -eq 2 ]; then
	 export mem2=rrfsmem1.m0001.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM2_INPUT_DIR}/${mem2}

      elif [ $i -eq 3 ]; then
	 export mem3=rrfsmem2.m0002.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM3_INPUT_DIR}/${mem3}

      elif [ $i -eq 4 ]; then
	 export mem4=rrfsmem3.m0003.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM4_INPUT_DIR}/${mem4}

      elif [ $i -eq 5 ]; then
	 export mem5=rrfsmem4.m0004.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM5_INPUT_DIR}/${mem5}

      elif [ $i -eq 6 ]; then
	 export mem6=rrfsmem5.m0005.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM6_INPUT_DIR}/${mem6}

      elif [ $i -eq 7 ]; then
	 export mem7=hrrr.t${vhr}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end}.nc
         export fcst_file=${MEM7_INPUT_DIR}/${mem7}

      elif [ $i -eq 8 ]; then
	 export mem8=rrfs.m000ctl.t${cyc_lag6}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag6}.nc
         export fcst_file=${MEM8_INPUT_DIR}/${mem8}

      elif [ $i -eq 9 ]; then
	 export mem9=rrfsmem1.m0001.t${cyc_lag6}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag6}.nc
         export fcst_file=${MEM9_INPUT_DIR}/${mem9}

      elif [ $i -eq 10 ]; then
	 export mem10=rrfsmem2.m0002.t${cyc_lag6}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag6}.nc
         export fcst_file=${MEM10_INPUT_DIR}/${mem10}

      elif [ $i -eq 11 ]; then
	 export mem11=rrfsmem3.m0003.t${cyc_lag6}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag6}.nc
         export fcst_file=${MEM11_INPUT_DIR}/${mem11}

      elif [ $i -eq 12 ]; then
	 export mem12=rrfsmem4.m0004.t${cyc_lag6}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag6}.nc
         export fcst_file=${MEM12_INPUT_DIR}/${mem12}

      elif [ $i -eq 13 ]; then
	 export mem13=rrfsmem5.m0005.t${cyc_lag6}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag6}.nc
         export fcst_file=${MEM13_INPUT_DIR}/${mem13}

      elif [ $i -eq 14 ]; then
	 export mem14=hrrr.t${cyc_lag6}z.MXUPHL25_A24.SSPF.${ACCUM_BEG}-${ACCUM_END}.f${fhr_end_lag6}.nc
         export fcst_file=${MEM14_INPUT_DIR}/${mem14}

      fi

      # Copy the member files to working directory if they exist
      if [ -s $fcst_file ]; then
         echo "File found for member $i. Copying to working directory."
         cp -v $fcst_file ${MODEL_INPUT_DIR}
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
    
   if [ "$fhr_end" -gt 54 ]; then
      export mems="$mem1, $mem2, $mem3, $mem4, $mem5, $mem6"
      export nmem="6"
      export min_file_req=6
      export ens_thresh="1.0"
   elif [ "$fhr_end" -gt 48 ]; then
      export mems="$mem1, $mem2, $mem3, $mem4, $mem5, $mem6, $mem8, $mem9, $mem10, $mem11, $mem12, $mem13"
      export nmem="12"
      export min_file_req=12
      export ens_thresh="1.0"
   elif [ "$fhr_end" -gt 42 ]; then
      export mems="$mem1, $mem2, $mem3, $mem4, $mem5, $mem6, $mem7, $mem8, $mem9, $mem10, $mem11, $mem12, $mem13"
      export nmem="13"
      export min_file_req=12
      export ens_thresh="0.92"
   else
      export mems="$mem1, $mem2, $mem3, $mem4, $mem5, $mem6, $mem7, $mem8, $mem9, $mem10, $mem11, $mem12, $mem13, $mem14"
      export nmem="14"
      export min_file_req=12
      export ens_thresh="0.85"
   fi
   if [ $nfiles -ge $min_file_req ]; then
      echo "Found $nfiles forecast files. Generating ${MODELNAME} SSPF for ${vhr}Z ${INITDATE} cycle at F${fhr_end}"
      ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/GenEnsProd_fcstREFS_MXUPHL_SurrogateSevere.conf
      export err=$?; err_chk

      if [ $SENDCOM = YES ]; then
         mkdir -p $COMOUT/${RUN}.${INITDATE}/${modsys}
         for FILE in $DATA/sspf/${modsys}.${INITDATE}/*; do
            cp -v $FILE $COMOUT/${RUN}.${INITDATE}/${modsys}
         done
      fi

   else

      echo "WARNING: Only $nfiles ${MODELNAME} forecast files found for ${vhr}Z ${INITDATE} cycle. At least $min_file_req files are required. METplus will not run."

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


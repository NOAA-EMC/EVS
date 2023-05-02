#!/bin/bash
###############################################################################
# Name of Script: exevs_rrfs_severe_prep.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script preprocesses RRFS control UH data for 
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
# Define surrogate severe settings
############################################################

export VERIF_GRID=G211
export VERIF_GRID_DX=81.271
export GAUSS_RAD=120

export MXUPHL25_THRESH1=160.0


############################################################
# Set some model-specific environment variables 
############################################################

export COMINfcst=${COMINrrfs}

if [ $cyc -eq 00 ];then
   nloop=2
   fhr_beg1=12
   fhr_end1=36
   fhr_beg2=36
   fhr_end2=60

elif [ $cyc -eq 06 ]; then
   nloop=2
   fhr_beg1=6
   fhr_end1=30
   fhr_beg2=30
   fhr_end2=54

elif [ $cyc -eq 12 ]; then
   nloop=2
   fhr_beg1=0
   fhr_end1=24
   fhr_beg2=24
   fhr_end2=48

elif [ $cyc -eq 18 ]; then
   nloop=1
   fhr_beg1=18
   fhr_end1=42

else
   echo "Current cyc is unsupported"
   exit 0

fi

export nloop
export fhr_beg1
export fhr_end1
export fhr_beg2
export fhr_end2


############################################################
# Write poescript for each domain and use case
############################################################

njob=0

# Create output directory for GridStat (and EnsembleStat) runs
mkdir -p $DATA/gen_ens_prod
mkdir -p $DATA/pcp_combine
mkdir -p $DATA/sspf

MEMNUM="ctl"
echo "${USHevs}/${COMPONENT}/evs_rrfs_severe_prep.sh $MEMNUM $njob" >> $DATA/poescript
njob=$((njob+1))


for member in {1..9}; do
   MEMNUM="mem000${member}"
   echo "${USHevs}/${COMPONENT}/evs_rrfs_severe_prep.sh $MEMNUM $njob" >> $DATA/poescript
   njob=$((njob+1))
done


###################################################################
# Run the command file
###################################################################

chmod 775 $DATA/poescript

export MP_PGMMODEL=mpmd
export MP_CMDFILE=${DATA}/poescript

if [ $USE_CFP = YES ]; then

   echo "running cfp"
   mpiexec -np $nproc --cpu-bind verbose,core cfp ${MP_CMDFILE}
   export err=$?; err_chk
   echo "done running cfp"

else

   echo "not running cfp"
   ${MP_CMDFILE}
   export err=$?; err_chk

fi


###################################################################
# Copy hourly output to $COMOUT
###################################################################

output_dirs="pcp_combine sspf"

if [ $SENDCOM = YES ]; then

   mkdir -p $COMOUT/${modsys}.${IDATE}

   for output_dir in ${output_dirs}; do
      if [ "$(ls -A $DATA/$output_dir)" ]; then
         for FILE in $DATA/${output_dir}/${modsys}.${IDATE}/*; do
            cp -v $FILE $COMOUT/${modsys}.${IDATE}
         done
      fi
   done
fi



exit



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

      export fcst_file=$COMINfcst/${modsys}.${IDATE}/${cyc}/${MODELNAME}.t${cyc}z.prslev.f$(printf "%03d" $fhr).conus_3km.grib2

      if [ -s $fcst_file ]; then
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

      ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/GenEnsProd_fcstCAM_MXUPHL_SurrogateSevere.conf
      export err=$?; err_chk


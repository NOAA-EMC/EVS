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

export machine=${machine:-"WCOSS2"}
export VERIF_GRID=G211
export VERIF_GRID_DX=81.271
export GAUSS_RAD=120


############################################################
# Set some model-specific environment variables 
############################################################

export MODEL_INPUT_DIR=${COMINrrfs}

export MXUPHL25_THRESH1=160.0

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
   err_exit "Current cyc is unsupported"

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


for member in {1..5}; do
   MEMNUM="${member}"

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
            if [ -s "$FILE" ]; then
               cp -v $FILE $COMOUT/${modsys}.${IDATE}
            fi
         done
      fi
   done
fi

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

#!/bin/bash

##################################################################################
# Name of Script: exevs_cam_radar_plots.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script runs METplus to generate radar
#                    verification graphics for deterministic and ensemble CAMs.
# History Log:
# 06/2023: Initial script assembled by Logan Dawson
##################################################################################


set +x

echo
echo " ENTERING SUB SCRIPT $0 "
echo

set -x


############################################################
# Set some job-wide environment variables
############################################################

export USH_DIR=${USHevs}/${COMPONENT}

export PRUNE_DIR=${DATA}/data
export STAT_OUTPUT_BASE_DIR=${DATA}/stat_archive
export STAT_OUTPUT_BASE_TEMPLATE="{MODEL}.{valid?fmt=%Y%m%d}/${NET}.stats.{MODEL}.${RUN}.${VERIF_CASE}.v{valid?fmt=%Y%m%d}.stat"

export SAVE_DIR=${DATA}/out
export IMG_HEADER=${NET}.${COMPONENT}

export LOG_TEMPLATE="${SAVE_DIR}/logs/EVS_verif_plotting_job{njob}_`date '+%Y%m%d-%H%M%S'`_$$.out"
export LOG_LEVEL="DEBUG"

export PYTHONDONTWRITEBYTECODE=1

export CONFIDENCE_INTERVALS="False"

# METplus Settings
IFS='.' read -ra MET_VER <<< "$met_ver"
printf -v MET_VERSION '%s.' "${MET_VER[@]:0:2}"
export MET_VERSION="${MET_VERSION%.}"


############################################################
# Define some configuration settings to define
# plots to be created.
############################################################


export MODELS="namnest, hireswarw, hireswarwmem2, hireswfv3, hrrr"
export VERIF_TYPE="mrms"
export DATE_TYPE="INIT"
export EVAL_PERIOD="LAST31DAYS"
export eval_period=`echo ${EVAL_PERIOD} | tr '[:upper:]' '[:lower:]'`
export pastdays=31
export VALID_BEG=""
export VALID_END=""
export INIT_BEG=""
export INIT_END=""
export FCST_VALID_HOUR=""
export FCST_LEAD="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60"


PLOT_TYPES="threshold_average lead_average performance_diagram"
DOMAINS="alaska conus"
FCST_INIT_HOURS="0 6 12 18"

############################################################
# Write poescript for each domain and use case
############################################################

# Create working directories 
mkdir -p ${PRUNE_DIR}
mkdir -p ${SAVE_DIR}/logs
mkdir -p ${SAVE_DIR}/${VERIF_CASE}/${eval_period}
mkdir -p ${STAT_OUTPUT_BASE_DIR}



model_list="hireswarw hireswarwmem2 hireswfv3 hrrr namnest href_pmmn"

for model in ${model_list}; do
   n=0
   while [ $n -le $pastdays ]; do
      hrs=$((n*24))
      day=`$NDATE -$hrs ${VDATE}00 | cut -c1-8`

      mkdir -p ${STAT_OUTPUT_BASE_DIR}/${model}.${day}

      stat_file=evs.stats.${model}.${RUN}.${VERIF_CASE}.v${day}.stat
      dest=${STAT_OUTPUT_BASE_DIR}/${model}.${day}/${stat_file}

      if [ ${model:0:4} = href ]; then
	 origin=${COMIN}/stats/${COMPONENT}/${model:0:4}.${day}/${stat_file}
      else
	 origin=${COMIN}/stats/${COMPONENT}/${model}.${day}/${stat_file}
      fi

      if [ -s $origin ]; then
         ln -sf ${origin} ${dest}
      fi

      n=$((n+1))
   done
done



njob=0

#Loop over plot types
for PLOT_TYPE in ${PLOT_TYPES}; do

   if [ $PLOT_TYPE = lead_average ]; then
      LINE_TYPES="nbrcnt nbrctc"
   elif [ $PLOT_TYPE = performance_diagram ]; then
      LINE_TYPES="nbrctc"
   elif [ $PLOT_TYPE = threshold_average ]; then
      LINE_TYPES="nbrcnt nbrctc"
   fi

   # Loop over domains
   for DOMAIN in ${DOMAINS}; do

      # Set list of fields based on domain
      if [ $DOMAIN = conus ]; then
         RADAR_FIELDS="REFC RETOP"
      elif [ $DOMAIN = alaska ]; then
         RADAR_FIELDS="REFC"
      fi

      # Loop over radar fields
      for RADAR_FIELD in ${RADAR_FIELDS}; do

         # Loop over line types
         for LINE_TYPE in ${LINE_TYPES}; do

            # Loop over forecast initializations
            for FCST_INIT_HOUR in ${FCST_INIT_HOURS}; do
	
               echo "${USHevs}/${COMPONENT}/evs_cam_plots_radar.sh $PLOT_TYPE $DOMAIN $RADAR_FIELD $LINE_TYPE $FCST_INIT_HOUR $njob" >> $DATA/poescript
               njob=$((njob+1))

            done

         done

      done

   done

done



###################################################################
# Run the command file 
####################################################################

chmod 775 $DATA/poescript

export MP_PGMMODEL=mpmd
export MP_CMDFILE=${DATA}/poescript

#USE_CFP=NO
if [ $USE_CFP = YES ]; then

#  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   echo "running cfp"
   mpiexec -np $nproc --cpu-bind verbose,core cfp ${MP_CMDFILE} 
   export err=$?; err_chk
   echo "done running cfp"

else

   echo "not running cfp"
   ${MP_CMDFILE} 
   export err=$?; err_chk

fi


exit

python $USHevs/${COMPONENT}/cam_plots_radar_create_job_scripts.py
export err=$?; err_chk



###################################################################
# Copy hourly output to $COMOUT
###################################################################

if [ $MODELNAME = href ] || [ $MODELNAME = rrfs ]; then
   output_dirs="ensemble_stat grid_stat"
else
   output_dirs="grid_stat"
fi

if [ $SENDCOM = YES ]; then
   for output_dir in ${output_dirs}; do
      if [ "$(ls -A $DATA/$output_dir)" ]; then
         for FILE in $DATA/${output_dir}/*; do
            cp -v $FILE $COMOUTsmall
         done
      fi
   done
fi


###################################################################
# Run METplus (StatAnalysis) if GridStat output exists
###################################################################

if [ $cyc = 23 ]; then

   if [ "$(ls -A $COMOUTsmall)" ]; then

      if [ $MODELNAME = href ]; then

         HREF_MODS="href_pmmn href_prob href"
         HREF_MODS="href_pmmn href_prob"

         for HREF_MOD in ${HREF_MODS}; do
	    export HREF_MOD
            run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/StatAnalysis_fcstHREF_obsMRMS_gatherByDay.conf
            export err=$?; err_chk
         done

      else

         run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/StatAnalysis_fcstCAM_obsMRMS_gatherByDay.conf
         export err=$?; err_chk

      fi

      # Copy output to $COMOUTfinal
      if [ $SENDCOM = YES ]; then
         mkdir -p $COMOUTfinal
         for FILE in $DATA/stat_analysis/*; do
            cp -v $FILE $COMOUTfinal
         done
      fi

   else
      echo "Missing stat output for ${VDATE}. METplus will not run."

   fi

fi


exit


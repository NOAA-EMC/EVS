#!/bin/bash

##################################################################################
# Name of Script: exevs_cam_radar_plots.sh
# Contact(s):     Marcel G. Caron (marcel.caron@noaa.gov)
# Purpose of Script: This script runs METplus to generate radar
#                    verification graphics for deterministic and ensemble CAMs.
##################################################################################


set -x

echo
echo " ENTERING SUB SCRIPT $0 "
echo

set -x


############################################################
# Define some configuration settings to define
# plots to be created.
############################################################

export machine=${machine:-"WCOSS2"}
export MODELS="hrrr, namnest, hireswarw, hireswarwmem2, hireswfv3, href_pmmn"
export VERIF_TYPE="mrms"
export DATE_TYPE="INIT"
export eval_period=`echo ${EVAL_PERIOD} | tr '[:upper:]' '[:lower:]'`
export pastdays=`echo ${EVAL_PERIOD} | cut -c 5-6`
export VALID_BEG=""
export VALID_END=""
export INIT_BEG=""
export INIT_END=""
export FCST_VALID_HOUR=""
export FCST_LEAD="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60"

#PLOT_TYPES="threshold_average lead_average performance_diagram"
DOMAINS="alaska conus"
FCST_INIT_HOURS="0 6 12 18"


############################################################
# Set some job-wide environment variables
############################################################

export USH_DIR=${USHevs}/${COMPONENT}

export PRUNE_DIR=${DATA}/data
export STAT_OUTPUT_BASE_DIR=${DATA}/stat_archive
export STAT_OUTPUT_BASE_TEMPLATE="{MODEL}.{valid?fmt=%Y%m%d}/${NET}.stats.{MODEL}.${RUN}.${VERIF_CASE}.v{valid?fmt=%Y%m%d}.stat"

export SAVE_DIR=${DATA}/out
export LOG_DIR=${SAVE_DIR}/logs
export OUTPUT_DIR=${SAVE_DIR}/${VERIF_CASE}/${eval_period}
export IMG_HEADER=${NET}.${COMPONENT}

export LOG_TEMPLATE="${LOG_DIR}/EVS_verif_plotting_job{njob}_$($NDATE)_$$.out"
export LOG_LEVEL="DEBUG"

export PYTHONDONTWRITEBYTECODE=1

export CONFIDENCE_INTERVALS="False"

# METplus Settings
IFS='.' read -ra MET_VER <<< "$met_ver"
printf -v MET_VERSION '%s.' "${MET_VER[@]:0:2}"
export MET_VERSION="${MET_VERSION%.}"


############################################################
# Write poescript for each domain and use case
############################################################

# Create working directories 
mkdir -p ${PRUNE_DIR}
mkdir -p ${STAT_OUTPUT_BASE_DIR}
mkdir -p ${LOG_DIR}
mkdir -p ${OUTPUT_DIR}


model_list="hrrr namnest hireswarw hireswarwmem2 hireswfv3 href_pmmn"

for model in ${model_list}; do
   n=0
   while [ $n -le $pastdays ]; do
      hrs=$((n*24))
      day=`$NDATE -$hrs ${VDATE}00 | cut -c 1-8`

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




if [ $LINE_TYPE = nbrcnt ]; then
   PLOT_TYPES="lead_average threshold_average"
elif [ $LINE_TYPE = nbrctc ]; then
   PLOT_TYPES="lead_average performance_diagram threshold_average"
fi


njob=0

#Loop over plot types
for PLOT_TYPE in ${PLOT_TYPES}; do

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

         # Loop over forecast initializations
         for FCST_INIT_HOUR in ${FCST_INIT_HOURS}; do
	
            echo "${USHevs}/${COMPONENT}/evs_cam_plots_radar.sh $PLOT_TYPE $DOMAIN $RADAR_FIELD $LINE_TYPE $FCST_INIT_HOUR $njob" >> $DATA/poescript
            njob=$((njob+1))

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

export USE_CFP=YES

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
# Copy output to $COMOUT
###################################################################

cd $OUTPUT_DIR

export tarfile=${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}_${LINE_TYPE}.${eval_period}.v${VDATE}.tar

if [ "$(ls -A $OUTPUT_DIR)" ]; then
   tar -cvf ${tarfile} ./*.png
fi

if [ $SENDCOM = YES ]; then

   mkdir -p $COMOUT/${RUN}.${VDATE}

   if [ -s $tarfile ]; then
      cp -v $tarfile $COMOUT/${RUN}.${VDATE}/
      if [ $SENDDBN = YES ]; then
          $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/${RUN}.${VDATE}/${tarfile}
      fi
   else
      echo "tarfile creation was not completed. Need to rerun"
   fi

fi


exit


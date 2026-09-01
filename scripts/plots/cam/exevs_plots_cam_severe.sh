#!/bin/bash

##################################################################################
# Name of Script: exevs_plots_cam_severe.sh
# Contact(s):     Marcel G. Caron (marcel.caron@noaa.gov)
# Purpose of Script: This script runs METplus to generate severe
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
export MODELS="hrrr, rrfs, rrfsmem1, rrfsmem2, rrfsmem3, rrfsmem4, rrfsmem5"
export VERIF_TYPE="lsr"
export DATE_TYPE="INIT"
export eval_period=`echo ${EVAL_PERIOD} | tr '[:upper:]' '[:lower:]'`
export pastdays=`echo ${EVAL_PERIOD} | cut -c 5-6`
export VALID_BEG=""
export VALID_END=""
export INIT_BEG=""
export INIT_END=""
export FCST_VALID_HOUR=""


############################################################
# Set some job-wide environment variables
############################################################

export USH_DIR=${USHevs}/${COMPONENT}

export PRUNE_DIR=${DATA}/data
export STAT_OUTPUT_BASE_DIR=${DATA}/stat_archive
export STAT_OUTPUT_BASE_TEMPLATE="{MODEL}.{valid?fmt=%Y%m%d}/${NET}.stats.{MODEL}.${RUN}.${VERIF_CASE}.v{valid?fmt=%Y%m%d}.stat"

export OUTPUT_DIR=${DATA}/out/${VERIF_CASE}/${eval_period}
export IMG_HEADER=${NET}.${COMPONENT}

export RESTART_DIR="${COMOUTplots}/${VERIF_CASE}/restart"
export COMPLETED_JOBS_DIR="completed_jobs_${LINE_TYPE}_${EVAL_PERIOD}"

export LOG_LEVEL="DEBUG"

export PYTHONDONTWRITEBYTECODE=1

export CONFIDENCE_INTERVALS="False"

# METplus Settings
IFS='.' read -ra MET_VER <<< "$met_ver"
printf -v MET_VERSION '%s.' "${MET_VER[@]:0:2}"
export MET_VERSION="${MET_VERSION%.}"


############################################################
# Symlink .stat files from COMIN
# Mainly for REFS when product is included in model name 
############################################################

# Create working directories 
mkdir -p ${PRUNE_DIR}
mkdir -p ${STAT_OUTPUT_BASE_DIR}
mkdir -p ${OUTPUT_DIR}
mkdir -p ${RESTART_DIR}
mkdir -p ${RESTART_DIR}/${COMPLETED_JOBS_DIR}
mkdir -p ${RESTART_DIR}/${VERIF_CASE}/${EVAL_PERIOD}
mkdir -p ${DATA}/out/logs # main log output dir


og_model_list="hrrr rrfs rrfsmem1 rrfsmem2 rrfsmem3 rrfsmem4 rrfsmem5"

for model in ${og_model_list}; do
   n=0
   while [ $n -le $pastdays ]; do
      hrs=$((n*24))
      day=`$NDATE -$hrs ${VDATE}00 | cut -c 1-8`

      mkdir -p ${STAT_OUTPUT_BASE_DIR}/${model}.${day}

      stat_file=evs.stats.${model}.${RUN}.${VERIF_CASE}.v${day}.stat
      dest=${STAT_OUTPUT_BASE_DIR}/${model}.${day}/${stat_file}

      if [ "${model:0:4}" = "refs" ]; then
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


############################################################
# Check For Restart Files
############################################################

python ${USHevs}/cam/cam_production_restart.py
export err=$?; err_chk


############################################################
# Write poescript for each domain and use case
############################################################

DOMAINS="conus"

if [ "$LINE_TYPE" = "nbrcnt" ]; then
   PLOT_TYPES="lead_average threshold_average"
elif [ "$LINE_TYPE" = "nbrctc" ]; then
   PLOT_TYPES="lead_average performance_diagram threshold_average"
elif [ "$LINE_TYPE" = "pstd" ]; then
   PLOT_TYPES="lead_average threshold_average"
fi


njob=0

#Loop over plot types
for PLOT_TYPE in ${PLOT_TYPES}; do

   if [ "$PLOT_TYPE" = "lead_average" ]; then
      FCST_INIT_HOURS="0,6,12,18"
   else
      FCST_INIT_HOURS="0 6 12 18"
   fi

   # Loop over domains
   for DOMAIN in ${DOMAINS}; do

      # Loop over forecast initializations
      for FCST_INIT_HOUR in ${FCST_INIT_HOURS}; do
	
         if [ "$FCST_INIT_HOUR" = "0,6,12,18" ]; then
            export FCST_LEADs="24,36,48,60,72,84"
         elif [ "$FCST_INIT_HOUR" = "0" ]; then
            export FCST_LEADs="36 60 84"
         elif [ "$FCST_INIT_HOUR" = "6" ]; then
            export FCST_LEADs="30 54 78"
         elif [ "$FCST_INIT_HOUR" = "12" ]; then
            export FCST_LEADs="24 48 72"
         elif [ "$FCST_INIT_HOUR" = "18" ]; then
            export FCST_LEADs="42 66"
         fi

         # Loop over forecast initializations
         for FCST_LEAD in ${FCST_LEADs}; do
            
            model_list="${og_model_list}"
            if [ "$FCST_LEAD" -gt 60 ]; then
               model_list=${model_list/hrrr /}
               model_list=${model_list/ rrfsmem1/}
               model_list=${model_list/ rrfsmem2/}
               model_list=${model_list/ rrfsmem3/}
               model_list=${model_list/ rrfsmem4/}
               model_list=${model_list/ rrfsmem5/}

            elif [ "$FCST_LEAD" -gt 48 ]; then
               model_list=${model_list/hrrr /}
            fi

            echo "Using models in (${model_list}) for FCST_LEAD=$FCST_LEAD."

            echo "${USHevs}/${COMPONENT}/evs_cam_plots_severe.sh $PLOT_TYPE $DOMAIN $LINE_TYPE $FCST_INIT_HOUR $FCST_LEAD $njob" >> $DATA/poescript
            mkdir -p ${DATA}/out/workdirs/job${njob}/logs
            mkdir -p ${DATA}/out/workdirs/job${njob}/${COMPLETED_JOBS_DIR}
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

if [ "$USE_CFP" = "YES" ]; then

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
# Copy Plots Output to Main Directory
###################################################################
shopt -s nullglob
for CHILD_DIR in ${DATA}/out/workdirs/*; do
    cp -ruv $CHILD_DIR/* ${DATA}/out/.
    export err=$?; err_chk
done
shopt -u nullglob


###################################################################
# Copy output to $COMOUT
###################################################################

cd $OUTPUT_DIR

export tarfile=${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}_${LINE_TYPE}.${eval_period}.v${VDATE}.tar

if [ "$(ls -A $OUTPUT_DIR)" ]; then
   tar -cvf ${tarfile} ./*.png
fi

if [ "$SENDCOM" = "YES" ]; then

   mkdir -p $COMOUT/${RUN}.${VDATE}

   if [ -s $tarfile ]; then
      cp -v $tarfile $COMOUT/${RUN}.${VDATE}/
      if [ "$SENDDBN" = "YES" ]; then
          $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/${RUN}.${VDATE}/${tarfile}
      fi
   else
      echo "tarfile creation was not completed. Need to rerun"
   fi

fi


exit


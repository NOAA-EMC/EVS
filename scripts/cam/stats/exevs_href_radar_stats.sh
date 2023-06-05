#!/bin/bash
###############################################################################
# Name of Script: exevs_href_radar_stats.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script runs METplus to generate radar
#                    verification statistics for HREF.
# History Log:
# 04/28/2023: Initial script assembled by Logan Dawson
###############################################################################


set +x

echo
echo " ENTERING SUB SCRIPT $0 "
echo

set -x


###################################################################
# Set some model-specific variables
###################################################################

export fhr_min=1
export fhr_max=48
export fhr_inc=1

export COMINfcst=${COMINhref}


############################################################
# Set up poescript for MPMD execution
############################################################

mkdir -p $DATA/ensemble_stat
mkdir -p $DATA/grid_stat

ENSPRODS="pmmn prob"
DOMAINS="alaska conus"

for ENSPROD in ${ENSPRODS}; do

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
         echo "${USHevs}/${COMPONENT}/evs_href_stats_radar.sh $DOMAIN $RADAR_FIELD $ENSPROD" >> $DATA/poescript
      done

   done


   ###################################################################
   # Run the command file 
   ####################################################################

   chmod 775 $DATA/poescript

   export MP_PGMMODEL=mpmd
   export MP_CMDFILE=${DATA}/poescript

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

done


###################################################################
# Run METplus (StatAnalysis) if GridStat output exists
###################################################################

if [ $cyc = 23 ]; then

   if [ "$(ls -A $COMOUTsmall)" ]; then

      run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/StatAnalysis_fcstCAM_obsMRMS_gatherByDay.conf
      export err=$?; err_chk

      # Copy output to $COMOUTfinal
      if [ $SENDCOM = YES ]; then
         mkdir -p $COMOUTfinal
         for FILE in $DATA/stat_analysis/*; do
            cp -v $FILE $COMOUTfinal
         done
      fi

   else
      echo "Missing stat output for ${VDATE}12. METplus will not run."

   fi

fi


exit


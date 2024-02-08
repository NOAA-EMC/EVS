#!/bin/bash

##################################################################################
# Name of Script: exevs_cam_radar_stats.sh
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: This script runs METplus to generate radar
#                    verification statistics for deterministic and ensemble CAMs.
# History Log:
# 04/28/2023: Initial script assembled by Logan Dawson
##################################################################################


set -x

echo
echo " ENTERING SUB SCRIPT $0 "
echo

set -x


############################################################
# Update Mask List and Include SPC OLTKs if Valid
# Mask Files Exist in EVSINspcotlk
# Only for CONUS verification
############################################################

export machine=${machine:-"WCOSS2"}
export VERIF_GRID=G227
export ADD_CONUS_REGIONS=True
export ADD_CONUS_SUBREGIONS=False

python $USHevs/${COMPONENT}/evs_cam_stats_check_otlk.py
export err=$?; err_chk


############################################################
# Write poescript for each domain and use case
############################################################

njob=0

# Create output directory for GridStat (and EnsembleStat) runs 
mkdir -p $DATA/grid_stat

if [ $MODELNAME = href ] || [ $MODELNAME = rrfs ]; then
   mkdir -p $DATA/ensemble_stat
fi


if [ $MODELNAME = href ]; then
   PRODS="pmmn ppf prob ens"
   PRODS="pmmn ppf prob"
else
   PRODS="det"
fi

DOMAINS="alaska conus"

#Loop over products
for PROD in ${PRODS}; do

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

         echo "${USHevs}/${COMPONENT}/evs_cam_stats_radar.sh $DOMAIN $RADAR_FIELD $PROD $njob" >> $DATA/poescript
         njob=$((njob+1))

      done

   done

done


###################################################################
# Run the command file 
####################################################################

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

if [ $MODELNAME = href ] || [ $MODELNAME = rrfs ]; then
   output_dirs="ensemble_stat grid_stat"
else
   output_dirs="grid_stat"
fi

if [ $SENDCOM = YES ]; then
   for output_dir in ${output_dirs}; do
      if [ "$(ls -A $DATA/$output_dir)" ]; then
         for FILE in $DATA/${output_dir}/*; do
            if [ -s "$FILE" ]; then
               cp -v $FILE $COMOUTsmall
            fi
         done
      fi
   done
fi


###################################################################
# Run METplus (StatAnalysis) if GridStat output exists
###################################################################

if [ $vhr = 23 ]; then

   if [ "$(ls -A $COMOUTsmall)" ]; then

      if [ $MODELNAME = href ]; then

         HREF_MODS="href_pmmn href_prob href"
         HREF_MODS="href_pmmn href_prob"

         for HREF_MOD in ${HREF_MODS}; do
	    export HREF_MOD
            run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstHREF_obsMRMS_gatherByDay.conf
            export err=$?; err_chk
         done

      else

         run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstCAM_obsMRMS_gatherByDay.conf
         export err=$?; err_chk

      fi

      # Copy output to $COMOUTfinal
      if [ $SENDCOM = YES ]; then
         mkdir -p $COMOUTfinal
         for FILE in $DATA/stat_analysis/*; do
            if [ -s "$FILE" ]; then
               cp -v $FILE $COMOUTfinal
            fi
         done
      fi

   else
      echo "Missing stat output for ${VDATE}. METplus will not run."

   fi

fi

# Cat the METplus log files
log_dir="$DATA/logs"
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


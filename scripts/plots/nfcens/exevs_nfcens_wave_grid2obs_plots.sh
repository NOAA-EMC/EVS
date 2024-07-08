#!/bin/bash
################################################################################
# Name of Script: exevs_nfcens_wave_grid2obs_plots.sh                           
# Deanna Spindler / Deanna.Spindler@noaa.gov                                    
# Samira Ardani / samira.ardani@noaa.gov
# Purpose of Script: Run the grid2obs plots for any global wave model           
#                    (deterministic and ensemble: GEFS-Wave, GFS-Wave, NFCENS)  
#                    NFCENSv2: Add FNMOC and GEFS model to compare against NFCENS                                                                                  
# Usage:                                                                        
#  Parameters: None                                                             
#  Input files:                                                                 
#     evs.stats.nfcens.wave.grid2obs.vYYYYMMDD.stat                             
#  Output files:                                                                
#     evs.plots.nfcens.wave.grid2obs.last31days.vYYYYMMDD.tar                   
#     evs.plots.nfcens.wave.grid2obs.last90days.vYYYYMMDD.tar                   
#  User controllable options: None                                              
################################################################################

set -x

# set major & minor MET version
export MET_VERSION_major_minor=`echo $MET_VERSION | sed "s/\([^.]*\.[^.]*\)\..*/\1/g"`

# Use LOUD variable to turn on/off trace.  Defaults to YES (on).
export LOUD=${LOUD:-YES}; [[ $LOUD = yes ]] && export LOUD=YES
[[ "$LOUD" != YES ]] && set -x

#############################
## grid2obs wave model plots 
#############################

cd $DATA
echo "Starting grid2obs_plots for ${MODELNAME}_${RUN}"

set -x
echo ' '
echo ' ******************************************'
echo " *** ${MODELNAME}-${RUN} grid2obs plots ***"
echo ' ******************************************'
echo ' '
echo "Starting at : `date`"
echo '-------------'
echo ' '
[[ "$LOUD" = YES ]] && set -x

############################
# get the model .stat files 
############################
set -x
echo ' '
echo 'Copying *.stat files :'
echo '-----------------------------'
[[ "$LOUD" = YES ]] && set -x

mkdir -p ${DATA}/stats

plot_start_date=${PDYm90}
plot_end_date=${VDATE}
export models='nfcens gefs fnmoc'
export MODNAMS='NFCENS GEFS FNMOC'
export model_list=${MODNAMS}
theDate=${plot_start_date}
while (( ${theDate} <= ${plot_end_date} )); do
	EVSINnfcens=${COMIN}/stats/${COMPONENT}/${MODELNAME}.${theDate}
	for model in ${models}; do
		if [ -s ${EVSINnfcens}/evs.stats.${model}.${RUN}.${VERIF_CASE}.v${theDate}.stat ]; then
	  		cp ${EVSINnfcens}/evs.stats.${model}.${RUN}.${VERIF_CASE}.v${theDate}.stat ${DATA}/stats/.
  		else
	  		echo "WARNING: ${EVSINnfcens}/evs.stats.${model}.${RUN}.${VERIF_CASE}.v${theDate}.stat DOES NOT EXIST"
  		fi
	done
	theDate=$(date --date="${theDate} + 1 day" '+%Y%m%d')
done

####################
# quick error check 
####################
nc=`ls ${DATA}/stats/evs.stats.nfcens*stat | wc -l | awk '{print $1}'`
nc1=`ls ${DATA}/stats/evs.stats.gefs*stat | wc -l | awk '{print $1}'`
nc2=`ls ${DATA}/stats/evs.stats.fnmoc*stat | wc -l | awk '{print $1}'`

echo " Found ${nc} ${DATA}/stats/evs.stats.nfcens*stat file for ${VDATE} "
if [ "${nc}" != '0' ]
	then
  	set -x
  	echo "Successfully copied the NFCENS *.stat file for ${VDATE}"
  	[[ "$LOUD" = YES ]] && set -x
	
	if [ "${nc1}" != '0' ]; then
		 echo "Successfully copied the GEFS *.stat file for ${VDATE}"
	else
		 echo "WARNING: Did not copy the GEFS *.stat files for ${VDATE}" 
	fi

	
	if [ "${nc2}" != '0' ]; then
		 echo "Successfully copied the FNMOC *.stat file for ${VDATE}"
	else
		 echo "WARNING: Did not copy the FNMOC *.stat files for ${VDATE}" 
	fi
	
else
  set -x
  echo ' '
  echo '**************************************** '
  echo '*** FATAL ERROR: NO NFCENS *.stat FILES *** '
  echo "             for ${VDATE} "
  echo '**************************************** '
  echo ' '
  echo "${MODELNAME}_${RUN} $VDATE $vhour : NFCENS *.stat files missing."
  [[ "$LOUD" = YES ]] && set -x
  "FATAL ERROR: NO NFCENS *.stat files for ${VDATE}"
  err_exit "FATAL ERROR: Did not copy the NFCENS *.stat files for ${VDATE}"
  exit
fi

#################################
# Make the command files for cfp 
#################################

${USHevs}/${COMPONENT}/evs_wave_timeseries.sh
export err=$?; err_chk
## lead_averages
${USHevs}/${COMPONENT}/evs_wave_leadaverages.sh
export err=$?; err_chk
chmod 775 plot_all_${MODELNAME}_${RUN}_g2o_plots.sh

###########################################
# Run the command files for the LAST31DAYS 
###########################################
if [ ${run_mpi} = 'yes' ] ; then
  mpiexec -np 128 -ppn 64 --cpu-bind verbose,depth cfp plot_all_${MODELNAME}_${RUN}_g2o_plots.sh
else
  echo "not running mpiexec"
  sh plot_all_${MODELNAME}_${RUN}_g2o_plots.sh
fi

#######################
# Gather all the files 
#######################
periods='LAST31DAYS LAST90DAYS'
if [ $gather = yes ] ; then
  echo "copying all images into one directory"
  cp ${DATA}/wave/*png ${DATA}/sfcshp/.  ## lead_average plots
  nc=$(ls ${DATA}/sfcshp/*.fhrmean_valid*.png | wc -l | awk '{print $1}')
  echo "copied $nc lead_average plots"
  for period in ${periods} ; do
    period_lower=$(echo ${period,,})
    if [ ${period} = 'LAST31DAYS' ] ; then
      period_out='last31days'
    elif [ ${period} = 'LAST90DAYS' ] ; then
      period_out='last90days'
    fi
    # check to see if the plots are there
    nc=$(ls ${DATA}/sfcshp/*${period_lower}*.png | wc -l | awk '{print $1}')
    echo " Found ${nc} ${DATA}/plots/*${period_lower}*.png files for ${VDATE} "
    if [ "${nc}" != '0' ]
    then
      set -x
      echo "Found ${nc} ${period_lower} plots for ${VDATE}"
      [[ "$LOUD" = YES ]] && set -x
    else
      set -x
      echo ' '
      echo '**************************************** '
      echo '*** FATAL ERROR: NO ${period} PLOTS  *** '
      echo "    found for ${VDATE} "
      echo '**************************************** '
      echo ' '
      echo "${MODELNAME}_${RUN} ${VDATE} ${period}: PLOTS are missing."
      [[ "$LOUD" = YES ]] && set -x
      "FATAL ERROR : NO ${period} PLOTS FOR ${VDATE}"
      err_exit "FATAL ERROR: Did not find any ${period} plots for ${VDATE}"
    fi
    
    # tar and copy them to the final destination
    if [ "${nc}" > '0' ] ; then
      cd ${DATA}/sfcshp
      tar -cvf evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${period_out}.v${VDATE}.tar evs.*${period_lower}*.png
      if [ -s evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${period_out}.v${VDATE}.tar ]; then
	      cp -v evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${period_out}.v${VDATE}.tar ${COMOUTplots}/.
      fi
    fi
  done
else  
  echo "not copying the plots"
fi

msg="JOB $job HAS COMPLETED NORMALLY."

if [ $SENDDBN = YES ]; then
	for file in $(ls ${COMOUTplots}/${NET}.${STEP}.${COMPONENT}.${RUN}.*.tar);do
		$DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $file
	done
fi


#########################################
## copy log files into logs and cat them
#########################################

cd ${DATA}
mkdir -p ${DATA}/logs
log_dir=$DATA/logs

extns='out log'
for extn in ${extns} ; do
	count=$(find ${DATA} -type f -name "*.${extn}"|wc -l)
	if [ $count != 0 ] ; then
		cp ${DATA}/*.${extn} ${log_dir}

	fi
done	


log_file_count=$(find ${DATA} -type f -name "*.out" -o -name ".log" |wc -l)
if [[ $log_file_count -ne 0 ]]; then
	for log_file in $log_dir/*; do
		echo "Start: $log_file"
		cat $log_file
		echo "End: $log_file"
	done
fi

# --------------------------------------------------------------------------- #
# Ending output                                                                

set -x
echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs stat *** "
echo ' '
[[ "$LOUD" = YES ]] && set -x

# End of NFCENS grid2obs plots script ------------------------------------- #

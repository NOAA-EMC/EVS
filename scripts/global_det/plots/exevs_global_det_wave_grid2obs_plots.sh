#!/bin/bash
################################################################################
# Name of Script: exevs_global_det_wave_grid2obs_plots.sh                       
# Deanna Spindler / Deanna.Spindler@noaa.gov                                    
# Purpose of Script: Run the grid2obs plots for any global wave model           
#                    (deterministic and ensemble: GEFS-Wave, GFS-Wave, NWPS)    
#                                                                               
# Usage:                                                                        
#  Parameters: None                                                             
#  Input files:                                                                 
#     evs.stats.gfs.wave.grid2obs.vYYYYMMDD.stat                                
#  Output files:                                                                
#     evs.plots.global_det.wave.grid2obs.last31days.vYYYYMMDD.tar               
#     evs.plots.global_det.wave.grid2obs.last90days.vYYYYMMDD.tar               
#  User controllable options: None                                              
################################################################################

set -x 
# Use LOUD variable to turn on/off trace.  Defaults to YES (on).
export LOUD=${LOUD:-YES}; [[ $LOUD = yes ]] && export LOUD=YES
[[ "$LOUD" != YES ]] && set +x

#############################
## grid2obs wave model plots 
#############################

cd $DATA
echo "in $0 JLOGFILE is $jlogfile"
echo "Starting grid2obs_plots for ${MODELNAME}_${RUN}"

set +x
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
set +x
echo ' '
echo 'Copying *.stat files :'
echo '-----------------------------'
[[ "$LOUD" = YES ]] && set -x

mkdir -p ${DATA}/stats

plot_start_date=${PDYm90}
plot_end_date=${VDATE}

theDate=${plot_start_date}
while (( ${theDate} <= ${plot_end_date} )); do
  COMINstats=${COMIN}/stats/${COMPONENT}/${MODELNAME}.${theDate}
  cp ${COMINstats}/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${theDate}.stat ${DATA}/stats/.
  theDate=$(date --date="${theDate} + 1 day" '+%Y%m%d')
done

####################
# quick error check 
####################
nc=`ls ${DATA}/stats/evs*stat | wc -l | awk '{print $1}'`
echo " Found ${nc} ${DATA}/stats/evs*stat file for ${VDATE} "
if [ "${nc}" != '0' ]
then
  set +x
  echo "Successfully copied the GFS-Wave *.stat file for ${VDATE}"
  [[ "$LOUD" = YES ]] && set -x
else
  set +x
  echo ' '
  echo '**************************************** '
  echo '*** ERROR : NO GFS-Wave *.stat FILE *** '
  echo "             for ${VDATE} "
  echo '**************************************** '
  echo ' '
  echo "${MODELNAME}_${RUN} $VDATE $cycle : GFS-Wave *.stat file missing."
  [[ "$LOUD" = YES ]] && set -x
  ./postmsg "$jlogfile" "FATAL ERROR : NO GFS-Wave *.stat file for ${VDATE}"
  err_exit "FATAL ERROR: Did not copy the GFS-Wave *.stat file for ${VDATE}"
  exit
fi

#################################
# Make the command files for cfp 
#################################

## time_series
${USHevs}/${COMPONENT}/evs_wave_timeseries.sh

## lead_averages
${USHevs}/${COMPONENT}/evs_wave_leadaverages.sh

chmod 775 plot_all_${MODELNAME}_${RUN}_g2o_plots.sh

###########################################
# Run the command files for the PAST31DAYS 
###########################################
if [ ${run_mpi} = 'yes' ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
  mpiexec -np 36 --cpu-bind verbose,core --depth=3 cfp plot_all_${MODELNAME}_${RUN}_g2o_plots.sh
else
  echo "not running mpiexec"
  sh plot_all_${MODELNAME}_${RUN}_g2o_plots.sh
fi

#######################
# Gather all the files 
#######################
periods='PAST31DAYS PAST90DAYS'
if [ $gather = yes ] ; then
  echo "copying all images into one directory"
  cp ${DATA}/wave/*png ${DATA}/sfcshp/.  ## lead_average plots
  nc=$(ls ${DATA}/sfcshp/*.fhr_valid*.png | wc -l | awk '{print $1}')
  echo "copied $nc lead_average plots"
  for period in ${periods} ; do
    period_lower=$(echo ${period,,})
    if [ ${period} = 'PAST31DAYS' ] ; then
      period_out='last31days'
    elif [ ${period} = 'PAST90DAYS' ] ; then
      period_out='last90days'
    fi
    # check to see if the plots are there
    nc=$(ls ${DATA}/sfcshp/*${period_lower}*.png | wc -l | awk '{print $1}')
    echo " Found ${nc} ${DATA}/plots/*${period_lower}*.png files for ${VDATE} "
    if [ "${nc}" != '0' ]
    then
      set +x
      echo "Found ${nc} ${period_lower} plots for ${VDATE}"
      [[ "$LOUD" = YES ]] && set -x
    else
      set +x
      echo ' '
      echo '**************************************** '
      echo '*** ERROR : NO ${period} PLOTS  *** '
      echo "    found for ${VDATE} "
      echo '**************************************** '
      echo ' '
      echo "${MODELNAME}_${RUN} ${VDATE} ${period}: PLOTS are missing."
      [[ "$LOUD" = YES ]] && set -x
      ./postmsg "$jlogfile" "FATAL ERROR : NO ${period} PLOTS FOR ${VDATE}"
      err_exit "FATAL ERROR: Did not find any ${period} plots for ${VDATE}"
    fi
    
    # tar and copy them to the final destination
    if [ "${nc}" > '0' ] ; then
      cd ${DATA}/sfcshp
      tar -cvf evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${period_out}.v${VDATE}.tar evs.*${period_lower}*.png
    fi
  done
  cp evs.${STEP}.${COMPONENT}.${RUN}.*.tar ${COMOUTplots}/.
else  
  echo "not copying the plots"
fi

msg="JOB $job HAS COMPLETED NORMALLY."
postmsg "$jlogfile" "$msg"

# --------------------------------------------------------------------------- #
# Ending output                                                                

set +x
echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs stat *** "
echo ' '
[[ "$LOUD" = YES ]] && set -x

# End of GFS-Wave grid2obs plots script ------------------------------------- #

#!/bin/bash
################################################################################
# Name of Script: exevs_global_ens_wave_grid2obs_plots.sh                       
# Deanna Spindler / Deanna.Spindler@noaa.gov                                    
# Purpose of Script: Run the grid2obs plots for any global wave model           
#                    (deterministic and ensemble: GEFS-Wave, GFS-Wave, NWPS)    
#                                                                               
# Usage:                                                                        
#  Parameters: None                                                             
#  Input files:                                                                 
#     evs.stats.gefs.wave.grid2obs.vYYYYMMDD.stat                               
#  Output files:                                                                
#     evs.plots.global_ens.wave.grid2obs.last31days.vYYYYMMDD.tar               
#     evs.plots.global_ens.wave.grid2obs.last90days.vYYYYMMDD.tar               
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
  COMOUTstats=${COMOUT}/stats/${COMPONENT}/${MODELNAME}.${theDate}
  cp ${COMOUTstats}/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${theDate}.stat ${DATA}/stats/.
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
  echo "Successfully copied the GEFS-Wave *.stat file for ${VDATE}"
  [[ "$LOUD" = YES ]] && set -x
else
  set +x
  echo ' '
  echo '**************************************** '
  echo '*** ERROR : NO GEFS-Wave *.stat FILE *** '
  echo "             for ${VDATE} "
  echo '**************************************** '
  echo ' '
  echo "${MODELNAME}_${RUN} $VDATE $cycle : GEFS-Wave *.stat file missing."
  [[ "$LOUD" = YES ]] && set -x
  ./postmsg "$jlogfile" "FATAL ERROR : NO GEFS-Wave *.stat file for ${VDATE}"
  err_exit "FATAL ERROR: Did not copy the GEFS-Wave *.stat file for ${VDATE}"
  exit
fi

#################################
# Make the command files for cfp 
#################################

# set up plot variables

periods='PAST31DAYS PAST90DAYS'

cycles='00 12'
fhrs='000 024 048 072 096 120 144 168
      192 216 240 264 288 312 336 360 384'
wave_vars='WIND HTSGW PERPW'
stats_list='stats1 stats2 stats3 stats4 stats5'

export GRID2OBS_CONF="${PARMevs}/metplus_config/${COMPONENT}/${RUN}_${VERIF_CASE}/${STEP}"

cd ${DATA}
mkdir ${DATA}/sfcshp
touch plot_all_${MODELNAME}_${RUN}_g2o_plots.sh

# write the commands
for period in ${periods} ; do
  if [ ${period} = 'PAST31DAYS' ] ; then
    plot_start_date=${PDYm31}
  elif [ ${period} = 'PAST90DAYS' ] ; then
    plot_start_date=${PDYm90}
  fi
  for cyc in ${cycles} ; do
    for fhr in ${fhrs} ; do
      for wvar in ${wave_vars} ; do
        for stats in ${stats_list}; do
          echo "export VERIF_CASE=${VERIF_CASE} " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          echo "export RUN=${RUN} " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          echo "export USHevs=${USHevs}/${COMPONENT} " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          echo "export FIXevs=${FIXevs}  " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          echo "export DATA=${DATA} " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          echo "export MODNAM=${MODNAM} " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          echo "export PERIOD=${period} " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          echo "export VERIF_CASE=${VERIF_CASE} " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          echo "export plot_start_date=${plot_start_date} " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          echo "export plot_end_date=${VDATE} " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          echo "export CYC=${cyc} " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          case ${stats} in
            'stats1')
              echo "export METRIC='me, rmse' " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
              ;;
            'stats2')
              echo "export METRIC=pcor " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
              ;;
            'stats3')
              echo "export METRIC='fbar, obar' " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
              ;;
            'stats4')
              echo "export METRIC=esd " >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
              ;;
            'stats5')
              echo "export METRIC=si "  >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
              ;;
          esac
          echo "export FHR=${fhr}"        >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          echo "export WVAR=${wvar}"      >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          case ${wvar} in
            'WIND')
              echo "export OBS_LEVEL=Z10"  >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
              ;;
            *)
              echo "export OBS_LEVEL=L0"  >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
              ;;
          esac
          echo "${GRID2OBS_CONF}/py_plotting_wave.config"  >> plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          
          chmod +x plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh
          
          echo "${DATA}/plot_${wvar}_${cyc}_${fhr}_${stats}_${period}.sh" >> plot_all_${MODELNAME}_${RUN}_g2o_plots.sh
          
        done  # end of stats
      done  # end of wave vars
    done  # end of fcst hrs
  done  # end of cycles
done  # end of periods

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
if [ $gather = yes ] ; then
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

# End of GEFS-Wave grid2obs plots script ------------------------------------- #

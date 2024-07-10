#!/bin/bash
###############################################################################
# Name of Script: global_det_wave_timeseries.sh
# Developers: Deanna Spindler / Deanna.Spindler@noaa.gov
#             Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script generates the job scripts to create
#                    time series plots.
# Run By: scripts/plots/global_det/exevs_global_det_wave_grid2obs_plots.sh
###############################################################################

#################################
# Make the command files for cfp
#################################

set -x

# set up plot variables

periods="LAST${NDAYS}DAYS"

valid_hours='00 12'
fhrs='000 024 048 072 096 120 144 168
      192 216 240 264 288 312 336 360 384'
wave_vars='WIND HTSGW PERPW'
stats_list='stats1 stats2 stats3 stats4 stats5'
ptype='time_series'
obsnames='GDAS NDBC'

cd ${DATA}
touch ${DATA}/jobs/run_all_${RUN}_g2o_plots_poe.sh

export GRID2OBS_CONF="${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}"
MET_VERSION_major_minor=$(echo $MET_VERSION | sed "s/\([^.]*\.[^.]*\)\..*/\1/g")

# write the commands
for period in ${periods} ; do
  for valid_hour in ${valid_hours} ; do
    for wvar in ${wave_vars} ; do
      image_var=$(echo ${wvar} | tr '[A-Z]' '[a-z]')
      for stats in ${stats_list}; do
        for fhr in ${fhrs} ; do
          for obsname in $obsnames; do
              if [ $obsname = "GDAS" ]; then
                  OBTYPE="SFCSHP"
                  regions="GLOBAL"
              elif [ $obsname = "NDBC" ]; then
                  OBTYPE="NDBC_STANDARD"
                  regions="GLOBAL SEUS_CARB GOM NEUS_CAN WCOAST_AK HAWAII"
              fi
              obtypel=`echo $OBTYPE | tr '[A-Z]' '[a-z]'`
              for region in $regions; do
                  if [ $region = "GLOBAL" ]; then
                      regionl="glb"
                  else
                      regionl=`echo $region | tr '[A-Z]' '[a-z]'`
                  fi
                  echo "export VERIF_CASE=${VERIF_CASE} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export RUN=${RUN} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export COMPONENT=${COMPONENT}" >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export USHevs=${USHevs} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export FIXevs=${FIXevs}  " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export DATA=${DATA} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export MODNAM=${modnam_list} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export PERIOD=${period} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export VERIF_CASE=${VERIF_CASE} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export OBTYPE=${OBTYPE} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export plot_start_date=${VDATE_START} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export plot_end_date=${VDATE_END} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export VALID_HOUR=${valid_hour} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export REGION=${region} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export MET_VERSION_major_minor=${MET_VERSION_major_minor} " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  case ${stats} in
                    'stats1')
                      image_stat="me_rmse"
                      echo "export METRIC='me, rmse' " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                      ;;
                    'stats2')
                      image_stat="corr"
                      echo "export METRIC=corr " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                      ;;
                    'stats3')
                      image_stat="fbar_obar"
                      echo "export METRIC='fbar, obar' " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                      ;;
                    'stats4')
                      image_stat="esd"
                      echo "export METRIC=esd " >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                      ;;
                    'stats5')
                      image_stat="si"
                      echo "export METRIC=si "  >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                      ;;
                    'stats6')
                      image_stat="p95"
                      echo "export METRIC=p95 "  >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                      ;;
                  esac
                  echo "export FHR=${fhr}"        >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  echo "export WVAR=${wvar}"      >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  case ${wvar} in
                    'WIND')
                      image_level="z10"
                      echo "export OBS_LEVEL=Z10"  >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                      ;;
                    *)
                      image_level="l0"
                      echo "export OBS_LEVEL=L0"  >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                      ;;
                  esac
                  echo "export PTYPE=${ptype}" >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  # Make COMOUT restart directory
                  output_job_dir=$COMOUT/$VERIF_CASE/last${NDAYS}days/sl1l2/${image_var}_${image_level}/${regionl}/${image_stat}
                  mkdir -p $output_job_dir
                  #Define DATA and COMOUT image name
                  imagename=evs.${COMPONENT}.${image_stat}.${image_var}_${image_level}_${obtypel}.last${NDAYS}days.timeseries_valid${valid_hour}z_f${fhr}.latlon_0p25_${regionl}.png
                  output_image=$output_job_dir/$imagename
                  tmp_image=$DATA/images/$imagename
                  # Add commands
                  if [[ -s $output_image ]]; then
                      echo "cp -v $output_image $tmp_image" >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                  else
                      echo "${GRID2OBS_CONF}/py_plotting_wave.config"  >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                      echo "export err=\$?; err_chk" >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                      if [ $SENDCOM = YES ]; then
                          echo "if [ -f $tmp_image ]; then cp -v $tmp_image $output_image; fi" >> ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh
                      fi
                  fi

                  chmod +x ${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh

                  echo "${DATA}/jobs/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_${ptype}_${period}_${region}.sh" >> ${DATA}/jobs/run_all_${RUN}_g2o_plots_poe.sh
              done # end of regions
          done # end of obsnames
        done  # end of fcst hrs
      done  # end of stats
    done  # end of wave vars
  done  # end of valid hours
done  # end of periods


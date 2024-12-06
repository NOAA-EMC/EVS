#!/bin/bash
###############################################################################
# Name of Script: global_det_wave_copy_plots.sh
# Developers: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script generates the job scripts to create
#                    time series plots.
# Run By: scripts/plots/global_det/exevs_global_det_wave_grid2obs_plots.sh
###############################################################################

#################################
# Copy the plots to a common directory
#################################

set -x

# set up plot variables

periods="LAST${NDAYS}DAYS"

valid_hours='00 12'
fhrs='000 024 048 072 096 120 144 168
      192 216 240 264 288 312 336 360 384'
stats_list='stats1 stats2 stats3 stats4 stats5'
obsnames='GDAS NDBC JASON3'

for period in ${periods} ; do
  for valid_hour in ${valid_hours} ; do
    for obsname in $obsnames; do
      if [ $obsname = "GDAS" ]; then
          OBTYPE="SFCSHP"
          regions="GLOBAL"
          wave_vars='WIND HTSGW PERPW'
      elif [ $obsname = "NDBC" ]; then
          OBTYPE="NDBC_STANDARD"
          regions="GLOBAL SEUS_CARB GOM NEUS_CAN WCOAST_AK HAWAII"
          wave_vars='WIND HTSGW PERPW'
      elif [ $obsname = "JASON3" ]; then
          OBTYPE="JASON3"
          regions="GLOBAL"
          wave_vars='WIND HTSGW'
      fi
      obtypel=`echo $OBTYPE | tr '[A-Z]' '[a-z]'`
      for stats in ${stats_list}; do
        for wvar in ${wave_vars} ; do
          image_var=$(echo ${wvar} | tr '[A-Z]' '[a-z]')
          for region in $regions; do
            if [ $region = "GLOBAL" ]; then
                regionl="glb"
            else
                regionl=$(echo $region | tr '[A-Z]' '[a-z]')
            fi
            case ${stats} in
              'stats1')
                image_stat="me_rmse"
                ;;
              'stats2')
                image_stat="corr"
                ;;
              'stats3')
                image_stat="fbar_obar"
                ;;
              'stats4')
                image_stat="esd"
                ;;
              'stats5')
                image_stat="si"
                ;;
              'stats6')
                image_stat="p95"
                ;;
            esac
            case ${wvar} in
              'WIND')
                image_level="z10"
                ;;
              *)
                image_level="l0"
                ;;
            esac
            # Lead average plots
            imagename=evs.${COMPONENT}.${image_stat}.${image_var}_${image_level}_${obtypel}.last${NDAYS}days.fhrmean_valid${valid_hour}z_f384.latlon_0p25_${regionl}.png
            tmp_image=$DATA/images/$imagename
            job_work_dir=${DATA}/job_work_dir/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_${stats}_lead_average_${period}_${region}
            job_image=$job_work_dir/images/$imagename
            if [ ! -s $tmp_image ]; then
                if [ -s $job_image ]; then
                    cp -v $job_image $tmp_image
                else
                    echo "NOTE: $job_image does not exist"
                fi
            fi
            # Time series plots
            for fhr in ${fhrs} ; do
                imagename=evs.${COMPONENT}.${image_stat}.${image_var}_${image_level}_${obtypel}.last${NDAYS}days.timeseries_valid${valid_hour}z_f${fhr}.latlon_0p25_${regionl}.png
                tmp_image=$DATA/images/$imagename
                job_work_dir=${DATA}/job_work_dir/plot_obs${OBTYPE}_${wvar}_v${valid_hour}z_f${fhr}_${stats}_time_series_${period}_${region}
                job_image=$job_work_dir/images/$imagename
                if [ ! -s $tmp_image ]; then
                    if [ -s $job_image ]; then
                        cp -v $job_image $tmp_image
                    else
                        echo "NOTE: $job_image does not exist"
                    fi
                fi
            done  # end of fcst hrs
          done # end of regions
        done # end of wave vars
      done  # end of stats
    done  # end of obsname
  done  # end of valid hours
done  # end of periods

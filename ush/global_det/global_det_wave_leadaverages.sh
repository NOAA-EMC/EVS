#!/bin/bash
##############################################################
# Name of Script: global_det_wave_leadaverages.sh                    
# Deanna Spindler / Deanna.Spindler@noaa.gov                  
# Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: Make the lead_averages.py command files  
#                                                             

#################################
# Make the command files for cfp 
#################################

# set up plot variables

periods="PAST${NDAYS}DAYS"

valid_hours='00 12'
fhrs='000,024,048,072,096,120,144,168,192,216,240,264,288,312,336,360,384'
wave_vars='WIND HTSGW PERPW'
stats_list='stats1 stats2 stats3 stats4 stats5'
ptype='lead_average'

export GRID2OBS_CONF="${PARMevs}/metplus_config/${COMPONENT}/${RUN}_${VERIF_CASE}/${STEP}"

cd ${DATA}
touch ${DATA}/jobs/run_all_${RUN}_g2o_plots_poe.sh

# write the commands
for period in ${periods} ; do
  for vhr in ${valid_hours} ; do
    for wvar in ${wave_vars} ; do
      image_var=$(echo ${wvar} | tr '[A-Z]' '[a-z]')
      for stats in ${stats_list}; do
        echo "export VERIF_CASE=${VERIF_CASE} " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export RUN=${RUN} " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export COMPONENT=${COMPONENT}" >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export USHevs=${USHevs} " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export FIXevs=${FIXevs}  " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export DATA=${DATA} " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export MODNAM=${modnam_list} " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export PERIOD=${period} " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export VERIF_CASE=${VERIF_CASE} " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export plot_start_date=${VDATE_START} " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export plot_end_date=${VDATE_END} " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export VHR=${vhr} " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        case ${stats} in
          'stats1')
            image_stat="me_rmse"
            echo "export METRIC='me, rmse' " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
            ;;
          'stats2')
            image_stat="corr"
            echo "export METRIC=corr " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
            ;;
          'stats3')
            image_stat="fbar_obar"
            echo "export METRIC='fbar, obar' " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
            ;;
          'stats4')
            image_stat="esd"
            echo "export METRIC=esd " >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
            ;; 
          'stats5')
            image_stat="si"
            echo "export METRIC=si "  >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
            ;;
          'stats6')
            image_stat="p95"
            echo "export METRIC=p95 "  >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
            ;;
        esac
        echo "export FHR='000,024,048,072,096,120,144,168,192,216,240,264,288,312,336,360,384'" >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        echo "export WVAR=${wvar}"      >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        case ${wvar} in
          'WIND')
            image_level="z10"
            echo "export OBS_LEVEL=Z10"  >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
            ;;
          *)
            image_level="l0"
            echo "export OBS_LEVEL=L0"  >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
            ;;
        esac
        echo "export PTYPE=${ptype}" >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        # Make COMOUT restart directory
        COMOUTjob=$COMOUT/$VERIF_CASE/last${NDAYS}days/sl1l2/${image_var}_${image_level}/glb/${image_stat}
        mkdir -p $COMOUTjob
        #Define DATA and COMOUT image name
        imagename=evs.${COMPONENT}.${image_stat}.${image_var}_${image_level}_sfcshp.past${NDAYS}days.fhrmean_valid${vhr}z_f384.glb.png
        COMOUTimage=$COMOUTjob/$imagename
        DATAimage=$DATA/images/$imagename
        # Add commands
        if [[ -s $COMOUTimage ]]; then
            echo "cp -v $COMOUTimage $DATAimage" >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        else
            echo "${GRID2OBS_CONF}/py_plotting_wave.config"  >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
            echo "export err=$?; err_chk" >> ${DATA}/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
            if [ $SENDCOM = YES ]; then
                echo "cp -v $DATAimage $COMOUTimage" >> ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
                echo "export err=$?; err_chk" >> ${DATA}/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
            fi
        fi
        
        chmod +x ${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh
        
        echo "${DATA}/jobs/plot_${wvar}_v${vhr}z_${stats}_${ptype}_${period}.sh" >> ${DATA}/jobs/run_all_${RUN}_g2o_plots_poe.sh
        
      done  # end of stats
    done  # end of wave vars
  done  # end of valid hours
done  # end of periods
  

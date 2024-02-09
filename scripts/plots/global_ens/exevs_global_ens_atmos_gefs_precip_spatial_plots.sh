#!/bin/bash
#*******************************************************************************
# Purpose: setup environment, paths, and run the global_ens precip spatial map
#          plotting python script
#
# Last updated: 11/17/2023, Binbin Zhou Lynker@EMC/NCEP 
#******************************************************************************
set -x 

cd $DATA

export machine=WCOSS2

#***************************************
#Set required parameters
#***************************************
export VERIF_CASE=grid2grid
export evs_run_mode=production
export plot_verbosity=INFO
export JOB_GROUP=plot
export VERIF_TYPE=precip
export job_var=24hrAccumMaps
export fhr_start=24
export fhr_end=240
export fhr_inc=24
export valid_hr_start=12
export valid_hr_end=12
export valid_hr_inc=24
export init_hr_start=12
export init_hr_end=12
export init_hr_inc=24
export model_list='gefs cmce ecme naefs'
export model_plot_name_list='gefs cmce ecme naefs'
export obs_name=24hrCCPA
export event_equalization=NO
export start_date=$VDATE
export end_date=$VDATE
export date_type=VALID
export grid=G211
export fcst_var_name=APCP
export fcst_var_level_list='A24'
export fcst_var_thresh_list='NA'
export obs_var_name=APCP
export obs_var_level_list='A24'
export obs_var_thresh_list='NA'
export interp_method=NEAREST
export interp_points_list='1'
export line_type=SL1L2
export stat=FBAR
export vx_mask=CONUS
export plots_list=precip_spatial_map
export job_name=SL1L2/FBAR/24hrAccumMaps/CONUS/precip_spatial_map

mkdir -p $DATA/grid2grid_plots/plot_output/atmos.${VDATE}/logs

#**********************************************
# Link 24hr APCP ensemble mean netCDF files
# *********************************************
for model in $model_list ; do
 MODEL=`echo $model | tr '[a-z]' '[A-Z]'`	
 source=$EVSINapcp24mean/${model}
 target=$DATA/grid2grid_plots/data/$model
 mkdir -p $target
 for fhr in 024 048 072 096 120 144 168 192 216 240 ; do
  past=`$NDATE -$fhr ${VDATE}12`	
  INITDATE=${past:0:8}
  apcp24mean=$source/GenEnsProd_${MODEL}_APCP24_FHR${fhr}_${VDATE}_120000V_ens.nc
  if [ -f $apcp24mean ]; then
      size=`ls -l $apcp24mean | awk '{ print $5}'`
      if [ $size -gt 1000000 ] ; then
          ln -sf $source/GenEnsProd_${MODEL}_APCP24_FHR${fhr}_${VDATE}_120000V_ens.nc $target/${model}_precip_24hrAccum_init${INITDATE}12_fhr${fhr}.nc
      else
          echo "$apcp24mean SIZE LESS THAN 1000000"
      fi
  else
      echo "$apcp24mean DOES NOT EXIST"
  fi 
 done
done

#*************************************
# Run plotting script
#*************************************
python $USHevs/global_ens/ush_gens_plot_py/global_ens_atmos_plots.py
export err=$?; err_chk

# Cat the plotting log files
log_dir=$DATA/grid2grid_plots/plot_output/atmos.${VDATE}/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
    for log_file in $log_dir/*; do
        echo "Start: $log_file"
        cat $log_file
        echo "End: $log_file"
    done
fi

cd $DATA/grid2grid_plots/plot_output/atmos.${VDATE}/precip/SL1L2_FBAR_24hrAccumMaps_CONUS_precip_spatial_map/images
if ls *.gif 1> /dev/null 2>&1; then
   tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.precip_spatial.v${VDATE}.tar *.gif
else
   err_exit "No .gif files were found in $DATA/grid2grid_plots/plot_output/atmos.${VDATE}/precip/SL1L2_FBAR_24hrAccumMaps_CONUS_precip_spatial_map/images"
fi

if [ $SENDCOM = YES ]; then
    if [ -s evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.precip_spatial.v${VDATE}.tar ]; then
        cp -v evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.precip_spatial.v${VDATE}.tar  $COMOUT/.
    fi
fi
if [ $SENDDBN = YES ]; then 
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.precip_spatial.v${VDATE}.tar
fi


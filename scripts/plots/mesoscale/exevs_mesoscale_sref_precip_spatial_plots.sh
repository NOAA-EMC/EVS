#!/bin/bash
#*******************************************************************************
# Purpose: setup environment, paths, and run the sref precip spatial map 
#           plotting python script
# Last updated: 10/27/2023, Binbin Zhou Lynker@EMC/NCEP
# ******************************************************************************
set -x 

export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH
cd $DATA

export machine=WCOSS2

export VERIF_CASE=grid2grid
export evs_run_mode=production
export plot_verbosity=INFO
export JOB_GROUP=plot
export VERIF_TYPE=precip
export job_var=24hrAccumMaps
export fhr_start=24
export fhr_end=72
export fhr_inc=24
export valid_hr_start=12
export valid_hr_end=12
export valid_hr_inc=24
export init_hr_start=12
export init_hr_end=12
export init_hr_inc=24
export model_list='sref'
export model_plot_name_list='sref'
export obs_name=24hrCCPA
export event_equalization=NO
export start_date=$VDATE
export end_date=$VDATE
export date_type=VALID
export grid=G270
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

#*************************************************************************
# Virtual link the  sref's stat data files of past 90 days 
#**************************************************************************
for model in $model_list ; do
 MODEL=`echo $model | tr '[a-z]' '[A-Z]'`	
 target=$DATA/grid2grid_plots/data/$model
 mkdir -p $target
 for fhr in 24 48 72 ; do
  past=`$NDATE -$fhr ${VDATE}12`	
  INITDATE=${past:0:8}
  source=$EVSINapcp24mean/sref.$INITDATE/apcp24mean
  if [ -s $source/${model}.t12z.pgrb212.24mean.f${fhr}.nc ] ; then
    ln -sf $source/${model}.t12z.pgrb212.24mean.f${fhr}.nc $target/${model}_precip_24hrAccum_init${INITDATE}12_fhr0${fhr}.nc
  fi
 done
done

#******************************************************************
# Run spatial map python script
# *****************************************************************
python $USHevs/mesoscale/ush_sref_plot_precip_py/sref_atmos_plots.py 
export err=$?; err_chk

cd $DATA/grid2grid_plots/plot_output/atmos.${VDATE}/precip/SL1L2_FBAR_24hrAccumMaps_CONUS_precip_spatial_map/images

tar -cvf evs.plots.sref.precip.spatial.map.v${VDATE}.tar *.gif

if [ $SENDCOM = YES ] && [ -s evs.plots.sref.precip.spatial.map.v${VDATE}.tar ] ; then
 cp -v evs.plots.sref.precip.spatial.map.v${VDATE}.tar  $COMOUTplots/.  
fi

if [ $SENDDBN = YES ] ; then
   $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.sref.precip.spatial.map.v${VDATE}.tar
fi




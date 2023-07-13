#!/bin/bash

set -x 

cd $DATA

export machine=WCOSS2
export COMROOT=${COMROOT:-$(compath.py $envir/com)}

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

for model in $model_list ; do
 MODEL=`echo $model | tr '[a-z]' '[A-Z]'`	
 source=$COMINapcp24mean/${model}
 target=$DATA/grid2grid_plots/data/$model
 mkdir -p $target
 for fhr in 024 048 072 096 120 144 168 192 216 240 ; do
  past=`$NDATE -$fhr ${VDATE}12`	
  INITDATE=${past:0:8}
  apcp24mean=$source/GenEnsProd_${MODEL}_APCP24_FHR${fhr}_${VDATE}_120000V_ens.nc
  size=`ls -l $apcp24mean | awk '{ print $5}'`
  if [ $size -gt 1000000 ] ; then
    ln -sf $source/GenEnsProd_${MODEL}_APCP24_FHR${fhr}_${VDATE}_120000V_ens.nc $target/${model}_precip_24hrAccum_init${INITDATE}12_fhr${fhr}.nc	
  fi 
 done
done

source=$COMINccpa24/gefs
target=$DATA/grid2grid_plots/data/ccpa
mkdir -p $target
if [ -s $source/ccpa.t12z.grid3.24h.f00.nc ] ; then
 ln -sf $source/ccpa.t12z.grid3.24h.f00.nc $target/ccpa_precip_24hrAccum_valid${VDATE}12.nc
fi 

python $USHevs/global_ens/ush_gens_plot_py/global_det_atmos_plots.py

cd $DATA/grid2grid_plots/plot_output/atmos.${VDATE}/precip/SL1L2_FBAR_24hrAccumMaps_CONUS_precip_spatial_map/images
mask=`echo $vx_mask | tr '[A-Z]' '[a-z]'`
for model in $model_list ; do
  for fhr in 024 048 072 096 120 144 168 192 216 240 ; do
    past=`$NDATE -$fhr ${VDATE}12`
    INITDATE=${past:0:8}    
    #mv ${model}.v${VDATE}12.${fhr}h.${mask}.png  evs.${model}.spatial_map.apcp_a24.init${INITDATE}.vlid${VDATE}12.f${fhr}.buk_${mask}.png
    mv ${model}.v${VDATE}12.${fhr}h.${mask}.png  evs.${model}.spatial_map.apcp_a24.vlid12z_f${fhr}.buk_${mask}.png
  done
done  

#scp *.png wd20bz@emcrzdm:/home/people/emc/www/htdocs/bzhou/evs_plots/gens/spaticl

tar -cvf evs.plots.gefs.precip.spatial.map.v${VDATE}.tar *.png

cp evs.plots.gefs.precip.spatial.map.v${VDATE}.tar  $COMOUT/.  







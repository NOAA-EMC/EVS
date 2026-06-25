#!/bin/bash

set -eu

ECF_DIR=$(pwd)

# Function that loop over forecast cycles and
# creates link between the master and target
function link_master_to_cyc(){
  tmpl=$1  # Name of the master template
  cycs=$2  # Array of cycles
  for cyc in ${cycs[@]}; do
    cycchar=$(printf %02d $cyc)
    master=${tmpl}_master.ecf
    target=${tmpl}_${cycchar}.ecf
    rm -f $target
    ln -sf $master $target
  done
}

# CAM files
cd $ECF_DIR/scripts/prep/cam
echo "Linking CAM prep ..."
cyc=$(seq 0 23)
link_master_to_cyc "jevs_prep_cam_radar_vhr" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_prep_cam_rrfs_precip_vhr" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_prep_cam_rrfsmem_precip_vhr" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_prep_cam_hrrr_precip_vhr" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_prep_cam_hrrr_severe_vhr" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_prep_cam_rrfs_severe_vhr" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_prep_cam_rrfsmem_severe_vhr" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_prep_cam_refs_severe_vhr" "$cyc"
cd $ECF_DIR/scripts/stats/cam
echo "Linking CAM stats ..."
cyc=$(seq 0 23)
link_master_to_cyc "jevs_stats_cam_rrfs_firewxnest_grid2obs_vhr" "$cyc"
cyc=$(seq 0 23)
link_master_to_cyc "jevs_stats_cam_refs_radar_vhr" "$cyc"
cyc=$(seq 0 23)
link_master_to_cyc "jevs_stats_cam_hrrr_radar_vhr" "$cyc"
cyc=$(seq 0 23)
link_master_to_cyc "jevs_stats_cam_rrfs_radar_vhr" "$cyc"
cyc=$(seq 0 23)
link_master_to_cyc "jevs_stats_cam_rrfsmem_radar_vhr" "$cyc"
cyc=$(seq 19 22)
link_master_to_cyc "jevs_stats_cam_hrrr_precip_vhr" "$cyc"
cyc=$(seq 19 22)
link_master_to_cyc "jevs_stats_cam_rrfs_precip_vhr" "$cyc"
cyc=$(seq 19 22)
link_master_to_cyc "jevs_stats_cam_rrfsmem_precip_vhr" "$cyc"
cyc=$(seq 2 3)
link_master_to_cyc "jevs_stats_cam_hrrr_grid2obs_vhr" "$cyc"
cyc=$(seq 6 3 23)
link_master_to_cyc "jevs_stats_cam_hrrr_grid2obs_vhr" "$cyc"
cyc=$(seq 2 3)
link_master_to_cyc "jevs_stats_cam_rrfs_grid2obs_vhr" "$cyc"
cyc=$(seq 6 3 23)
link_master_to_cyc "jevs_stats_cam_rrfs_grid2obs_vhr" "$cyc"
cyc=$(seq 2 3)
link_master_to_cyc "jevs_stats_cam_rrfsmem_grid2obs_vhr" "$cyc"
cyc=$(seq 6 3 23)
link_master_to_cyc "jevs_stats_cam_rrfsmem_grid2obs_vhr" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_stats_cam_hrrr_snowfall_vhr" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_stats_cam_rrfs_snowfall_vhr" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_stats_cam_rrfsmem_snowfall_vhr" "$cyc"
cyc=$(seq 0 23)
link_master_to_cyc "jevs_stats_cam_rap_precip_vhr" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_stats_cam_rap_snowfall_vhr" "$cyc"

# AQM files
cd $ECF_DIR/scripts/stats/aqm
echo "Linking AQM stats ..."
cyc=$(seq 0 23)
link_master_to_cyc "jevs_stats_aqm_atmos_grid2grid_vhr" "$cyc"
cyc=$(seq 0 23)
link_master_to_cyc "jevs_stats_aqm_atmos_grid2obs_vhr" "$cyc"

# ANALYSES files
cd $ECF_DIR/scripts/stats/analyses
echo "Linking ANALYSES stats ..."
cyc=$(seq 0 23)
link_master_to_cyc "jevs_stats_analyses_urma_grid2obs_vhr" "$cyc"
cyc=$(seq 0 23)
link_master_to_cyc "jevs_stats_analyses_rtma_ru_grid2obs_vhr" "$cyc"
cyc=$(seq 0 23)
link_master_to_cyc "jevs_stats_analyses_rtma_grid2obs_vhr" "$cyc"

# GLOBAL-CHEM files
cd $ECF_DIR/scripts/stats/global_chem
echo "Linking GLOBAL_CHEM stats ..."
cyc=$(seq 0 3 21)
link_master_to_cyc "jevs_stats_global_chem_atmos_grid2obs_aeronet_vhr" "$cyc"
cyc=$(seq 0 3 21)
link_master_to_cyc "jevs_stats_global_chem_atmos_grid2obs_airnow_vhr" "$cyc"

echo "Done."

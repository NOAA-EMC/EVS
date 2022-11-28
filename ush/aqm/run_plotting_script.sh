#!/bin/sh -e
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## CAM_verif Plotting Set Up
##
## CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Used to configure and run CAM_verif plotting scripts.
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

# Settings
export MET_VERSION="10.0"
export VERIF_CASE="grid2obs"
export VERIF_TYPE="upper_air"
export URL_HEADER="fv3cam"
export USH_DIR="${NOSCRUB}/CAM_verif/plotting_scripts/stats"
export OUTPUT_BASE_DIR="/gpfs/dell2/emc/verification/noscrub/Perry.Shafran/metplus_cam/stat/"
export PRUNE_DIR="${NOSCRUB}/CAM_verif/data"
export SAVE_DIR="${NOSCRUB}/CAM_verif/out"
export LOG_METPLUS="${SAVE_DIR}/logs/CAM_verif_plotting_job_`date '+%Y%m%d-%H%M%S'`.out"
export LOG_LEVEL="INFO"
export MODEL="FV3LAM, FV3LAMX"
export FCST_VALID_HOUR="12"
export FCST_INIT_HOUR="12"
export VALID_BEG=""
export VALID_END=""
export INIT_BEG=""
export INIT_END=""
export EVAL_PERIOD="PAST30DAYS"
export DATE_TYPE="INIT"
export FCST_LEVEL="P1000,P925,P850,P700,P500,P400,P300,P250,P200,P150,P100,P50"
export OBS_LEVEL="P1000,P925,P850,P700,P500,P400,P300,P250,P200,P150,P100,P50"
export var_name="HGT, TMP, SPFH"
export VX_MASK_LIST="conus"
export FCST_LEAD="60"
export STATS="bias"
export LINE_TYPE="sl1l2"
export INTERP="BILIN"
export FCST_THRESH=""
export OBS_THRESH=""

# Uncomment below to run
#python $NOSCRUB/CAM_verif/plotting_scripts/stats/stat_by_level.py
python $NOSCRUB/CAM_verif/plotting_scripts/stats/time_series.py
#python $NOSCRUB/CAM_verif/plotting_scripts/stats/lead_average.py
#python $NOSCRUB/CAM_verif/plotting_scripts/stats/daily_cycle_average.py
#python $NOSCRUB/CAM_verif/plotting_scripts/stats/threshold_average.py
#python $NOSCRUB/CAM_verif/plotting_scripts/stats/performance_diagram.py

#!/bin/sh -e
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC VERIFICATION SYSTEM (CFS SUBSEASONAL)	
##
## CONTRIBUTORS: Shannon Shields, Shannon.Shields@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
## PURPOSE: Used to run the EVS package in stand alone mode.
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

export HOMEevs=`eval "cd ../../;pwd"`  # Home base of evs

echo "=============== SOURCING CONFIGS ==============="
passed_config=$1
passed_config_strlength=$(echo -n $passed_config | wc -m)
if [ $passed_config_strlength = 0 ]; then
    export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.cfs
    echo "No config passed, using default: $config"
else
    export config=$(readlink -f $passed_config)
    if [ ! -e $config ]; then
	echo "The passed config $config does not exist"
	exit 1
    else
        echo "Using passed config: $config"
    fi
fi
. $config
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully sourced ${config}"
echo

echo "=============== SETTING UP ==============="
. $HOMEevs/ush/subseasonal/set_up_subseasonal_evs.sh
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran set_up_subseasonal_evs.sh"

echo "=============== RUNNING METPLUS ==============="
if [ $RUN_GRID2GRID_STATS = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-GRID STATS VERIFICATION  ====="
    echo "===== creating partial sum data for grid-to-grid verification using METplus ====="
    export VERIF_CASE="grid2grid"
    export STEP="stats"
    python $HOMEevs/ush/subseasonal/run_subseasonal_batch_stats.py
fi

if [ $RUN_GRID2GRID_PLOTS = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-GRID PLOTS VERIFICATION  ====="
    echo "===== calculating statistics and creating plots for grid-to-grid verification using METplus ====="
    export VERIF_CASE="grid2grid"
    export STEP="plots"
    python $HOMEevs/ush/subseasonal/run_subseasonal_batch_plots.py
fi

if [ $RUN_GRID2OBS_STATS = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-OBSERVATIONS STATS VERIFICATION  ====="
    echo "===== creating partial sum data for grid-to-observations verification using METplus ====="
    export VERIF_CASE="grid2obs"
    export STEP="stats"
    python $HOMEevs/ush/subseasonal/run_subseasonal_batch_stats.py
fi

if [ $RUN_GRID2OBS_PLOTS = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-OBSERVATIONS PLOTS VERIFICATION  ====="
    echo "===== calculating statistics and creating plots for grid-to-observations verification using METplus ====="
    export VERIF_CASE="grid2obs"
    export STEP="plots"
    python $HOMEevs/ush/subseasonal/run_subseasonal_batch_plots.py
fi

#if [ $RUN_PRECIP_STATS = YES ] ; then
    #echo
    #echo "===== RUNNING PRECIPITATION STATS VERIFICATION  ====="
    #echo "===== creating partial sum data for precipitation verification using METplus ====="
    #export VERIF_CASE="precip"
    #export STEP="stats"
    #python $HOMEevs/ush/subseasonal/run_subseasonal_batch_stats.py
#fi

#if [ $RUN_PRECIP_PLOTS = YES ] ; then
    #echo
    #echo "===== RUNNING PRECIPITATION PLOTS VERIFICATION  ====="
    #echo "===== calculating statistics and creating plots for precipitation verification using METplus ====="
    #export VERIF_CASE="precip"
    #export STEP="plots"
    #python $HOMEevs/ush/subseasonal/run_subseasonal_batch_plots.py
#fi

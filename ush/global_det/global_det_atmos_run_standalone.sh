#!/bin/sh -e
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC Verification System (EVS) - Global Deterministic Atmospheric
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, IMSG @ NOAA/NWS/NCEP/EMC-VPPPGB
## PURPOSE: Used to run the EVS in standalone mode for 
##          Global Deterministic Atmospheric component verification jobs
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

export HOMEevs=`eval "cd ../../;pwd"`  # Home base of EVS

echo "=============== SOURCING CONFIGS ==============="
passed_config=$1
passed_config_strlength=$(echo -n $passed_config | wc -m)
if [ $passed_config_strlength = 0 ]; then
    export config=$HOMEevs/parm/evs_config/global_det/config.evs.global_det_atmos.standalone
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
[[ $status -eq 0 ]] && echo "Succesfully sourced ${config}"
echo

echo "=============== SETTING UP ==============="
. $HOMEevs/ush/global_det/global_det_atmos_set_up.sh
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_set_up.sh"

if [ $RUN_GRID2GRID_STATS = YES ] ; then
    echo
    echo "===== SUBMITTING GRID-TO-GRID STATISTICS GENERATION JOB ====="
    export VERIF_CASE="grid2grid"
    export STEP="stats"
    python $HOMEevs/ush/global_det/global_det_atmos_submit_batch_job.py
fi

if [ $RUN_GRID2GRID_PLOTS = YES ] ; then
    echo
    echo "===== SUBMITTING GRID-TO-GRID PLOTS GENERATION JOB ====="
    export VERIF_CASE="grid2grid"
    export STEP="plots"
    python $HOMEevs/ush/global_det/global_det_atmos_submit_batch_job.py
fi

if [ $RUN_GRID2OBS_STATS = YES ] ; then
    echo
    echo "===== SUBMITTING GRID-TO-OBSERVATIONS STATISTICS GENERATION JOB ====="
    export VERIF_CASE="grid2obs"
    export STEP="stats"
    python $HOMEevs/ush/global_det/global_det_atmos_submit_batch_job.py
fi

if [ $RUN_GRID2OBS_PLOTS = YES ] ; then
    echo
    echo "===== SUBMITTING GRID-TO-OBSERVATIONS PLOTS GENERATION JOB ====="
    export VERIF_CASE="grid2obs"
    export STEP="plots"
    python $HOMEevs/ush/global_det/global_det_atmos_submit_batch_job.py
fi

#!/bin/bash -e

# =============================================================================
#
# NAME: exevs_hireswarwmem2_grid2obs_prep.sh
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Handle all components of an EVS HiRes Window ARW2 Grid2Obs - Prep job
# DEPENDENCIES: $HOMEevs/jobs/cam/prep/JEVS_CAM_PREP 
#
# =============================================================================

set -x

# Set Basic Environment Variables
NEST_LIST="spc_otlk"

# Loop through HiRes Window ARW2 Grid2Obs configs
export njob=1
for NEST in $NEST_LIST; do
    export NEST=$NEST
    if [ $RUN_ENVIR = nco ]; then
        export evs_run_mode="production"
        source $config
    else
        export evs_run_mode=$evs_run_mode
        source $config
    fi
    echo "RUN MODE: $evs_run_mode"
 
    # Check User's Configuration Settings
    python $USHevs/cam/cam_check_settings.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran cam_check_settings.py"
    echo
 
    # Create Output Directories
    python $USHevs/cam/cam_create_output_dirs.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran cam_create_output_dirs.py" 
    
    for DAY in $DAYS; do
        export DAY=$DAY
        for VHOUR_GROUP in $VHOUR_GROUPS; do
            export VHOUR_GROUP=$VHOUR_GROUP
            # Create Job Script 
            python $USHevs/cam/cam_prep_grid2obs_create_job_script.py
            status=$?
            [[ $status -ne 0 ]] && exit $status
            [[ $status -eq 0 ]] && echo "Successfully ran cam_prep_grid2obs_create_job_script.py"
            export njob=$((njob+1))
        done
    done
done

# Create POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/cam/cam_prep_grid2obs_create_poe_job_scripts.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran cam_prep_grid2obs_create_poe_job_scripts.py"
fi

# Run all HiRes Window ARW2 grid2obs/prep jobs
chmod u+x ${DATA}/${VERIF_CASE}/${STEP}/prep_job_scripts/*
ncount_job=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/prep_job_scripts/job* |wc -l)
nc=1
if [ $USE_CFP = YES ]; then
    ncount_poe=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/prep_job_scripts/poe* |wc -l)
    while [ $nc -le $ncount_poe ]; do
        poe_script=${DATA}/${VERIF_CASE}/${STEP}/prep_job_scripts/poe_jobs${nc}
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        if [ $machine = WCOSS2 ]; then
            export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
            launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,depth cfp"
        elif [$machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
            export SLURM_KILL_BAD_EXIT=0
            launcher="srun --export=ALL --multi-prog"
        else
            echo "Cannot submit jobs to scheduler on this machine.  Set USE_CFP=NO and retry."
            exit 1    
        fi
        $launcher $MP_CMDFILE
        nc=$((nc+1))
    done
else
    set +x
    while [ $nc -le $ncount_job ]; do
        ${DATA}/${VERIF_CASE}/${STEP}/prep_job_scripts/job${nc}
        nc=$((nc+1))
    done
    set -x
fi

sleep 4
for NEST in $NEST_LIST; do
    export NEST=$NEST
    if [ $RUN_ENVIR = nco ]; then
        export evs_run_mode="production"
        source $config
    else
        export evs_run_mode=$evs_run_mode
        source $config
    fi
    # Copy files to desired location
    #all commands to copy output files into the correct EVS COMOUT directory
    if [ $SENDCOM = YES ]; then
        for OBS_DIR_PATH in $DATA/$VERIF_CASE/data/*; do
            OBS_DIR=$(echo ${OBS_DIR_PATH##*/})
            mkdir -p $COMOUT/$OBS_DIR
            for FILE in $OBS_DIR_PATH/*; do
                cp -v $FILE $COMOUT/$OBS_DIR/.
            done
        done
    fi

done

# Non-production jobs
#things to do if evs_run_mode != "production" (i.e., RUN_ENVIR != nco)
#if [ $evs_run_mode != "production" ]; then
#    if [ $SEND

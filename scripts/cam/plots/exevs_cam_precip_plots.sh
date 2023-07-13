#!/bin/bash -e

# =============================================================================
#
# NAME: exevs_cam_precip_plots.sh
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Handle all components of an EVS CAM Precipitation - Plots job
# DEPENDENCIES: $HOMEevs/jobs/cam/plots/JEVS_CAM_PLOTS 
#
# =============================================================================

set -x

# Set Basic Environment Variables

export njob=1
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

# Create Job Script 
python $USHevs/cam/cam_plots_precip_create_job_scripts.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran cam_plots_precip_create_job_scripts.py"
export njob=$((njob+1))

# Create POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/cam/cam_plots_precip_create_poe_job_scripts.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran cam_plots_precip_create_poe_job_scripts.py"
fi

# Run All CAM precip/plots Jobs
chmod u+x ${DATA}/${VERIF_CASE}/${STEP}/plotting_job_scripts/*
ncount_job=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/plotting_job_scripts/job* |wc -l)
nc=1
if [ $USE_CFP = YES ]; then
    ncount_poe=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/plotting_job_scripts/poe* |wc -l)
    while [ $nc -le $ncount_poe ]; do
        poe_script=${DATA}/${VERIF_CASE}/${STEP}/plotting_job_scripts/poe_jobs${nc}
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
        ${DATA}/${VERIF_CASE}/${STEP}/plotting_job_scripts/job${nc}
        nc=$((nc+1))
    done
    set -x
fi

# Copy files to desired location
#all commands to copy output files into the correct EVS COMOUT directory
if [ $SENDCOM = YES ]; then
    find ${DATA}/${VERIF_CASE}/out/*/*/*.png -type f -print | tar -cvf ${COMOUT}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.v${VDATE}.tar -T -
fi

# Non-production jobs
#things to do if evs_run_mode != "production" (i.e., RUN_ENVIR != nco)
#if [ $evs_run_mode != "production" ]; then
#    if [ $SEND

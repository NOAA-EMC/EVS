#!/bin/bash -e

# =============================================================================
#
# NAME: exevs_cam_precip_plots.sh
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Handle all components of an EVS CAM Precipitation - Plots job
# DEPENDENCIES: $HOMEevs/jobs/JEVS_CAM_PLOTS 
#
# =============================================================================

set -x

# Set Basic Environment Variables

export machine=${machine:-"WCOSS2"}
export PYTHONPATH=$USHevs/$COMPONENT:$PYTHONPATH
export njob=1
source $config
# Check User's Configuration Settings
python $USHevs/cam/cam_check_settings.py
export err=$?; err_chk

# Create Output Directories
python $USHevs/cam/cam_create_output_dirs.py
export err=$?; err_chk

# Check For Restart Files
python ${USHevs}/cam/cam_production_restart.py
export err=$?; err_chk

# Create Job Script 
python $USHevs/cam/cam_plots_precip_create_job_scripts.py
export err=$?; err_chk
export njob=$((njob+1))

# Create POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/cam/cam_plots_precip_create_poe_job_scripts.py
    export err=$?; err_chk
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
            launcher="mpiexec -np $nproc -ppn $ncpu --cpu-bind verbose,depth cfp"
        elif [$machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
            export SLURM_KILL_BAD_EXIT=0
            launcher="srun --export=ALL --multi-prog"
        else
            err_exit "Cannot submit jobs to scheduler on this machine.  Set USE_CFP=NO and retry."
        fi
        $launcher $MP_CMDFILE
        nc=$((nc+1))
    done
else
    set -x
    while [ $nc -le $ncount_job ]; do
        ${DATA}/${VERIF_CASE}/${STEP}/plotting_job_scripts/job${nc}
        nc=$((nc+1))
    done
    set -x
fi

# Cat the plotting log files
log_dir="$DATA/$VERIF_CASE/out/logs"
if [ -d $log_dir ]; then
    log_file_count=$(find $log_dir -type f | wc -l)
    if [[ $log_file_count -ne 0 ]]; then
        log_files=("$log_dir"/*)
        for log_file in "${log_files[@]}"; do
            if [ -f "$log_file" ]; then
                echo "Start: $log_file"
                cat "$log_file"
                echo "End: $log_file"
            fi
        done
    fi
fi

# Tar and Copy output files to EVS COMOUT directory
   find ${DATA}/${VERIF_CASE}/* -type f \( -name "*.png" -o -name "*.gif"  \) -print | tar -cvf ${DATA}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.v${VDATE}.tar --transform='s#.*/##' -T -

if [ $SENDCOM = YES ]; then
    FILE=${DATA}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.v${VDATE}.tar
    if [ -s "$FILE" ]; then
       cp -v ${FILE} ${COMOUTplots}/.
    fi
fi
if [ $SENDDBN = YES ]; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job ${COMOUTplots}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.v${VDATE}.tar
fi

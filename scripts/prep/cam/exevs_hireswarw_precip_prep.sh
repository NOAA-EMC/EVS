#!/bin/bash -e

# =============================================================================
#
# NAME: exevs_hireswarw_precip_prep.sh
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Handle all components of an EVS HiRes Window ARW Precipitation - 
#          Prep job
# DEPENDENCIES: $HOMEevs/jobs/JEVS_CAM_PREP
#
# =============================================================================

set -x

# Loop through HiRes Window ARW Precipitation configs
export machine=${machine:-"WCOSS2"}
export PYTHONPATH=$USHevs/$COMPONENT:$PYTHONPATH
export njob=1
for NEST in "conus" "ak" "pr" "hi"; do
    export NEST=$NEST
    for ACC in "24"; do
        export ACC=$ACC
        source $config
 
        # Check User's Configuration Settings
        python $USHevs/cam/cam_check_settings.py
        export err=$?; err_chk
 
        # Create Output Directories
        python $USHevs/cam/cam_create_output_dirs.py
        export err=$?; err_chk
 
        # Create Job Script 
        python $USHevs/cam/cam_prep_precip_create_job_script.py
        export err=$?; err_chk
        export njob=$((njob+1))
    done
done

# Create POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/cam/cam_prep_precip_create_poe_job_scripts.py
    export err=$?; err_chk
fi

# Run all Hires Window ARW precip/prep jobs
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
            launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,core cfp"
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
    while [ $nc -le $ncount_job ]; do
        ${DATA}/${VERIF_CASE}/${STEP}/prep_job_scripts/job${nc}
        export err=$?; err_chk
        nc=$((nc+1))
    done
fi

for NEST in "conus" "ak" "pr" "hi"; do
    export NEST=$NEST
    source $config
    # Copy files to desired location
    #all commands to copy output files into the correct EVS COMOUT directory
    if [ $SENDCOM = YES ]; then
        for OBS_DIR_PATH in $DATA/$VERIF_CASE/data/$VERIF_TYPE/*; do
            OBS_DIR=$(echo ${OBS_DIR_PATH##*/})
            mkdir -p $COMOUT/$OBS_DIR
            if [ ! -z "$(ls -A $OBS_DIR_PATH)" ]; then
                for FILE in $OBS_DIR_PATH/*; do
                    if [ -s "$FILE" ]; then
                       cp -v $FILE $COMOUT/$OBS_DIR/.
                    fi
                done
            fi
        done
    fi

done

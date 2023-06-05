#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_atmos_grid2grid_stats.sh 
# Purpose of Script: This script generates grid-to-grid
#                    verification statistics using METplus for the
#                    atmospheric component of global deterministic models
# Log history:
###############################################################################

set -x

export VERIF_CASE_STEP_abbrev="g2gs"

# Set run mode
if [ $RUN_ENVIR = nco ]; then
    export evs_run_mode="production"
    source $config
else
    export evs_run_mode=$evs_run_mode
fi
echo "RUN MODE:$evs_run_mode"

# Make directory
mkdir -p ${VERIF_CASE}_${STEP}

# Check user's config settings
python $USHevs/global_det/global_det_atmos_check_settings.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_check_settings.py"
echo

# Create output directories
python $USHevs/global_det/global_det_atmos_create_output_dirs.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_create_output_dirs.py"
echo

# Link needed data files and set up model information
python $USHevs/global_det/global_det_atmos_get_data_files.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_get_data_files.py"
echo

# Send for missing files
if ls $DATA/grid2grid_stats/data/mail_* 1> /dev/null 2>&1; then
    for FILE in $DATA/grid2grid_stats/data/mail_*; do
        $FILE
    done
fi

# Check for restart files
if [ $evs_run_mode = production ]; then
    python ${USHevs}/global_det/global_det_atmos_production_restart.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Succesfully ran ${USHevs}/global_det/global_det_atmos_production_restart.py"
fi

# Create and run job scripts for reformat_data, assemble_data, generate_stats, and gather_stats
for group in reformat_data assemble_data generate_stats gather_stats; do
    export JOB_GROUP=$group
    echo "Creating and running jobs for grid-to-grid stats: ${JOB_GROUP}"
    python $USHevs/global_det/global_det_atmos_stats_grid2grid_create_job_scripts.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_stats_grid2grid_create_job_scripts.py"
    chmod u+x ${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/*
    group_ncount_job=$(ls -l  ${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/job* |wc -l)
    nc=1
    if [ $USE_CFP = YES ]; then
        group_ncount_poe=$(ls -l  ${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/poe* |wc -l)
        while [ $nc -le $group_ncount_poe ]; do
            poe_script=$DATA/${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/poe_jobs${nc}
            chmod 775 $poe_script
            export MP_PGMMODEL=mpmd
            export MP_CMDFILE=${poe_script}
            if [ $machine = WCOSS2 ]; then
                export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
                nselect=$(cat $PBS_NODEFILE | wc -l)
                nnp=$(($nselect * $nproc))
                launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,depth cfp"
            elif [ $machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
                export SLURM_KILL_BAD_EXIT=0
                launcher="srun --export=ALL --multi-prog"
            fi
            $launcher $MP_CMDFILE
            nc=$((nc+1))
        done
    else
        while [ $nc -le $group_ncount_job ]; do
            sh +x $DATA/${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/job${nc}
            nc=$((nc+1))
        done
    fi
    if [ $SENDCOM = YES ]; then
        # Copy atmos
        for RUN_DATE_PATH in $DATA/${VERIF_CASE}_${STEP}/METplus_output/$RUN.*; do
            RUN_DATE_DIR=$(echo ${RUN_DATE_PATH##*/})
            for RUN_DATE_SUBDIR_PATH in $DATA/${VERIF_CASE}_${STEP}/METplus_output/$RUN_DATE_DIR/*; do
                RUN_DATE_SUBDIR=$(echo ${RUN_DATE_SUBDIR_PATH##*/})
                if [ $(ls -A "$RUN_DATE_SUBDIR_PATH/$VERIF_CASE" | wc -l) -ne 0 ]; then
                    for FILE in $RUN_DATE_SUBDIR_PATH/$VERIF_CASE/*; do
                        if [ ! -f $COMOUT/$RUN_DATE_DIR/$RUN_DATE_SUBDIR/$VERIF_CASE/${FILE##*/} ]; then
                            cp -v $FILE $COMOUT/$RUN_DATE_DIR/$RUN_DATE_SUBDIR/$VERIF_CASE/${FILE##*/}
                        fi
                    done
                fi
            done
        done
    fi
done

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    # Copy model files
    for MODEL in $model_list; do
        for MODEL_DATE_PATH in $DATA/${VERIF_CASE}_${STEP}/METplus_output/$MODEL.*; do
            MODEL_DATE_SUBDIR=$(echo ${MODEL_DATE_PATH##*/})
            for FILE in $DATA/${VERIF_CASE}_${STEP}/METplus_output/$MODEL_DATE_SUBDIR/*; do
                cp -v $FILE $COMOUT/$MODEL_DATE_SUBDIR/.
            done
        done
    done
fi

# Non-production jobs
if [ $evs_run_mode != "production" ]; then
    # Send data to archive
    if [ $SENDARCH = YES ]; then
        python $USHevs/global_det/global_det_atmos_copy_to_archive.py
        status=$?
        [[ $status -ne 0 ]] && exit $status
        [[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_copy_to_archive.py"
        echo
    fi
    # Send data to METviewer AWS server
    if [ $SENDMETVIEWER = YES ]; then
        python $USHevs/global_det/global_det_atmos_load_to_METviewer_AWS.py
        status=$?
        [[ $status -ne 0 ]] && exit $status
        [[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_load_to_METviewer_AWS.py"
        echo
    else
        # Clean up
        if [ $KEEPDATA != "YES" ] ; then
            cd $DATAROOT
            rm -rf $DATA
        fi
    fi
fi

#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_atmos_grid2obs_stats.sh
# Developers: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det atmos stats step
#                    for the grid-to-obs verification. It uses METplus to
#                    generate the statistics.
###############################################################################

set -x

export VERIF_CASE_STEP_abbrev="g2os"

echo "RUN MODE:$evs_run_mode"

# Source config
source $config

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
if [ $SENDMAIL = YES ] ; then
    if ls $DATA/grid2obs_stats/data/mail_* 1> /dev/null 2>&1; then
        for FILE in $DATA/grid2obs_stats/data/mail_*; do
            $FILE
        done
    fi
fi

# Create and run job scripts for reformat_data, assemble_data, generate_stats, and gather_stats
for group in reformat_data assemble_data generate_stats gather_stats; do
    export JOB_GROUP=$group
    echo "Creating and running jobs for grid-to-obs stats: ${JOB_GROUP}"
    python $USHevs/global_det/global_det_atmos_stats_grid2obs_create_job_scripts.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_stats_grid2obs_create_job_scripts.py"
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

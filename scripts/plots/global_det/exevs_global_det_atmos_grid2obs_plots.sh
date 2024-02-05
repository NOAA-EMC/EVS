#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_atmos_grid2obs_plots.sh
# Developers: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det atmos plots step
#                    for the grid-to-obs verification. It uses EMC-developed
#                    python scripts to do the plotting.
###############################################################################

set -x

export VERIF_CASE_STEP_abbrev="g2op"
echo "RUN MODE:$evs_run_mode"

# Source config
source $config
export err=$?; err_chk

# Make directory
mkdir -p ${VERIF_CASE}_${STEP}

# Set number of days being plotted
start_date_seconds=$(date +%s -d ${start_date})
end_date_seconds=$(date +%s -d ${end_date})
diff_seconds=$(expr $end_date_seconds - $start_date_seconds)
diff_days=$(expr $diff_seconds \/ 86400)
total_days=$(expr $diff_days + 1)
NDAYS=${NDAYS:-$total_days}

# Check user's config settings
python $USHevs/global_det/global_det_atmos_check_settings.py
export err=$?; err_chk

# Create output directories
python $USHevs/global_det/global_det_atmos_create_output_dirs.py
export err=$?; err_chk

# Link needed data files and set up model information
python $USHevs/global_det/global_det_atmos_get_data_files.py
export err=$?; err_chk

# Create and run job scripts for condense_stats, filter_stats, make_plots, and tar_images
for group in condense_stats filter_stats make_plots tar_images; do
    export JOB_GROUP=$group
    echo "Creating and running jobs for grid-to-obs plots: ${JOB_GROUP}"
    python $USHevs/global_det/global_det_atmos_plots_grid2obs_create_job_scripts.py
    export err=$?; err_chk
    chmod u+x ${VERIF_CASE}_${STEP}/plot_job_scripts/$group/*
    nc=1
    if [ $USE_CFP = YES ]; then
        group_ncount_poe=$(ls -l  ${VERIF_CASE}_${STEP}/plot_job_scripts/$group/poe* |wc -l)
        while [ $nc -le $group_ncount_poe ]; do
            poe_script=$DATA/${VERIF_CASE}_${STEP}/plot_job_scripts/$group/poe_jobs${nc}
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
            export err=$?; err_chk
            nc=$((nc+1))
        done
    else
        group_ncount_job=$(ls -l  ${VERIF_CASE}_${STEP}/plot_job_scripts/$group/job* |wc -l)
        while [ $nc -le $group_ncount_job ]; do
            $DATA/${VERIF_CASE}_${STEP}/plot_job_scripts/$group/job${nc}
            export err=$?; err_chk
            nc=$((nc+1))
        done
    fi
done

# Cat the plotting log files
log_dir=$DATA/${VERIF_CASE}_${STEP}/plot_output/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
    for log_file in $log_dir/*; do
        echo "Start: $log_file"
        cat $log_file
        echo "End: $log_file"
    done
fi

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    # Make and copy tar file
    cd ${VERIF_CASE}_${STEP}/plot_output/tar_files
    for VERIF_TYPE in $g2op_type_list; do
        large_tar_file=${DATA}/${VERIF_CASE}_${STEP}/plot_output/${RUN}.${end_date}/evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}_${VERIF_TYPE}.last${NDAYS}days.v${end_date}.tar
        tar -cvf $large_tar_file ${VERIF_CASE}_${VERIF_TYPE}*.tar
        if [ -f $large_tar_file ]; then
           cp -v $large_tar_file $COMOUT/.
        fi
    done
    cd $DATA
fi

if [ $SENDDBN = YES ]; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}_${VERIF_TYPE}.last${NDAYS}days.v${end_date}.tar
fi

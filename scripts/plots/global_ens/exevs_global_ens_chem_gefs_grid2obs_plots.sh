#!/bin/bash
###############################################################################
# Name of Script: exevs_global_ens_chem_gefs_grid2obs_plots.sh
# Developers: Ho-Chun Huang / Ho-Chun.Huang@noaa.gov
#
# Original Name of Script: exevs_global_det_atmos_grid2obs_plots.sh
# Original Author: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_ens_chem_gefs plots step
#                    for the grid-to-obs verification. It uses EMC-developed
#                    python scripts to do the plotting.
###############################################################################

set -x

export VERIF_CASE_STEP_abbrev="g2op"
echo "RUN MODE:${evs_run_mode}"

# Source config
source ${config}
export err=$?; err_chk

# Make directory
mkdir -p ${VERIF_CASE}_${STEP}

# Set number of days being plotted
start_date_seconds=$(date +%s -d ${start_date})
end_date_seconds=$(date +%s -d ${end_date})
diff_seconds=$(expr ${end_date_seconds} - ${start_date_seconds})
diff_days=$(expr ${diff_seconds} \/ 86400)
total_days=$(expr ${diff_days} + 1)
NDAYS=${NDAYS:-${total_days}}

# Check user's config settings
python ${USHevs}/${COMPONENT}/${COMPONENT}_${RUN}_check_settings.py
export err=$?; err_chk

# Create output directories
python ${USHevs}/${COMPONENT}/${COMPONENT}_${RUN}_create_output_dirs.py
export err=$?; err_chk

# Link needed data files and set up model information
python ${USHevs}/${COMPONENT}/${COMPONENT}_${RUN}_get_data_files.py
export err=$?; err_chk

# Create and run job scripts for condense_stats, filter_stats, make_plots, and tar_images
## for group in condense_stats filter_stats make_plots tar_images; do
declare -a proc_list=( condense_stats filter_stats make_plots tar_images )
for group in "${proc_list[@]}"; do
    export JOB_GROUP=${group}
    echo "Creating and running jobs for grid-to-obs plots: ${JOB_GROUP}"
    python ${USHevs}/${COMPONENT}/${COMPONENT}_${RUN}_${STEP}_${VERIF_CASE}_create_job_scripts.py
    export err=$?; err_chk
    chmod u+x ${VERIF_CASE}_${STEP}/plot_job_scripts/${group}/*
    nc=1
    if [ $USE_CFP = YES ]; then
        group_ncount_poe=$(ls -l  ${VERIF_CASE}_${STEP}/plot_job_scripts/${group}/poe* 2>/dev/null | wc -l)
        while [ $nc -le ${group_ncount_poe} ]; do
            poe_script=${DATA}/${VERIF_CASE}_${STEP}/plot_job_scripts/${group}/poe_jobs${nc}
            chmod 775 ${poe_script}
            export MP_PGMMODEL=mpmd
            export MP_CMDFILE=${poe_script}
            if [ "${machine}" == "WCOSS2" ]; then
                nselect=$(cat ${PBS_NODEFILE} | wc -l)
                nnp=$((${nselect} * ${nproc}))
                launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,depth cfp"
            elif [ "${machine}" == "HERA" ] || [ "${machine}" = "ORION" ] || [ "${machine}" = "S4" ] || [ "${machine}" == "JET" ]; then
                export SLURM_KILL_BAD_EXIT=0
                launcher="srun --export=ALL --multi-prog"
            fi
            ${launcher} ${MP_CMDFILE}
            export err=$?; err_chk
            nc=$((nc+1))
        done
    else
        group_ncount_job=$(ls -l  ${VERIF_CASE}_${STEP}/plot_job_scripts/${group}/job* 2>/dev/null | wc -l)
        while [ ${nc} -le ${group_ncount_job} ]; do
            ${DATA}/${VERIF_CASE}_${STEP}/plot_job_scripts/${group}/job${nc}
            export err=$?; err_chk
            nc=$((nc+1))
        done
    fi
    python $USHevs/global_ens/global_ens_chem_copy_job_dir_output.py
    export err=$?; err_chk
    # Cat the plotting log files
    if [ $JOB_GROUP = make_plots ]; then
        log_dir=$DATA/${VERIF_CASE}_${STEP}/plot_output/job_work_dir/${JOB_GROUP}/job*/*/*/*/*/*/*/*/logs
    else
        log_dir=$DATA/${VERIF_CASE}_${STEP}/plot_output/job_work_dir/${JOB_GROUP}/job*/*/*/*/*/*/*/logs
    fi
    log_file_count=$(find $log_dir -type f 2>/dev/null |wc -l)
    if [[ $log_file_count -ne 0 ]]; then
        for log_file in $log_dir/*; do
            echo "Start: $log_file"
            cat $log_file
            echo "End: $log_file"
        done
    fi
done

# Copy files to desired location
if [ "${SENDCOM}" == "YES" ]; then
    # Make and copy tar file
    cd ${VERIF_CASE}_${STEP}/plot_output/tar_files
    for VERIF_TYPE in ${g2op_type_list}; do
        tar_file_combine=${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}_${VERIF_TYPE}.last${NDAYS}days.v${end_date}.tar
        large_tar_file=${DATA}/${VERIF_CASE}_${STEP}/plot_output/${tar_file_combine}
        tar_file_count=$(find ${DATA}/${VERIF_CASE}_${STEP}/plot_output/tar_files -type f 2>/dev/null |wc -l)
        if [[ $tar_file_count -ne 0 ]]; then
            tar -cvf $large_tar_file *.tar
        fi
        if [ -f ${large_tar_file} ]; then
           cp -v ${large_tar_file} ${COMOUT}/.
        fi
    done
    cd ${DATA}
fi

if [ "${SENDDBN}" == "YES" ]; then
    ${DBNROOT}/bin/dbn_alert MODEL EVS_RZDM ${job} ${COMOUT}/${tar_file_combine}
fi

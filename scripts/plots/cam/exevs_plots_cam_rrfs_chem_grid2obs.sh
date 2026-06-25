#!/bin/bash
###############################################################################
# Name of Script: exevs_plots_cam_rrfs_chem_grid2obs.sh
# Developers: Ho-Chun Huang / Ho-Chun.Huang@noaa.gov
#
# Purpose of Script: This script is run for the RRFS-Smoke and Dust plots step
#                    for the grid-to-obs verification. It uses EMC-developed
#                    python scripts to do the plotting.
#
#   Change Logs:
#   03/20/2026   Ho-Chun Huang  Revise code for RRFS-Chem from AQM plots code
###############################################################################

set -x

# set VERIF_CASE_STEP_abbrev prior to source ${config}
export VERIF_CASE_STEP_abbrev="g2op"
echo "RUN MODE:${evs_run_mode}"

## STATDIR is a temporary staging area for renaming
## and/or updating model name id in the stats files.
## STATDIR is used in the environemnt setting in ${config}. 
export STATDIR=${DATA}/stats_staging
mkdir -p ${STATDIR}

# Source config
source ${config}
export err=$?; err_chk

#
# Bring in all stats files, and change into display name
# for different models or types of solution defined in ${config}
#
IFS=' ' read -ra obstype_list <<< "${g2op_type_list}"
IFS=' ' read -ra obssrc_list <<< "${g2op_src_list}"
let num_obstype=${#obstype_list[@]}
let num_obssrc=${#obssrc_list[@]}
if [ ${num_obstype} -lt 1 ]; then
    echo "DEBUG: There is no obs variable to be plotted, ${MODELNAME} ${RUN} ${VERIF_CASE} ${STEP} step will be skipped"
    exit
fi
if [ ${num_obstype} -ne ${num_obssrc} ]; then
    echo "DEBUG: The number of obs variables to be plotted is different from obs sources, ${MODELNAME} ${RUN} ${VERIF_CASE} ${STEP} step will be skipped"
    exit
fi

IFS=' ' read -ra mdl_list <<< "${model_list}"
IFS=' ' read -ra mdl_idir_list <<< "${model_evs_stats_dir_list}"
let num_mdl=${#mdl_list[@]}
if [ ${num_mdl} -gt 10 ]; then
    echo "DEBUG: The number of models to be plotted exceeds the maximum (=10), ${MODELNAME} ${RUN} ${VERIF_CASE} ${STEP} step will be skipped"
    exit
fi
for imdl in "${!mdl_list[@]}"; do
    model_name=${mdl_list[${imdl}]}
    idir=${mdl_idir_list[${imdl}]}
    target_model="${model_name%v[0-9]*}"   ## model name separate by version number started with "v"
    upper_model="${target_model^^}"     ## Upper case model name as in the stats files
    for ivar in "${!obstype_list[@]}"; do
	obsvar=${obstype_list[${ivar}]}
	obssrc=${obssrc_list[${ivar}]}
        NOW=${VDATE_START}
        while [ ${NOW} -le ${VDATE_END} ]; do
            cpfile=evs.stats.${target_model}.${RUN}.${VERIF_CASE}_${obssrc}_${obsvar}.v${NOW}.stat
            sedfile=${model_name}_${obssrc}_${obsvar}.v${NOW}.stat
            if [ -s ${idir}/${target_model}.${NOW}/${cpfile} ]; then
                cp -v ${idir}/${target_model}.${NOW}/${cpfile} ${STATDIR}
                sed "s/${upper_model}/${model_name}/g" ${STATDIR}/${cpfile} > ${STATDIR}/${sedfile}
            else
                echo "DEBUG: There is a missing stats file ${idir}.${NOW}/${cpfile}, the missing file will be skipped"
            fi
            cdate=${NOW}"00"
            NOW=$( ${NDATE} +24 ${cdate} | cut -c1-8 )
        done
    done
done

# Make directory
mkdir -p ${VERIF_CASE}_${STEP}

# Set number of days being plotted
start_date_seconds=$(date +%s -d ${start_date})
end_date_seconds=$(date +%s -d ${end_date})
diff_seconds=$(expr ${end_date_seconds} - ${start_date_seconds})
diff_days=$(expr ${diff_seconds} \/ 86400)
total_days=$(expr ${diff_days} + 1)
if [ "${NDAYS}" != "${total_days}" ]; then
    echo "DEBUG: There is a difference between NDAYS ${NDAYS} and VDATE_END computation, ${MODELNAME} ${RUN} ${VERIF_CASE} ${STEP} step will be skipped"
    exit
fi

# Check user's config settings
python ${USHevs}/${COMPONENT}/${COMPONENT}_${MODELNAME}_${RUN}_check_settings.py
export err=$?; err_chk

# Create output directories
python ${USHevs}/${COMPONENT}/${COMPONENT}_${MODELNAME}_${RUN}_create_output_dirs.py
export err=$?; err_chk

# Link needed data files and set up model information
python ${USHevs}/${COMPONENT}/${COMPONENT}_${MODELNAME}_${RUN}_get_data_files.py
export err=$?; err_chk

# Create and run job scripts for condense_stats, filter_stats, make_plots, and tar_images
declare -a proc_list=( condense_stats filter_stats make_plots tar_images )
for group in "${proc_list[@]}"; do
    export JOB_GROUP=${group}
    echo "Creating and running jobs for grid-to-obs plots: ${JOB_GROUP}"
    python ${USHevs}/${COMPONENT}/${COMPONENT}_${MODELNAME}_${RUN}_${STEP}_${VERIF_CASE}_create_job_scripts.py
    export err=$?; err_chk
    chmod u+x ${VERIF_CASE}_${STEP}/plot_job_scripts/${group}/*
    nc=1
    if [ "${USE_CFP}" == "YES" ]; then
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
            elif [ "${machine}" == "URSA" ] || [ "${machine}" = "ORION" ] || [ "${machine}" = "S4" ] || [ "${machine}" == "JET" ]; then
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
    python ${USHevs}/${COMPONENT}/${COMPONENT}_${MODELNAME}_${RUN}_copy_job_dir_output.py
    export err=$?; err_chk
    # Cat the plotting log files
    if [ "${JOB_GROUP}" = "make_plots" ] || [ "${JOB_GROUP}" = "tar_images" ]; then
        log_dir=${DATA}/${VERIF_CASE}_${STEP}/plot_output/job_work_dir/${JOB_GROUP}/job*/*/*/*/*/*/*/*/logs
    else
        log_dir=${DATA}/${VERIF_CASE}_${STEP}/plot_output/job_work_dir/${JOB_GROUP}/job*/*/*/*/*/*/*/logs
    fi
    log_file_count=$(find ${log_dir} -type f 2>/dev/null |wc -l)
    if [[ ${log_file_count} -ne 0 ]]; then
        for log_file in ${log_dir}/*; do
            echo "Start: ${log_file}"
            cat ${log_file}
            echo "End: ${log_file}"
        done
    fi
done

# Copy files to desired location
if [ "${SENDCOM}" == "YES" ]; then
    # Make and copy tar file
    cd ${VERIF_CASE}_${STEP}/plot_output/tar_files
    for VERIF_TYPE in ${g2op_type_list}; do
        tar_file_combine=${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}_${VERIF_TYPE}.${fig_name_label}.v${end_date}.tar
        large_tar_file=${DATA}/${VERIF_CASE}_${STEP}/plot_output/${tar_file_combine}
        tar_file_count=$(find ${DATA}/${VERIF_CASE}_${STEP}/plot_output/tar_files ${VERIF_CASE}_${VERIF_TYPE}*.tar 2>/dev/null | wc -l)
        if [ ${tar_file_count} -ne 0 ]; then
            tar -cvf ${large_tar_file} ${VERIF_CASE}_${VERIF_TYPE}*.tar
        fi
        if [ -f ${large_tar_file} ]; then
            if [[ ${DATA_TYPE} == *"headline"* ]]; then
                OUTPUT_LOC=${COMOUTheadline}
            else
                OUTPUT_LOC=${COMOUT}
            fi
            cp -v ${large_tar_file} ${OUTPUT_LOC}/.

            if [ "${SENDDBN}" == "YES" ]; then
                ${DBNROOT}/bin/dbn_alert MODEL EVS_RZDM ${job} ${OUTPUT_LOC}/${tar_file_combine}
            fi
        fi
    done
    cd ${DATA}
fi
exit

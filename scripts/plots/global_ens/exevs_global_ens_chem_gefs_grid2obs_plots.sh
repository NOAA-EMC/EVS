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

export STATDIR=${DATA}/stats_staging
mkdir -p ${STATDIR}

# Source config
source ${config}
export err=$?; err_chk

model1=`echo ${MODELNAME} | tr a-z A-Z`
export model1

gefs_ver_id=$( echo ${gefs_ver} | awk -F"." '{print $1}' )
export modelid=${MODELNAME}${gefs_ver_id}

ObsType=`echo ${DATA_TYPE} | tr A-Z a-z`
export ObsType

IFS=' ' read -ra obstype_list <<< "${g2op_type_list}"
IFS=' ' read -ra obsvar_list <<< "${g2op_obsvar_list}"
let num_obstype=${#obstype_list[@]}
if [ ${num_obstype} -lt 1 ]; then
    echo "ERROR :: number of variable to be plotted is zero"
    exit
fi

varid="undefined"
let iobstype=0
while [ ${iobstype} -lt ${num_obstype} ]; do
    if [ "${ObsType}" == "${obstype_list[${iobstype}]}" ]; then
        export varid=${obsvar_list[${iobstype}]}
    fi
    ((iobstype++))
done

if [ "${varid}" == "undefined" ]; then
    echo "ERROR :: can not find observation index for variable ${ObsType}"
    exit
fi

# Bring in all stats files, and change into display name
# for different models or types of solution defined in ${config}

IFS=' ' read -ra mdl_list <<< "${model_list}"
IFS=' ' read -ra mdl_idir_list <<< "${model_evs_stats_dir_list}"
let num_mdl=${#mdl_list[@]}
if [ ${num_mdl} -gt 10 ]; then
    echo "number of model to be plotted can not exceed 10"
    exit
fi
let imdl=0
while [ ${imdl} -lt ${num_mdl} ]; do
    mdl=${mdl_list[${imdl}]}
    mdl_id=$( echo ${mdl_list[${imdl}]} | awk -F${MODELNAME} '{print $2}' )
    idir=${mdl_idir_list[${imdl}]}
    NOW=${VDATE_START}
    while [ ${NOW} -le ${VDATE_END} ]; do
        cpfile=evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}_${ObsType}_${varid}.v${NOW}.stat
        sedfile=${mdl}.${ObsType}${varid}.v${NOW}.stat
        if [ -s ${idir}/${MODELNAME}.${NOW}/${cpfile} ]; then
            cpreq ${idir}/${MODELNAME}.${NOW}/${cpfile} ${STATDIR}
            sed "s/${model1}/${mdl}/g" ${STATDIR}/${cpfile} > ${STATDIR}/${sedfile}
        else
            echo "DEBUG ${MODELNAME} ${STEP} :: Can not find ${idir}/${MODELNAME}.${NOW}/${cpfile}"
        fi
        cdate=${NOW}"00"
        NOW=$( ${NDATE} +24 ${cdate} | cut -c1-8 )
    done
    ((imdl++))
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
    echo "ERROR: input information inconsistent between NDAYS ${NDAYS} and VDATE_END computation"
    exit
fi

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
declare -a proc_list=( condense_stats filter_stats make_plots tar_images )
for group in "${proc_list[@]}"; do
    export JOB_GROUP=${group}
    echo "Creating and running jobs for grid-to-obs plots: ${JOB_GROUP}"
    python ${USHevs}/${COMPONENT}/${COMPONENT}_${RUN}_${STEP}_${VERIF_CASE}_create_job_scripts.py
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
    python ${USHevs}/global_ens/global_ens_chem_copy_job_dir_output.py
    export err=$?; err_chk
    # Cat the plotting log files
    if [ "${JOB_GROUP}" = "make_plots" ] || [ "${JOB_GROUP}" = "tar_images" ]; then
        log_dir=${DATA}/${VERIF_CASE}_${STEP}/plot_output/job_work_dir/${JOB_GROUP}/job*/*/*/*/*/*/*/*/logs
    else
        log_dir=${DATA}/${VERIF_CASE}_${STEP}/plot_output/job_work_dir/${JOB_GROUP}/job*/*/*/*/*/*/*/logs
    fi
    log_file_count=$(find ${log_dir} -type f 2>/dev/null | wc -l)
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
        tar_file_count=$(find ${DATA}/${VERIF_CASE}_${STEP}/plot_output/tar_files -type f 2>/dev/null | wc -l)
        if [ ${tar_file_count} -ne 0 ]; then
            tar -cvf ${large_tar_file} *.tar
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

#!/bin/bash
###############################################################################
# Name of Script: exevs_plots_global_chem_headline_grid2obs.sh
# Developers: Ho-Chun Huang / Ho-Chun.Huang@noaa.gov
#
# Purpose of Script: This script is run for the global_chem plots step for
#                    the headline verification. It uses EMC-developed
#                    python scripts to do the plotting.
#
#   Change Logs:
#    09/02/2025  Ho-Chun Huang    move cpreq to cp -v to comply with EE2
#    02/17/2026  Ho-Chun Huang    modified for GCAFSv1
###############################################################################

set -x

echo "RUN MODE:${evs_run_mode}"

## Provide temporary staging area for renaming and/or updating model
## name id in the stats files
export STATDIR=${DATA}/stats_staging

## Provide input stats location in ~/ush/global_chem/global_chem_plots_headline.py
export linked_stat_base_dir=${DATA}/data/headline

mkdir -p ${STATDIR} ${linked_stat_base_dir}

model1=`echo ${MODELNAME} | tr a-z A-Z`
export model1

gcafs_ver_id=$( echo ${gcafs_ver} | awk -F"." '{print $1}' )
export modelid=${MODELNAME}${gcafs_ver_id}
#
# Define the verification variables and observation sources
declare -a obstype_list=("airnow_pm25" "aeronet_aod")
declare -a obssrc_list=("airnow" "aeronet")

# Define the model names, plot names, and stats directory
declare -a mdl_list=("${modelid}")
declare -a plotname_list=("${gcafs_ver_id}")
declare -a mdl_idir_list=("${COMIN}/stats/${COMPONENT}")

# Define a constant for the maximum number of models
readonly MAX_MODELS=10

# Check if observation arrays have matching lengths
if (( ${#obstype_list[@]} != ${#obssrc_list[@]} )); then
    echo "DEBUG: The number of verification types does not match the number of observation sources."
    exit 1
fi

# Check if the number of models exceeds the maximum limit
if (( ${#mdl_list[@]} > MAX_MODELS )); then
    echo "DEBUG: Number of models to plot cannot exceed ${MAX_MODELS}."
    exit 1
fi

# Check if model and plot name arrays have matching lengths
if (( ${#mdl_list[@]} != ${#plotname_list[@]} )); then
    echo "DEBUG: The number of model IDs does not match the number of names to be plotted."
    exit 1
fi

# Export verification type info
export num_obs_type="${#obstype_list[@]}"
export plot_obstype_list=$(IFS=,; echo "${obstype_list[*]}")

# Export observation source info
export num_obs_src="${#obssrc_list[@]}"
export plot_obssrc_list=$(IFS=,; echo "${obssrc_list[*]}")

# Export model info
export num_plot_mdl="${#mdl_list[@]}"
export plot_model_list=$(IFS=,; echo "${mdl_list[*]}")

# Export plot name info
export num_plot_name="${#plotname_list[@]}"
export plot_plotname_list=$(IFS=,; echo "${plotname_list[*]}")

#
# Bringing in all statistics files and rearranging the filename and
# model ID according to the model name defined in `mdl_list`.
#
let imdl=0
while [ ${imdl} -lt ${#mdl_list[@]} ]; do
    biasc=$( echo ${mdl_list[${imdl}]} | awk -F"_" '{print $2}' )
    input_plots_model_name=${mdl_list[${imdl}]}
    idir=${mdl_idir_list[${imdl}]}
    linked_plot_stat_dir=${linked_stat_base_dir}/${input_plots_model_name}
    if [ ! -d ${linked_plot_stat_dir} ]; then mkdir -p ${linked_plot_stat_dir}; fi
    for ivar in "${obstype_list[@]}"; do
        ## get 2 additional day's stat for day 1 forecast
        cdate=${VDATE_START}"00"
        NOW=$( ${NDATE} -48 ${cdate} | cut -c1-8 )
        while [ ${NOW} -le ${VDATE_END} ]; do
            cpfile=evs.stats.${MODELNAME}.atmos.${VERIF_CASE}_${ivar}.v${NOW}.stat
            sedfile=${input_plots_model_name}_${ivar}.v${NOW}.stat
            if [ -s ${idir}/${MODELNAME}.${NOW}/${cpfile} ]; then
                cp -v ${idir}/${MODELNAME}.${NOW}/${cpfile} ${STATDIR}
                sed "s/${model1}/${input_plots_model_name}/g" ${STATDIR}/${cpfile} > ${STATDIR}/${sedfile}
                dest_model_date_stat_file=${linked_plot_stat_dir}/${input_plots_model_name}_${ivar}_v${NOW}.stat
                ln -s ${STATDIR}/${sedfile} ${dest_model_date_stat_file}
            else
                echo "DEBUG :: Input Stats ${idir}/${MODELNAME}.${NOW}/${cpfile} is missing and it will be skipped"
            fi
            cdate=${NOW}"00"
            NOW=$( ${NDATE} +24 ${cdate} | cut -c1-8 )
        done
    done
    ((imdl++))
done

# Create headline plots
python ${USHevs}/global_chem/global_chem_plots_headline.py
export err=$?; err_chk

# Copy files to desired location
if [ "${SENDCOM}" == "YES" ]; then
    # Make and copy tar file
    cd ${DATA}/images
    headline_tar_name=${DATA}/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar
    tar -cvf ${headline_tar_name} *.png
    if [ -f "${headline_tar_name}" ]; then
        cp -v ${headline_tar_name} ${COMOUT}/.
    fi
fi

# Cat the plotting log files
log_dir=${DATA}/logs
log_file_count=$(find ${log_dir} -type f |wc -l)
if [[ ${log_file_count} -ne 0 ]]; then
    for log_file in ${log_dir}/*; do
        echo "Start: ${log_file}"
        cat ${log_file}
        echo "End: ${log_file}"
    done
fi

if [ "${SENDDBN}" = "YES" ]; then
    headline_tar_name=${COMOUT}/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar
    if [ -f "${headline_tar_name}" ]; then
        ${DBNROOT}/bin/dbn_alert MODEL EVS_RZDM ${job} ${headline_tar_name}
    fi
fi

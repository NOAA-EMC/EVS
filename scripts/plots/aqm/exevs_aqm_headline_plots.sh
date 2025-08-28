#!/bin/bash
###############################################################################
# Name of Script: exevs_aqm_headline_plots.sh
# Developers: Ho-Chun Huang / Ho-Chun.Huang@noaa.gov
#
# Purpose of Script: This script is run for the aqm plots step for
#                    the headline verification. It uses EMC-developed
#                    python scripts to do the plotting.
#
#   Change Logs:
###############################################################################

set -x

echo "RUN MODE:${evs_run_mode}"

## Temporary staging area for renaming and/or updating model
## name id in the stats files
export STATDIR=${DATA}/stats_staging

## Provides data location in ~/ush/aqm/aqm_plots_headline.py
export linked_stat_base_dir=${DATA}/data/headline

mkdir -p ${STATDIR} ${linked_stat_base_dir}

model1=`echo ${MODELNAME} | tr a-z A-Z`
export model1

aqm_ver_id=$( echo ${aqm_ver} | awk -F"." '{print $1$2}' )
export modelid=${MODELNAME}${aqm_ver_id}
#
# Define plot type, model id, and input stats file locations.
#
declare -a obstype_list=(ozmax8 pmave)
declare -a mdl_list=(${modelid}_raw ${modelid}_bc)
declare -a plotname_list=(raw bc)
declare -a obssrc_list=(airnow airnow)

declare -a mdl_idir_list=(${COMIN}/stats/${COMPONENT} ${COMIN}/stats/${COMPONENT})

let num_mdl=${#mdl_list[@]}
if [ ${num_mdl} -gt 10 ]; then
    echo "number of model to be plotted can not exceed 10"
    exit
else
    export num_plot_mdl="${num_mdl}"
    IFS=","
    export plot_model_list="${mdl_list[*]}"
fi

let num_plotname=${#plotname_list[@]}
if [ ${num_plotname} -gt 10 ]; then
    echo "number of model to be plotted can not exceed 10"
    exit
else
    export num_plot_name="${num_plotname}"
    IFS=","
    export plot_plotname_list="${plotname_list[*]}"
fi

let num_obssrc=${#obssrc_list[@]}
if [ ${num_obssrc} -gt 10 ]; then
    echo "number of obs_src to be plotted can not exceed 10"
    exit
else
    export num_obs_src="${num_obssrc}"
    IFS=","
    export plot_obssrc_list="${obssrc_list[*]}"
fi
#
# Bringing in all statistics files and rearranging the filename and
# model ID according to the model name defined in `mdl_list`.
#
let imdl=0
while [ ${imdl} -lt ${num_mdl} ]; do
    biasc=$( echo ${mdl_list[${imdl}]} | awk -F"_" '{print $2}' )
    input_plots_model_name=${mdl_list[${imdl}]}
    idir=${mdl_idir_list[${imdl}]}
    linked_plot_stat_dir=${linked_stat_base_dir}/${input_plots_model_name}
    if [ ! -d ${linked_plot_stat_dir} ]; then mkdir -p ${linked_plot_stat_dir}; fi
    for ivar in "${obstype_list[@]}"; do
        #
        ## The `ozmax8` variable is validated at 11Z, and the `pamve`
        ## variable is validated at 04Z, both on the day following the
        ## initial start date.
        ## To obtain the valid-time data at 04Z and 11Z for `VDATE_START`
        ## for forecast days 1, 2, and 3, it is necessary to include
        ## statistics from previous days.
        #
        if [ "${ivar}" == "ozmax8" ]  || [ "${ivar}" == "pmave" ]; then  ## get 3 additional day's stat
            cdate=${VDATE_START}"00"
            NOW=$( ${NDATE} -72 ${cdate} | cut -c1-8 )
        else
            NOW=${VDATE_START}
	fi
        while [ ${NOW} -le ${VDATE_END} ]; do
            cpfile=evs.stats.${MODELNAME}_${biasc}.atmos.${VERIF_CASE}_${ivar}.v${NOW}.stat
            sedfile=${input_plots_model_name}_${ivar}.v${NOW}.stat
            if [ -s ${idir}/${MODELNAME}.${NOW}/${cpfile} ]; then
                cpreq ${idir}/${MODELNAME}.${NOW}/${cpfile} ${STATDIR}
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
python ${USHevs}/aqm/aqm_plots_headline.py
export err=$?; err_chk

# Copy files to desired location
if [ "${SENDCOM}" = "YES" ]; then
    # Make and copy tar file
    cd ${DATA}/images
    headline_tar_name=${DATA}/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar
    tar -cvf ${headline_tar_name} *.png
    if [[ -f "${headline_tar_name}" ]]; then
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
    if [[ -f "${headline_tar_name}" ]]; then
        ${DBNROOT}/bin/dbn_alert MODEL EVS_RZDM ${job} ${headline_tar_name}
    fi
fi

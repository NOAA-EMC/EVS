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

export obs_src_name=airnow

## Need temporary staging area for renaming and/or updating model
## name id in the stats files
## STATDIR is used in the environemnt setting in $USHevs/aqm/aqm_atmos_plots_headline.py
export STATDIR=${DATA}/stats_staging
## Linked stats dir 
export linked_stat_base_dir=${DATA}/data/headline
mkdir -p ${STATDIR} ${linked_stat_base_dir}

model1=`echo ${MODELNAME} | tr a-z A-Z`
export model1

aqm_ver_id=$( echo ${aqm_ver} | awk -F"." '{print $1$2}' )
export modelid=${MODELNAME}${aqm_ver_id}

#
# Bring in all stats files, and change into display name
# for different models or types of solution defined in ${config}
#
declare -a obstype_list=(ozmax8 pmave)
declare -a mdl_list=(${modelid}_raw ${modelid}_bc)
declare -a mdl_idir_list=(${COMIN}/stats/${COMPONENT} ${COMIN}/stats/${COMPONENT})

let num_mdl=${#mdl_list[@]}
if [ ${num_mdl} -gt 10 ]; then
    echo "number of model to be plotted can not exceed 10"
    exit
fi
let imdl=0
while [ ${imdl} -lt ${num_mdl} ]; do
    biasc=$( echo ${mdl_list[${imdl}]} | awk -F"_" '{print $2}' )
    idir=${mdl_idir_list[${imdl}]}
    for ivar in "${obstype_list[@]}"; do
        #
        ## the time stamp of aqm daily variable is valided at 11Z (ozmax8)
        ## and 04z (pamve) of next day from initial start date.  To get
	## the valid-time at 04Z and 11Z of date=VDATE_START for forecast
	## day1,day2, and day3, the stat of previous days also need
        ## to be copied
        #
        if [ "${ivar}" == "ozmax8" ]  || [ "${ivar}" == "pmave" ]; then  ## get 3 additional day's stat
            cdate=${VDATE_START}"00"
            NOW=$( ${NDATE} -72 ${cdate} | cut -c1-8 )
	    echo "variable = ${ivar} old_start_date = ${VDATE_START} new_start_date = ${NOW}"
        else
            NOW=${VDATE_START}
	fi
        while [ ${NOW} -le ${VDATE_END} ]; do
            cpfile=evs.stats.${MODELNAME}_${biasc}.${RUN}.${VERIF_CASE}_${ivar}.v${NOW}.stat
            sedfile=${modelid}_${biasc}_${ivar}.v${NOW}.stat
            if [ -s ${idir}/${MODELNAME}.${NOW}/${cpfile} ]; then
                cpreq ${idir}/${MODELNAME}.${NOW}/${cpfile} ${STATDIR}
                sed "s/${model1}/${modelid}_${biasc}/g" ${STATDIR}/${cpfile} > ${STATDIR}/${sedfile}
            else
                echo "DEBUG ${MODELNAME} ${STEP} :: Can not find ${idir}/${MODELNAME}.${NOW}/${cpfile}"
            fi
            dest_model_date_stat_file=${linked_stat_base_dir}/${modelid}_${biasc}/${modelid}_${biasc}_${ivar}_v${NOW}.stat
## check file size before linked
            ln -s ${STATDIR}/${sedfile} ${dest_model_date_stat_file}
            cdate=${NOW}"00"
            NOW=$( ${NDATE} +24 ${cdate} | cut -c1-8 )
        done
    done
    ((imdl++))
done

# Create headline plots
python $USHevs/aqm/aqm_atmos_plots_headline.py
export err=$?; err_chk

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    # Make and copy tar file
    cd $DATA/images
    tar -cvf $DATA/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar *.png
    if [ -f $DATA/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar ]; then
        cp -v $DATA/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar $COMOUT/.
    fi
fi

# Cat the plotting log files
log_dir=$DATA/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
    for log_file in $log_dir/*; do
        echo "Start: $log_file"
        cat $log_file
        echo "End: $log_file"
    done
fi

if [ $SENDDBN = YES ]; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.atmos.${RUN}.v${VDATE_END}.tar
fi

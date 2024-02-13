#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_wave_grid2obs_plots.sh
# Developers: Deanna Spindler / Deanna.Spindler@noaa.gov
#             Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det wave plots step
#                    for the grid-to-obs verification. It uses EMC-developed
#                    python scripts to do the plotting.
###############################################################################

set -x

#############################
## grid2obs wave model plots
#############################

cd $DATA
echo "in $0"
echo "Starting grid2obs_plots for ${RUN}"
echo "Starting at : `date`"

export model_list="gfs"
export modnam_list=$(echo $model_list | tr '[a-z]' '[A-Z]')

mkdir -p ${DATA}/stats
mkdir -p ${DATA}/jobs
mkdir -p ${DATA}/logs
mkdir -p ${DATA}/images

############################
# get the model .stat files
############################
echo ' '
echo 'Copying *.stat files :'

theDate=${VDATE_START}
while (( ${theDate} <= ${VDATE_END} )); do
    for MODEL in $model_list; do
        input_stats_file=${COMIN}/stats/${COMPONENT}/${MODEL}.${theDate}/evs.stats.${MODEL}.${RUN}.${VERIF_CASE}.v${theDate}.stat
        tmp_stats_file=${DATA}/stats/evs.stats.${MODEL}.${RUN}.${VERIF_CASE}.v${theDate}.stat
        if [[ -s $input_stats_file ]]; then
            cp -v $input_stats_file $tmp_stats_file
        else
            if [[ $input_stats_file == *"/com/"* ]] || [[ $input_stats_file == *"/dcom/"* ]]; then
                alert_word="WARNING"
            else
                alert_word="NOTE"
            fi
            echo "${alert_word}: $input_stats_file does not exist"
        fi
        theDate=$($NDATE +24 ${theDate}${vhr} | cut -c 1-8)
    done
done
####################
# quick error check
####################
for MODEL in $model_list; do
    nc=`ls ${DATA}/stats/evs.stats.${MODEL}.${RUN}.${VERIF_CASE}.v* | wc -l | awk '{print $1}'`
    echo " Found ${nc} ${DATA}/stats/${RUN}.${VERIF_CASE}.v* files"
    if [ "${nc}" != '0' ]; then
        echo "Successfully copied ${MODEL} *.stat files"
    else
        err_exit "${MODEL} *.stat files missing."
    fi
done

#################################
# Make the command files for cfp
#################################
## time_series
${USHevs}/${COMPONENT}/global_det_wave_plots_grid2obs_timeseries.sh
export err=$?; err_chk
## lead_averages
${USHevs}/${COMPONENT}/global_det_wave_plots_grid2obs_leadaverages.sh
export err=$?; err_chk

chmod 775 $DATA/jobs/run_all_${RUN}_g2o_plots_poe.sh

###########################################
# Run the command files
###########################################
plot_ncount_job=$(ls -l ${DATA}/jobs/plot*.sh |wc -l)
poe_script=${DATA}/jobs/run_all_${RUN}_g2o_plots_poe.sh
if [[ $plot_ncount_job -gt 0 ]]; then
    if [ $USE_CFP = YES ]; then
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        nselect=$(cat $PBS_NODEFILE | wc -l)
        nnp=$(($nselect * $nproc))
        launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,depth cfp"
        $launcher $MP_CMDFILE
        export err=$?; err_chk
    else
        ${poe_script}
        export err=$?; err_chk
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

#######################
# Gather all the files
#######################
# check to see if the plots are there
nc=$(ls ${DATA}/images/*.png | wc -l | awk '{print $1}')
echo " Found ${nc} ${DATA}/images/*.png "
if [ "${nc}" != '0' ]; then
    echo "Found ${nc} images"
    cd ${DATA}/images
    tar -cvf evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.last${NDAYS}days.v${VDATE_END}.tar *.png
    if [ $SENDCOM = YES ]; then
        if [ -f evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.last${NDAYS}days.v${VDATE_END}.tar ]; then
            cp -v evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.last${NDAYS}days.v${VDATE_END}.tar ${COMOUT}/.
        fi
    fi
    if [ $SENDDBN = YES ]; then
        $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.last${NDAYS}days.v${VDATE_END}.tar
    fi
    cd $DATA
else
    err_exit "PLOTS are missing"
fi

echo ' '
echo "Ending grid2obs_plots for ${RUN}"
echo "Ending at : `date`"
echo ' '

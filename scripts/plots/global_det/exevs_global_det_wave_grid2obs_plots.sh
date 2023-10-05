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
echo "in $0 JLOGFILE"
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
        COMINstatsfilename=${COMIN}/stats/${COMPONENT}/${MODEL}.${theDate}/evs.stats.${MODEL}.${RUN}.${VERIF_CASE}.v${theDate}.stat
        DATAstatsfilename=${DATA}/stats/evs.stats.${MODEL}.${RUN}.${VERIF_CASE}.v${theDate}.stat
        if [[ -s $COMINstatsfilename ]]; then
            cp -v $COMINstatsfilename $DATAstatsfilename
        else
            echo "DOES NOT EXIST $COMINstatsfilename"
        fi
        theDate=$(date --date="${theDate} + 1 day" '+%Y%m%d')
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
        echo ' '
        echo '**************************************** '
        echo "*** ERROR : NO ${MODEL} *.stat FILES *** "
        echo '**************************************** '
        echo ' '
        echo "${MODEL}_${RUN} : ${MODEL} *.stat files missing."
        ./postmsg "$jlogfile" "FATAL ERROR : NO ${MODEL} *.stat files"
        err_exit "FATAL ERROR: Did not copy the ${MODEL} *.stat files"
        exit
    fi
done

#################################
# Make the command files for cfp
#################################
## time_series
${USHevs}/${COMPONENT}/global_det_wave_plots_grid2obs_timeseries.sh
## lead_averages
${USHevs}/${COMPONENT}/global_det_wave_plots_grid2obs_leadaverages.sh

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
        export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
        nselect=$(cat $PBS_NODEFILE | wc -l)
        nnp=$(($nselect * $nproc))
        launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,depth cfp"
        $launcher $MP_CMDFILE
    else
        /bin/bash ${poe_script}
    fi
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
        cp -v evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.last${NDAYS}days.v${VDATE_END}.tar ${COMOUT}/.
    fi
    cd $DATA
else
    echo ' '
    echo '**************************************** '
    echo '*** ERROR : NO PLOTS found  *** '
    echo '**************************************** '
    echo ' '
    echo "${RUN} : PLOTS are missing."
    ./postmsg "$jlogfile" "FATAL ERROR : NO PLOTS"
    err_exit "FATAL ERROR: Did not find any plots"
fi

echo ' '
echo "Ending grid2obs_plots for ${RUN}"
echo "Ending at : `date`"
echo ' '

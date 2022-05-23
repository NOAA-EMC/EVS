#!/bin/sh
###############################################################################
# Name of Script: exevs_global_det_atmos_grid2grid_stats.sh 
# Purpose of Script: This script generates grid-to-grid
#                    verification statistics using METplus for the
#                    atmospheric component of global deterministic models
# Log history:
###############################################################################

set -x

export VERIF_CASE_STEP_abbrev="g2gs"

# Set run mode
if [ $RUN_ENVIR = nco ]; then
    export evs_run_mode="production"
else
    export evs_run_mode=$evs_run_mode
fi
echo "RUN MODE:$evs_run_mode"

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
[[ $status -eq 0 ]] && echo "Succesfully ran global_det_get_data_files.py"
echo

# Create job scripts data
python $USHevs/global_det/global_det_atmos_stats_grid2grid_create_job_scripts.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_create_stats_job_scripts.py"

# Run job scripts for reformat, make_met_data, and gather
#for group in reformat make_met_data gather; do
for group in reformat; do
    chmod u+x ${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/*
    group_ncount_poe=$(ls -l  ${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/poe* |wc -l)
    group_ncount_job=$(ls -l  ${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/job* |wc -l)
    if [ $USE_CFP = YES ]; then
        nc=0
        while [ $nc -lt $group_ncount_poe ]; do
            nc=$((nc+1))
            poe_script=$DATA/${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/poe_jobs${nc}
            chmod 775 $poe_script
            export MP_PGMMODEL=mpmd
            export MP_CMDFILE=${poe_script}
            if [ $machine = WCOSS2 ]; then
                export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
                launcher="mpiexec -np ${nproc} -ppn ${nproc} --cpu-bind verbose,depth cfp"
            elif [ $machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
                launcher="srun --export=ALL --multi-prog"
            fi
            $launcher $MP_CMDFILE
        done
    else
        nc=0
        while [ $nc -lt $group_ncount_job ]; do
            nc=$((nc+1))
            sh +x $DATA/${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/job${nc}
        done
    fi
done

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    DATE=${start_date}
    while [ $DATE -le ${end_date} ] ; do
        ls $DATA/${VERIF_CASE}_${STEP}/METplus_output/$RUN.$DATE
        for MODEL in $model_list; do
            ls $DATA/${VERIF_CASE}_${STEP}/METplus_output/$MODEL.$DATE
        done
        DATE=$(echo $($NDATE +24 ${DATE}00 ) |cut -c 1-8 )
    done
    #cp -r $DATA/${VERIF_CASE}_${STEP}/METplus_output/$RUN.* $COMROOT/$NET/$evs_ver/$STEP/$COMPONENT/.
    #for model in $model_list; do
    #    cp -r $DATA/${VERIF_CASE}_${STEP}/METplus_output/$model.* $COMROOT/$NET/$evs_ver/$STEP/$COMPONENT/.
    #done
fi

# Send data to METviewer AWS server

# Clean up
#if [ $RUN_ENVIR != nco ]; then
#fi

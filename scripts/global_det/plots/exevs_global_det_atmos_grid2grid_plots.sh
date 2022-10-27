#!/bin/sh
###############################################################################
# Name of Script: exevs_global_det_atmos_grid2grid_plots.sh
# Purpose of Script: This script generates grid-to-grid
#                    verification plots using python for the
#                    atmospheric component of global deterministic models
# Log history:
###############################################################################

set -x

export VERIF_CASE_STEP_abbrev="g2gp"

# Set run mode
if [ $RUN_ENVIR = nco ]; then
    export evs_run_mode="production"
    source $config
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
[[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_get_data_files.py"
echo

# Create job scripts data
python $USHevs/global_det/global_det_atmos_plots_grid2grid_create_job_scripts.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_plots_grid2grid_create_job_scripts.py"

# Run job scripts
chmod u+x ${VERIF_CASE}_${STEP}/plot_job_scripts/*
ncount_job=$(ls -l  ${VERIF_CASE}_${STEP}/plot_job_scripts/job* |wc -l)
nc=1
if [ $USE_CFP = YES ]; then
    ncount_poe=$(ls -l  ${VERIF_CASE}_${STEP}/plot_job_scripts/poe* |wc -l)
    while [ $nc -le $ncount_poe ]; do
        poe_script=$DATA/${VERIF_CASE}_${STEP}/plot_job_scripts/poe_jobs${nc}
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        if [ $machine = WCOSS2 ]; then
            export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
            launcher="mpiexec -np ${nproc} -ppn ${nproc} --cpu-bind verbose,depth cfp"
        elif [ $machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
            export SLURM_KILL_BAD_EXIT=0
            launcher="srun --export=ALL --multi-prog"
        fi
        $launcher $MP_CMDFILE
        nc=$((nc+1))
    done
else
    while [ $nc -le $ncount_job ]; do
        sh +x $DATA/${VERIF_CASE}_${STEP}/plot_job_scripts/job${nc}
        nc=$((nc+1))
    done
fi

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    # Make and copy tar file
    cd ${VERIF_CASE}_${STEP}/plot_output/${RUN}.${end_date}/images
    for VERIF_TYPE_SUBDIR_PATH in $DATA/${VERIF_CASE}_${STEP}/plot_output/$RUN.${end_date}/images/*; do
        VERIF_TYPE_SUBDIR=$(echo ${VERIF_TYPE_SUBDIR_PATH##*/})
        cd $VERIF_TYPE_SUBDIR
        tar -cvf ${DATA}/${VERIF_CASE}_${STEP}/plot_output/${RUN}.${end_date}/images/plots_${COMPONENT}_${RUN}_grid2grid_${VERIF_TYPE_SUBDIR}_v${start_date}to${end_date}.tar *
        cp -v ${DATA}/${VERIF_CASE}_${STEP}/plot_output/${RUN}.${end_date}/images/plots_${COMPONENT}_${RUN}_grid2grid_${VERIF_TYPE_SUBDIR}_v${start_date}to${end_date}.tar $COMOUT/.
    done
    cd $DATA
fi

# Non-production jobs
if [ $evs_run_mode != "production" ]; then
    # Clean up
    if [ $KEEPDATA != "YES" ] ; then
        cd $DATAROOT
        rm -rf $DATA
    fi
fi

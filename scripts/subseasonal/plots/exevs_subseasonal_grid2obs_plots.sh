#!/bin/bash
# Program Name: exevs_subseasonal_grid2obs_plots.sh
# Author(s)/Contact(s): Shannon Shields
# Abstract: This script generates grid-to-obs verification plots
#           using python for the subseasonal models
# History Log:

set -x

echo
echo "===== RUNNING GRID-TO-OBS PLOTS VERIFICATION  ====="
export STEP="plots"
export VERIF_CASE_STEP="grid2obs_plots"
export VERIF_CASE_STEP_abbrev="g2oplots"

# Set up directories
mkdir -p $VERIF_CASE_STEP
cd $VERIF_CASE_STEP

# Set number of days being plotted
start_date_seconds=$(date +%s -d ${start_date})
end_date_seconds=$(date +%s -d ${end_date})
diff_seconds=$(expr $end_date_seconds - $start_date_seconds)
diff_days=$(expr $diff_seconds \/ 86400)
total_days=$(expr $diff_days + 1)
NDAYS=${NDAYS:-total_days}

# Check user's configuration file
python $USHevs/subseasonal/check_subseasonal_config_plots.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran check_subseasonal_config_plots.py"
echo

# Create output directories
python $USHevs/subseasonal/create_METplus_subseasonal_output_dirs.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran create_METplus_subseasonal_output_dirs.py"
echo

# Link needed data files and set up model information
python $USHevs/subseasonal/get_subseasonal_stat_files.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran get_subseasonal_stat_files.py"
echo

# Create job scripts
for group in condense_stats filter_stats make_plots tar_images; do
    export JOB_GROUP=$group
    echo "Creating and running jobs for grid-to-obs plots: ${JOB_GROUP}"
    python $USHevs/subseasonal/subseasonal_plots_grid2obs_create_job_scripts.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran subseasonal_plots_grid2obs_create_job_scripts.py"
    # Run job scripts
    chmod u+x $DATA/$VERIF_CASE_STEP/plot_job_scripts/$group/*
    group_ncount_job=$(ls -l  $DATA/$VERIF_CASE_STEP/plot_job_scripts/$group/job* |wc -l)
    nc=1
    if [ $USE_CFP = YES ]; then
        group_ncount_poe=$(ls -l  $DATA/$VERIF_CASE_STEP/plot_job_scripts/$group/poe* |wc -l)
        while [ $nc -le $group_ncount_poe ]; do
	    poe_script=$DATA/$VERIF_CASE_STEP/plot_job_scripts/$group/poe_jobs${nc}
	    chmod 775 $poe_script
	    export MP_PGMMODEL=mpmd
	    export MP_CMDFILE=${poe_script}
	    if [ $machine = WCOSS2 ]; then
	        export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
	        nselect=$(cat $PBS_NODEFILE | wc -l)
	        nnp=$(($nselect * $nproc))
	        launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,depth cfp"
	    elif [ $machine = HERA -o $machine = ORION ]; then
	        export SLURM_KILL_BAD_EXIT=0
	        launcher="srun --export=ALL --multi-prog"
	    fi
	    $launcher $MP_CMDFILE
	    nc=$((nc+1))
        done
    else
        while [ $nc -le $group_ncount_job ]; do
	    sh +x $DATA/$VERIF_CASE_STEP/plot_job_scripts/$group/job${nc}
	    nc=$((nc+1))
        done
    fi
done

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    # Make and copy tar file
    cd $DATA/$VERIF_CASE_STEP/plot_output/${RUN}.${end_date}/images
    for VERIF_TYPE_SUBDIR_PATH in $DATA/$VERIF_CASE_STEP/plot_output/$RUN.${end_date}/images/*; do
	VERIF_TYPE_SUBDIR=$(echo ${VERIF_TYPE_SUBDIR_PATH##*/})
	cd $VERIF_TYPE_SUBDIR
	large_tar_file=${DATA}/${VERIF_CASE_STEP}/plot_output/${RUN}.${end_date}/images/evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}_prepbufr.last${NDAYS}days.v${PDYm2}.tar
        tar -cvf $large_tar_file *.tar
	cp -v $large_tar_file $COMOUT/.
    done
    cd $DATA
fi

# SENDDBN alert
if [ $SENDDBN = YES ] ; then
    tarname=evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}_prepbufr.last${NDAYS}days.v${PDYm2}.tar
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/$tarname
fi

#!/bin/bash
# Program Name: exevs_subseasonal_grid2grid_plots.sh
# Author(s)/Contact(s): Shannon Shields
# Abstract: This script is run by JEVS_SUBSEASONAL_PLOTS in jobs/.
#           This script generates grid-to-grid verification plots
#           using python for the subseasonal models.

set -x

echo
echo "===== RUNNING GRID-TO-GRID PLOTS VERIFICATION  ====="
export STEP="plots"
export VERIF_CASE_STEP="grid2grid_plots"
export VERIF_CASE_STEP_abbrev="g2gplots"

# Source config
source $config
export err=$?; err_chk

# Set up directories
mkdir -p $VERIF_CASE_STEP
cd $VERIF_CASE_STEP

# Set number of days being plotted
diff_hours=$($NHOUR  ${end_date}00 ${start_date}00)
diff_days=$(expr $diff_hours \/ 24)
total_days=$(expr $diff_days + 1)
NDAYS=${NDAYS:-total_days}

# Check user's configuration file
python $USHevs/subseasonal/check_subseasonal_config_plots.py
export err=$?; err_chk

# Create output directories
python $USHevs/subseasonal/create_METplus_subseasonal_output_dirs.py
export err=$?; err_chk

# Link needed data files and set up model information
python $USHevs/subseasonal/get_subseasonal_stat_files.py
export err=$?; err_chk

# Create job scripts
for group in condense_stats filter_stats make_plots tar_images; do
    export JOB_GROUP=$group
    echo "Creating and running jobs for grid-to-grid plots: ${JOB_GROUP}"
    python $USHevs/subseasonal/subseasonal_plots_grid2grid_create_job_scripts.py
    export err=$?; err_chk
    # Run job scripts
    chmod u+x $DATA/$VERIF_CASE_STEP/plot_job_scripts/$group/*
    nc=1
    if [ $USE_CFP = YES ]; then
        group_ncount_poe=$(ls -l  $DATA/$VERIF_CASE_STEP/plot_job_scripts/$group/poe* |wc -l)
        while [ $nc -le $group_ncount_poe ]; do
	    poe_script=$DATA/$VERIF_CASE_STEP/plot_job_scripts/$group/poe_jobs${nc}
	    chmod 775 $poe_script
	    export MP_PGMMODEL=mpmd
	    export MP_CMDFILE=${poe_script}
	    if [ $machine = WCOSS2 ]; then
	        nselect=$(cat $PBS_NODEFILE | wc -l)
	        nnp=$(($nselect * $nproc))
	        launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,depth cfp"
	    elif [ $machine = HERA -o $machine = ORION ]; then
	        export SLURM_KILL_BAD_EXIT=0
	        launcher="srun --export=ALL --multi-prog"
	    fi
	    $launcher $MP_CMDFILE
	    export err=$?; err_chk
	    nc=$((nc+1))
        done
    else
	group_ncount_job=$(ls -l  $DATA/$VERIF_CASE_STEP/plot_job_scripts/$group/job* |wc -l)
        while [ $nc -le $group_ncount_job ]; do
	    $DATA/$VERIF_CASE_STEP/plot_job_scripts/$group/job${nc}
	    export err=$?; err_chk
	    nc=$((nc+1))
        done
    fi
done

# Cat the plotting log files
log_dir=$DATA/${VERIF_CASE}_${STEP}/plot_output/${RUN}.${end_date}/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
    for log_file in $log_dir/*; do
	echo "Start: $log_file"
	cat $log_file
	echo "End: $log_file"
    done
fi

# Copy files to desired location
if [ $SENDCOM = YES ]; then
    # Make and copy tar file
    cd $DATA/$VERIF_CASE_STEP/plot_output/${RUN}.${end_date}/images
    for VERIF_TYPE_SUBDIR_PATH in $DATA/$VERIF_CASE_STEP/plot_output/$RUN.${end_date}/images/*; do
	VERIF_TYPE_SUBDIR=$(echo ${VERIF_TYPE_SUBDIR_PATH##*/})
	cd $VERIF_TYPE_SUBDIR
	large_tar_file=${DATA}/${VERIF_CASE_STEP}/plot_output/${RUN}.${end_date}/images/evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}_${VERIF_TYPE_SUBDIR}.last${NDAYS}days.v${end_date}.tar
        tar -cvf $large_tar_file *.tar
	if [ -s $large_tar_file ]; then
	    cp -v $large_tar_file $COMOUT/.
	fi
    done
    cd $DATA
fi

# SENDDBN alert
if [ $SENDDBN = YES ] ; then
    tarname=evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}_${VERIF_TYPE}.last${NDAYS}days.v${end_date}.tar
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/$tarname
fi

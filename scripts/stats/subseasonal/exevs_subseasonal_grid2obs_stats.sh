#!/bin/bash
# Program Name: exevs_subseasonal_grid2obs_stats.sh
# Author(s)/Contact(s): Shannon Shields
# Abstract: This script is run by JEVS_SUBSEASONAL_STATS in jobs/.
#           This script runs METplus for subseasonal grid-to-obs verification             to produce stats.

set -x

echo
echo "===== RUNNING GRID-TO-OBS STATS VERIFICATION  ====="
export STEP="stats"
export VERIF_CASE_STEP="grid2obs_stats"
export VERIF_CASE_STEP_abbrev="g2ostats"

# Source config
source $config
export err=$?; err_chk

# Set up directories
mkdir -p $VERIF_CASE_STEP
cd $VERIF_CASE_STEP


# Check user's configuration file
python $USHevs/subseasonal/check_subseasonal_config_stats.py
export err=$?; err_chk

# Set up environment variables for initialization, valid, and forecast hours and source them
python $USHevs/subseasonal/set_init_valid_fhr_subseasonal_stats_info.py
export err=$?; err_chk
. $DATA/$VERIF_CASE_STEP/python_gen_env_vars.sh
export err=$?; err_chk

# Create output directories for METplus
python $USHevs/subseasonal/create_METplus_subseasonal_output_dirs.py
export err=$?; err_chk

# Link needed data files and set up model information
python $USHevs/subseasonal/subseasonal_get_data_files.py
export err=$?; err_chk

# Create job scripts to run METplus for reformat_data, assemble_data, generate_stats, and gather_stats
for group in reformat_data assemble_data generate_stats gather_stats; do
    export JOB_GROUP=$group
    if [ "${JOB_GROUP}" = "reformat_data" ]; then
	echo "Creating and running jobs for grid-to-obs stats: ${JOB_GROUP}"
	export njobs=0
	WEEKLY_LIST="Week1 Week2 Week3 Week4 Week5"
	for WEEK in $WEEKLY_LIST; do
	    export WEEK=$WEEK
	    if [ "${WEEK}" = "Week1" ]; then
		export CORRECT_INIT_DATE=$PDYm9
		export CORRECT_LEAD_SEQ=0,12,24,36,48,60,72,84,96,108,120,132,144,156,168
	    elif [ "${WEEK}" = "Week2" ]; then
		export CORRECT_INIT_DATE=$PDYm16
		export CORRECT_LEAD_SEQ=168,180,192,204,216,228,240,252,264,276,288,300,312,324,336
	    elif [ "${WEEK}" = "Week3" ]; then
		export CORRECT_INIT_DATE=$PDYm23
		export CORRECT_LEAD_SEQ=336,348,360,372,384,396,408,420,432,444,456,468,480,492,504
	    elif [ "${WEEK}" = "Week4" ]; then
		export CORRECT_INIT_DATE=$PDYm30
		export CORRECT_LEAD_SEQ=504,516,528,540,552,564,576,588,600,612,624,636,648,660,672
	    elif [ "${WEEK}" = "Week5" ]; then
		export CORRECT_INIT_DATE=$PDYm37
		export CORRECT_LEAD_SEQ=672,684,696,708,720,732,744,756,768,780,792,804,816,828,840
	    fi
	    python $USHevs/subseasonal/subseasonal_stats_grid2obs_create_weekly_reformat_job_scripts.py
	    export err=$?; err_chk
	    export njobs=$((njobs+1))
	done
	DAYS6_10_LIST="Days6_10"
	for DAYS in $DAYS6_10_LIST; do
	    export njobs=5
	    export DAYS=$DAYS
	    if [ "${DAYS}" = "Days6_10" ]; then
		export CORRECT_INIT_DATE=$PDYm12
		export CORRECT_LEAD_SEQ=120,132,144,156,168,180,192,204,216,228,240
	    fi
	    python $USHevs/subseasonal/subseasonal_stats_grid2obs_create_days6_10_reformat_job_scripts.py
	    export err=$?; err_chk
	done
	WEEKS3_4_LIST="Weeks3_4"
	for WEEKS in $WEEKS3_4_LIST; do
	    export njobs=6
	    export WEEKS=$WEEKS
	    if [ "${WEEKS}" = "Weeks3_4" ]; then
		export CORRECT_INIT_DATE=$PDYm30
		export CORRECT_LEAD_SEQ=336,348,360,372,384,396,408,420,432,444,456,468,480,492,504,516,528,540,552,564,576,588,600,612,624,636,648,660,672
	    fi
	    python $USHevs/subseasonal/subseasonal_stats_grid2obs_create_weeks3_4_reformat_job_scripts.py
	    export err=$?; err_chk
	done
	# Create reformat_data POE job scripts
	if [ $USE_CFP = YES ]; then
	    python $USHevs/subseasonal/subseasonal_stats_grid2obs_create_poe_job_scripts.py
	    export err=$?; err_chk
	fi
    elif [ "${JOB_GROUP}" = "assemble_data" ]; then
	echo "Creating and running jobs for grid-to-obs stats: ${JOB_GROUP}"
	export njobs=0
	WEEKLY_LIST="Week1 Week2 Week3 Week5"
	for WEEK in $WEEKLY_LIST; do
	    export WEEK=$WEEK
	    if [ "${WEEK}" = "Week1" ]; then
		export CORRECT_INIT_DATE=$PDYm9
		export CORRECT_LEAD_SEQ=0,12,24,36,48,60,72,84,96,108,120,132,144,156,168
	    elif [ "${WEEK}" = "Week2" ]; then
		export CORRECT_INIT_DATE=$PDYm16
		export CORRECT_LEAD_SEQ=168,180,192,204,216,228,240,252,264,276,288,300,312,324,336
	    elif [ "${WEEK}" = "Week3" ]; then
		export CORRECT_INIT_DATE=$PDYm23
		export CORRECT_LEAD_SEQ=336,348,360,372,384,396,408,420,432,444,456,468,480,492,504
	    elif [ "${WEEK}" = "Week5" ]; then
		export CORRECT_INIT_DATE=$PDYm37
		export CORRECT_LEAD_SEQ=672,684,696,708,720,732,744,756,768,780,792,804,816,828,840
	    fi
	    python $USHevs/subseasonal/subseasonal_stats_grid2obs_create_weekly_assemble_job_scripts.py
	    export err=$?; err_chk
	    export njobs=$((njobs+1))
	done
	DAYS6_10_LIST="Days6_10"
	for DAYS in $DAYS6_10_LIST; do
	    export njobs=4
	    export DAYS=$DAYS
	    if [ "${DAYS}" = "Days6_10" ]; then
		export CORRECT_INIT_DATE=$PDYm12
		export CORRECT_LEAD_SEQ=120,132,144,156,168,180,192,204,216,228,240
	    fi
	    python $USHevs/subseasonal/subseasonal_stats_grid2obs_create_days6_10_assemble_job_scripts.py
	    export err=$?; err_chk
	done
	WEEKS3_4_LIST="Weeks3_4"
	for WEEKS in $WEEKS3_4_LIST; do
	    export njobs=5
	    export WEEKS=$WEEKS
	    if [ "${WEEKS}" = "Weeks3_4" ]; then
		export CORRECT_INIT_DATE=$PDYm30
		export CORRECT_LEAD_SEQ=336,348,360,372,384,396,408,420,432,444,456,468,480,492,504,516,528,540,552,564,576,588,600,612,624,636,648,660,672
	    fi
	    python $USHevs/subseasonal/subseasonal_stats_grid2obs_create_weeks3_4_assemble_job_scripts.py
	    export err=$?; err_chk
	done
	# Create assemble_data POE job scripts
	if [ $USE_CFP = YES ]; then
            python $USHevs/subseasonal/subseasonal_stats_grid2obs_create_poe_job_scripts.py
	    export err=$?; err_chk
	fi
    else
        echo "Creating and running jobs for grid-to-obs stats: ${JOB_GROUP}"
        python $USHevs/subseasonal/subseasonal_stats_grid2obs_create_job_scripts.py
        export err=$?; err_chk
    fi
    chmod u+x $DATA/$VERIF_CASE_STEP/METplus_job_scripts/$group/*
    nc=1
    if [ $USE_CFP = YES ]; then
        group_ncount_poe=$(ls -l  $DATA/$VERIF_CASE_STEP/METplus_job_scripts/$group/poe* |wc -l)
        while [ $nc -le $group_ncount_poe ]; do
	    poe_script=$DATA/$VERIF_CASE_STEP/METplus_job_scripts/$group/poe_jobs${nc}
	    chmod 775 $poe_script
	    export MP_PGMMODEL=mpmd
	    export MP_CMDFILE=${poe_script}
	    if [ $machine = WCOSS2 ]; then
	        launcher="mpiexec -np ${nproc} -ppn ${nproc} --cpu-bind verbose,core cfp"
	    elif [ $machine = HERA -o $machine = ORION ]; then
		export SLURM_KILL_BAD_EXIT=0
	        launcher="srun --export=ALL --multi-prog"
	    fi
	    $launcher $MP_CMDFILE
	    export err=$?; err_chk
	    nc=$((nc+1))
        done
    else
	group_ncount_job=$(ls -l  $DATA/$VERIF_CASE_STEP/METplus_job_scripts/$group/job* |wc -l)
        while [ $nc -le $group_ncount_job ]; do
	    $DATA/$VERIF_CASE_STEP/METplus_job_scripts/$group/job${nc}
	    export err=$?; err_chk
	    nc=$((nc+1))
        done
    fi
done


# Copy stat files to desired location
if [ $SENDCOM = YES ]; then
    for MODEL in $model_list; do
	for MODEL_DATE_PATH in $DATA/$VERIF_CASE_STEP/METplus_output/$MODEL.*; do
	    MODEL_DATE_SUBDIR=$(echo ${MODEL_DATE_PATH##*/})
	    for FILE in $DATA/$VERIF_CASE_STEP/METplus_output/$MODEL_DATE_SUBDIR/*; do
		if [ -s $FILE ]; then
		    cp -v $FILE $COMOUT/$MODEL_DATE_SUBDIR/.
		fi
	    done
        done
    done
fi

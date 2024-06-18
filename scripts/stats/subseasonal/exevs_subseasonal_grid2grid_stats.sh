#!/bin/bash
# Program Name: exevs_subseasonal_grid2grid_stats.sh
# Author(s)/Contact(s): Shannon Shields
# Abstract: This script is run by JEVS_SUBSEASONAL_STATS in jobs/.
#           This script runs METplus for subseasonal grid-to-grid verification            to produce stats.

set -x

echo
echo "===== RUNNING GRID-TO-GRID STATS VERIFICATION  ====="
export STEP="stats"
export VERIF_CASE_STEP="grid2grid_stats"
export VERIF_CASE_STEP_abbrev="g2gstats"

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
	echo "Creating and running jobs for grid-to-grid stats: ${JOB_GROUP}"
	export njobs=0
	DAILY_LIST="Day1 Day2 Day3 Day4 Day5 Day6 Day7 Day8 Day9 Day10 Day11 Day12 Day13 Day14 Day15 Day16 Day17 Day18 Day19 Day20 Day21 Day22 Day23 Day24 Day25 Day26 Day27 Day28 Day29 Day30 Day31 Day32 Day33 Day34 Day35"
	for DAY in $DAILY_LIST; do
	    export DAY=$DAY
	    if [ "${DAY}" = "Day1" ]; then
		export CORRECT_INIT_DATE=$PDYm3
		export CORRECT_LEAD_SEQ=0,12,24
	    elif [ "${DAY}" = "Day2" ]; then
		export CORRECT_INIT_DATE=$PDYm4
		export CORRECT_LEAD_SEQ=24,36,48
	    elif [ "${DAY}" = "Day3" ]; then
		export CORRECT_INIT_DATE=$PDYm5
		export CORRECT_LEAD_SEQ=48,60,72
	    elif [ "${DAY}" = "Day4" ]; then
		export CORRECT_INIT_DATE=$PDYm6
	        export CORRECT_LEAD_SEQ=72,84,96
	    elif [ "${DAY}" = "Day5" ]; then
		export CORRECT_INIT_DATE=$PDYm7
	        export CORRECT_LEAD_SEQ=96,108,120
	    elif [ "${DAY}" = "Day6" ]; then
		export CORRECT_INIT_DATE=$PDYm8
		export CORRECT_LEAD_SEQ=120,132,144
	    elif [ "${DAY}" = "Day7" ]; then
		export CORRECT_INIT_DATE=$PDYm9
		export CORRECT_LEAD_SEQ=144,156,168
	    elif [ "${DAY}" = "Day8" ]; then
		export CORRECT_INIT_DATE=$PDYm10
		export CORRECT_LEAD_SEQ=168,180,192
	    elif [ "${DAY}" = "Day9" ]; then
		export CORRECT_INIT_DATE=$PDYm11
		export CORRECT_LEAD_SEQ=192,204,216
	    elif [ "${DAY}" = "Day10" ]; then
		export CORRECT_INIT_DATE=$PDYm12
	        export CORRECT_LEAD_SEQ=216,228,240
	    elif [ "${DAY}" = "Day11" ]; then
		export CORRECT_INIT_DATE=$PDYm13
	        export CORRECT_LEAD_SEQ=240,252,264
	    elif [ "${DAY}" = "Day12" ]; then
		export CORRECT_INIT_DATE=$PDYm14
	        export CORRECT_LEAD_SEQ=264,276,288
	    elif [ "${DAY}" = "Day13" ]; then
		export CORRECT_INIT_DATE=$PDYm15
		export CORRECT_LEAD_SEQ=288,300,312
	    elif [ "${DAY}" = "Day14" ]; then
		export CORRECT_INIT_DATE=$PDYm16
		export CORRECT_LEAD_SEQ=312,324,336
	    elif [ "${DAY}" = "Day15" ]; then
		export CORRECT_INIT_DATE=$PDYm17
		export CORRECT_LEAD_SEQ=336,348,360
	    elif [ "${DAY}" = "Day16" ]; then
		export CORRECT_INIT_DATE=$PDYm18
		export CORRECT_LEAD_SEQ=360,372,384
	    elif [ "${DAY}" = "Day17" ]; then
		export CORRECT_INIT_DATE=$PDYm19
	        export CORRECT_LEAD_SEQ=384,396,408
	    elif [ "${DAY}" = "Day18" ]; then
		export CORRECT_INIT_DATE=$PDYm20
		export CORRECT_LEAD_SEQ=408,420,432
	    elif [ "${DAY}" = "Day19" ]; then
		export CORRECT_INIT_DATE=$PDYm21
		export CORRECT_LEAD_SEQ=432,444,456
	    elif [ "${DAY}" = "Day20" ]; then
		export CORRECT_INIT_DATE=$PDYm22
		export CORRECT_LEAD_SEQ=456,468,480
	    elif [ "${DAY}" = "Day21" ]; then
		export CORRECT_INIT_DATE=$PDYm23
		export CORRECT_LEAD_SEQ=480,492,504
	    elif [ "${DAY}" = "Day22" ]; then
		export CORRECT_INIT_DATE=$PDYm24
		export CORRECT_LEAD_SEQ=504,516,528
	    elif [ "${DAY}" = "Day23" ]; then
		export CORRECT_INIT_DATE=$PDYm25
		export CORRECT_LEAD_SEQ=528,540,552
	    elif [ "${DAY}" = "Day24" ]; then
		export CORRECT_INIT_DATE=$PDYm26
		export CORRECT_LEAD_SEQ=552,564,576
	    elif [ "${DAY}" = "Day25" ]; then
		export CORRECT_INIT_DATE=$PDYm27
		export CORRECT_LEAD_SEQ=576,588,600
	    elif [ "${DAY}" = "Day26" ]; then
		export CORRECT_INIT_DATE=$PDYm28
	        export CORRECT_LEAD_SEQ=600,612,624
	    elif [ "${DAY}" = "Day27" ]; then
		export CORRECT_INIT_DATE=$PDYm29
		export CORRECT_LEAD_SEQ=624,636,648
	    elif [ "${DAY}" = "Day28" ]; then
		export CORRECT_INIT_DATE=$PDYm30
		export CORRECT_LEAD_SEQ=648,660,672
	    elif [ "${DAY}" = "Day29" ]; then
		export CORRECT_INIT_DATE=$PDYm31
	        export CORRECT_LEAD_SEQ=672,684,696
	    elif [ "${DAY}" = "Day30" ]; then
		export CORRECT_INIT_DATE=$PDYm32
		export CORRECT_LEAD_SEQ=696,708,720
	    elif [ "${DAY}" = "Day31" ]; then
		export CORRECT_INIT_DATE=$PDYm33
		export CORRECT_LEAD_SEQ=720,732,744
	    elif [ "${DAY}" = "Day32" ]; then
		export CORRECT_INIT_DATE=$PDYm34
		export CORRECT_LEAD_SEQ=744,756,768
	    elif [ "${DAY}" = "Day33" ]; then
		export CORRECT_INIT_DATE=$PDYm35
		export CORRECT_LEAD_SEQ=768,780,792
	    elif [ "${DAY}" = "Day34" ]; then
		export CORRECT_INIT_DATE=$PDYm36
		export CORRECT_LEAD_SEQ=792,804,816
	    elif [ "${DAY}" = "Day35" ]; then
		export CORRECT_INIT_DATE=$PDYm37
		export CORRECT_LEAD_SEQ=816,828,840
	    fi
	    python $USHevs/subseasonal/subseasonal_stats_grid2grid_create_daily_reformat_job_scripts.py
	    export err=$?; err_chk
	    export njobs=$((njobs+1))
        done
	WEEKLY_LIST="Week1 Week2 Week3 Week5"
	export njobs=35 
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
	    python $USHevs/subseasonal/subseasonal_stats_grid2grid_create_weekly_reformat_job_scripts.py
	    export err=$?; err_chk
	    export njobs=$((njobs+4)) 
        done
	WEEK4_LIST="Week4"
	for WEEK in $WEEK4_LIST; do
	    export njobs=51
	    export WEEK=$WEEK
	    if [ "${WEEK}" = "Week4" ]; then
		export CORRECT_INIT_DATE=$PDYm30
		export CORRECT_LEAD_SEQ=504,516,528,540,552,564,576,588,600,612,624,636,648,660,672
	    fi
	    python $USHevs/subseasonal/subseasonal_stats_grid2grid_create_week4_reformat_job_scripts.py
	    export err=$?; err_chk
	done
	MONTHLY_LIST="Month1"
	for MONTH in $MONTHLY_LIST; do
	    export njobs=53
	    export MONTH=$MONTH
	    if [ "${MONTH}" = "Month1" ]; then
		export CORRECT_INIT_DATE=$PDYm32
		export CORRECT_LEAD_SEQ=0,12,24,36,48,60,72,84,96,108,120,132,144,156,168,180,192,204,216,228,240,252,264,276,288,300,312,324,336,348,360,372,384,396,408,420,432,444,456,468,480,492,504,516,528,540,552,564,576,588,600,612,624,636,648,660,672,684,696,708,720
	    fi
	    python $USHevs/subseasonal/subseasonal_stats_grid2grid_create_monthly_reformat_job_scripts.py
	    export err=$?; err_chk
        done
	DAYS6_10_LIST="Days6_10"
	for DAYS in $DAYS6_10_LIST; do
	    export njobs=55
	    export DAYS=$DAYS
	    if [ "${DAYS}" = "Days6_10" ]; then
		export CORRECT_INIT_DATE=$PDYm12
		export CORRECT_LEAD_SEQ=120,132,144,156,168,180,192,204,216,228,240
	    fi
	    python $USHevs/subseasonal/subseasonal_stats_grid2grid_create_days6_10_reformat_job_scripts.py
	    export err=$?; err_chk
	done
	WEEKS3_4_LIST="Weeks3_4"
	for WEEKS in $WEEKS3_4_LIST; do
	    export njobs=57
	    export WEEKS=$WEEKS
	    if [ "${WEEKS}" = "Weeks3_4" ]; then
		export CORRECT_INIT_DATE=$PDYm30
		export CORRECT_LEAD_SEQ=336,348,360,372,384,396,408,420,432,444,456,468,480,492,504,516,528,540,552,564,576,588,600,612,624,636,648,660,672
	    fi
	    python $USHevs/subseasonal/subseasonal_stats_grid2grid_create_weeks3_4_reformat_job_scripts.py
	    export err=$?; err_chk
	done
	# Create reformat_data POE job scripts
	if [ $USE_CFP = YES ]; then
	    python $USHevs/subseasonal/subseasonal_stats_grid2grid_create_poe_job_scripts.py
	    export err=$?; err_chk
	fi
    else
        echo "Creating and running jobs for grid-to-grid stats: ${JOB_GROUP}"
        python $USHevs/subseasonal/subseasonal_stats_grid2grid_create_job_scripts.py
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

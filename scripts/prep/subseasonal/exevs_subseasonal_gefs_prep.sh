#!/bin/bash
# Program Name: exevs_subseasonal_gefs_prep.sh
# Author(s)/Contact(s): Shannon Shields
# Abstract: This script is run by JEVS_SUBSEASONAL_PREP in jobs/.
#           This script retrieves data for subseasonal GEFS verification.

set -x


echo
echo "===== RUNNING EVS SUBSEASONAL GEFS PREP  ====="
export STEP="prep"

# Source config
source $config
export err=$?; err_chk

# Set up directories
mkdir -p $STEP
cd $STEP

# Check user's configuration file
python $USHevs/subseasonal/check_subseasonal_config_gefs_prep.py
export err=$?; err_chk

# Set up environment variables for initialization, valid, and forecast hours and source them
python $USHevs/subseasonal/set_init_valid_fhr_subseasonal_prep_info.py
export err=$?; err_chk
. $DATA/$STEP/python_gen_env_vars.sh
export err=$?; err_chk

# Create job script
mkdir -p data
export JOB_GROUP=retrieve_data
echo "Creating and running job for GEFS: ${JOB_GROUP}"
python $USHevs/subseasonal/subseasonal_prep_gefs_create_job_scripts.py
export err=$?; err_chk
chmod u+x $DATA/$STEP/prep_job_scripts/retrieve_data/*
nc=1
if [ $USE_CFP = YES ]; then
    group_ncount_poe=$(ls -l  $DATA/$STEP/prep_job_scripts/retrieve_data/poe* |wc -l)
    while [ $nc -le $group_ncount_poe ]; do
	poe_script=$DATA/$STEP/prep_job_scripts/retrieve_data/poe_jobs${nc}
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
    group_ncount_job=$(ls -l  $DATA/$STEP/prep_job_scripts/retrieve_data/job* |wc -l)
    while [ $nc -le $group_ncount_job ]; do
	$DATA/$STEP/prep_job_scripts/retrieve_data/job${nc}
	export err=$?; err_chk
	nc=$((nc+1))
    done
fi

# Send for missing files
if [ $SENDMAIL = YES ] ; then
    if ls $DATA/mail_* 1> /dev/null 2>&1; then
        for FILE in $DATA/mail_*; do
            $FILE
        done
    fi
fi

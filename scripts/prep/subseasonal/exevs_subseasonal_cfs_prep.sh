#!/bin/bash
# Program Name: exevs_subseasonal_cfs_prep
# Author(s)/Contact(s): Shannon Shields
# Abstract: This script is run by JEVS_SUBSEASONAL_PREP in jobs/.
#           This script retrieves data for subseasonal CFS verification.

set -x


echo
echo "===== RUNNING EVS SUBSEASONAL CFS PREP  ====="
export STEP="prep"

# Source config
source $config
export err=$?; err_chk

# Set up directories
mkdir -p $STEP
cd $STEP

# Check user's configuration file
python $USHevs/subseasonal/check_subseasonal_config_cfs_prep.py
export err=$?; err_chk

# Set up environment variables for initialization, valid, and forecast hours and source them
python $USHevs/subseasonal/set_init_valid_fhr_subseasonal_prep_info.py
export err=$?; err_chk
. $DATA/$STEP/python_gen_env_vars.sh
export err=$?; err_chk

# Retrieve needed data files and set up model information
mkdir -p data
python $USHevs/subseasonal/get_cfs_subseasonal_data_files_prep.py
export err=$?; err_chk

# Send for missing files
if [ $SENDMAIL = YES ] ; then
    if ls $DATA/mail_* 1> /dev/null 2>&1; then
        for FILE in $DATA/mail_*; do
	    $FILE
        done
    fi
fi

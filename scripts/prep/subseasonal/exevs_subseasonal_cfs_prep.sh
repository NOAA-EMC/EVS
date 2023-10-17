#!/bin/bash
# Program Name: exevs_subseasonal_cfs_prep
# Author(s)/Contact(s): Shannon Shields
# Abstract: This script is run by JEVS_SUBSEASONAL_PREP in jobs/.
#           This script retrieves data for subseasonal CFS verification.
# History Log:

set -x


echo
echo "===== RUNNING EVS SUBSEASONAL CFS PREP  ====="
export STEP="prep"


# Set up directories
mkdir -p $STEP
cd $STEP

# Check user's configuration file
python $USHevs/subseasonal/check_subseasonal_config_cfs_prep.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran check_subseasonal_config_cfs_prep.py"
echo

# Set up environment variables for initialization, valid, and forecast hours and source them
python $USHevs/subseasonal/set_init_valid_fhr_subseasonal_prep_info.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran set_init_valid_fhr_subseasonal_prep_info.py"
echo
. $DATA/$STEP/python_gen_env_vars.sh
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully sourced python_gen_env_vars.sh"
echo

# Retrieve needed data files and set up model information
mkdir -p data
python $USHevs/subseasonal/get_cfs_subseasonal_data_files_prep.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran get_cfs_subseasonal_data_files_prep.py"
echo

# Send for missing files
if [ $SENDMAIL = YES ] ; then
    if ls $DATA/mail_* 1> /dev/null 2>&1; then
        for FILE in $DATA/mail_*; do
	    $FILE
        done
    fi
fi

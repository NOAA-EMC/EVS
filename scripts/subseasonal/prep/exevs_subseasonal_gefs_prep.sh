#!/bin/bash
# Program Name: exevs_subseasonal_gefs_prep
# Author(s)/Contact(s): Shannon Shields
# Abstract: Retrieve data for subseasonal GEFS verification
# History Log:

set -x


echo
echo "===== RUNNING EVS SUBSEASONAL GEFS PREP  ====="
export STEP="prep"


# Set up directories
mkdir -p $STEP
cd $STEP

# Check user's configuration file
python $USHevs/subseasonal/check_subseasonal_config_gefs_prep.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran check_subseasonal_config_gefs_prep.py"
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
python $USHevs/subseasonal/get_gefs_subseasonal_data_files_prep.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran get_gefs_subseasonal_data_files_prep.py"
echo

# Send for missing files
if ls $DATA/mail_* 1> /dev/null 2>&1; then
    for FILE in $DATA/mail_*; do
        $FILE
    done
fi

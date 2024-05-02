#!/bin/bash
# Program Name: exevs_subseasonal_obs_prep
# Author(s)/Contact(s): Shannon Shields
# Abstract: This script is run by JEVS_SUBSEASONAL_PREP in jobs/.
#           This script retrieves data for subseasonal observations.

set -x


echo
echo "===== RUNNING EVS SUBSEASONAL OBS PREP  ====="
export STEP="prep"

# Source config
source $config
export err=$?; err_chk

# Set up directories
mkdir -p $STEP
cd $STEP

# Check user's configuration file
python $USHevs/subseasonal/check_subseasonal_config_obs_prep.py
export err=$?; err_chk

# Set up environment variables for initialization, valid, and forecast hours and source them
python $USHevs/subseasonal/set_init_valid_fhr_subseasonal_prep_info.py
export err=$?; err_chk
. $DATA/$STEP/python_gen_env_vars.sh
export err=$?; err_chk

# Retrieve needed data files and set up obs information
mkdir -p data
python $USHevs/subseasonal/subseasonal_prep_obs.py
export err=$?; err_chk
. $DATA/$STEP/metplus_precip.sh
# Copy pcp_combine prep file to desired location
if [ $SENDCOM = YES ]; then
    pcp_metplus_file=${DATA}/${STEP}/METplus_output/ccpa/pcp_combine_precip_accum24hr_24hrCCPA_${INITDATE}12.nc
    if [ -s $pcp_metplus_file ]; then
	cp -v $pcp_metplus_file $pcp_arch_file
    fi
fi

# Send for missing files
if [ $SENDMAIL = YES ] ; then
    if ls $DATA/mail_* 1> /dev/null 2>&1; then
        for FILE in $DATA/mail_*; do
            $FILE
        done
    fi
fi

# Cat the METplus log file
log_dir=$DATA/$STEP/METplus_output/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
    for log_file in $log_dir/*; do
	echo "Start: $log_file"
	cat $log_file
	echo "End: $log_file"
    done
fi

#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_atmos_prep.sh
# Purpose of Script: This script does prep for any global deterministic model
#                    atmospheric verification
# Log history:
###############################################################################

set -x 

echo

############################################################
## Global Deterministic Atmospheric Prep
############################################################
python ${USHevs}/global_det/global_det_atmos_prep.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran ${USHevs}/global_det/global_det_atmos_prep.py"

# Send for missing files
if ls $DATA/mail_* 1> /dev/null 2>&1; then
    for FILE in $DATA/mail_*; do
        $FILE
    done
fi

if [ ${KEEPDATA} != YES ]; then
    rm -rf $DATA
fi

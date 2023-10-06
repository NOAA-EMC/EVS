#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_atmos_prep.sh
# Developers: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det atmos prep step
###############################################################################

set -x

echo

# Run prep work for global determinstic model and observations
python ${USHevs}/global_det/global_det_atmos_prep.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran ${USHevs}/global_det/global_det_atmos_prep.py"

# Send for missing files
if [ $SENDMAIL = YES ] ; then
    if ls $DATA/mail_* 1> /dev/null 2>&1; then
        for FILE in $DATA/mail_*; do
            $FILE
        done
    fi
fi

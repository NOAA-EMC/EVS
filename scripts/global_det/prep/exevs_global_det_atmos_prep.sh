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

if [ -f $DATA/${COMPONENT}_${RUN}_${STEP}_missing_files.txt ]; then
    export subject="${COMPONENT} ${RUN} ${STEP} Missing Data for init date ${INITDATE}"
    export maillist=${maillist:-'geoffrey.manikin@noaa.gov, mallory.row@noaa.gov'}
    cat $DATA/${COMPONENT}_${RUN}_${STEP}_missing_files.txt |  mail -s "$subject" $maillist
fi

if [ ${KEEPDATA} != YES ]; then
    rm -rf $DATA
fi

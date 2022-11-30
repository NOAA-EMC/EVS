#!/bin/sh
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

if [ $SENDCOM = YES ]; then
    for mname in $MODELNAME; do
        mkdir -p $COMOUT.$INITDATE/$mname
        for FILE in $DATA/$RUN.$INITDATE/$mname/*; do
            cp -v $FILE $COMOUT.$INITDATE/$mname/.
        done
    done
    for oname in $OBSNAME; do
        mkdir -p $COMOUT.$INITDATE/$oname
        for FILE in $DATA/$RUN.$INITDATE/$oname/*; do
            cp -v $FILE $COMOUT.$INITDATE/$oname/.
        done
    done
fi

if [ ${KEEPDATA} != YES ]; then
    rm -rf $DATA
fi

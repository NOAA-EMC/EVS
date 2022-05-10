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
python ${USHevs}/global_det/global_det_atmos_prep_prod_archive.py

if [ $SENDCOM = YES ]; then
    for MODEL in cfs cmc cmc_regional dwd ecmwf fnmoc gfs imd jma metfra ukmet; do
        mkdir -p $COMOUT/$MODEL
        for FILE in $DATA/$RUN.$INITDATE/$MODEL/*; do
            cp -v $FILE $COMOUT/$MODEL/.
        done
    done
fi

if [ ${KEEPDATA} != YES ]; then
    rm -rf $DATA
fi

#!/bin/sh
###############################################################################
# Name of Script: exevs_global_det_prep.sh  
# Purpose of Script: This script does prep for any global deterministic model
#                    verification
# Log history:
###############################################################################

set -x 

echo

############################################################
## Global Deterministic Atmospheric Prep
############################################################
python ${USHevs}/global_det/global_det_atmos_prep_prod_archive.py

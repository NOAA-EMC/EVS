#!/bin/bash

set -x

export RUNnow=aeronet
mkdir -p $COMOUTprep/$VDATE/$RUNnow

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/metplus_chem.conf \
-c ${CONFIGevs}/$STEP/ASCII2NC_obsAeronet.conf

export err=$?; err_chk

exit



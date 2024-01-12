#!/bin/bash

set -x

export RUNnow=aeronet
mkdir -p $COMOUTprep/$VDATE/$RUNnow
#export metplus_verbosity=2
#export met_verbosity=2
#export METPLUS_PATH
export VDATE=$PDYm2
#export COMINobs=/lfs/h1/ops/dev/dcom/${VDATE}
#export COMOUTprep=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}/$STEP/$COMPONENT

#${MET_PATH}/bin/ascii2nc $COMINobs/validation_data/aq/aeronet/${VDATE}.lev15 $COMOUTprep/${VDATE}/${RUNnow}/All_${VDATE}.lev15.nc -format aeronetv3 -v 6

# convert Aeronet *.lev15 file into a netcdf file using ASCII2NC

${METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/${RUN}_${VERIF_CASE}/metplus_chem.conf \
-c ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/ASCII2NC_obsAeronet.conf

#/usr/bin/env
#${METPLUS_PATH}/ush/run_metplus.py ${PARMevs}/machine.conf ${CONFIGevs}/${RUN}_${VERIF_CASE}/$STEP/ASCII2NC_obsAeronet.conf

export err=$?; err_chk
cat $pgmout

exit



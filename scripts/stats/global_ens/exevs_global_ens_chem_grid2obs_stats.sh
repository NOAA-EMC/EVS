#!/bin/bash
########################################################################
###  UNIX Script Documentation Block
###                      .
### Script name:         exevs_global_ens_chem_grid2obs_stats.sh
### Script description:  To run grid-to-grid verification on all global chem
### Original Author   :  Partha Bhattacharjee
###
###   Change Logs:
###
###   01/16/2024   Ho-Chun Huang  consolidate exevs_global_ens_chem_grid2grid scripts
###
########################################################################
set -x

## For temporary stoage on the working dirary before moving to COMOUT
export finalstat=${DATA}/final
mkdir -p ${finalstat}

export CONFIGevs=${CONFIGevs:-${PARMevs}/${STEP}/$COMPONENT/${RUN}_${VERIF_CASE}}

export METPLUS_PATH

export obstype=`echo ${OBTTYPE} | tr a-z A-Z`

case ${OBTTYPE} in
    aeronet) point_stat_conf_file=PointStat_fcstGEFSAero_obsAeronet.conf;;
    airnow)  export outtyp=pm25
             point_stat_conf_file=PointStat_fcstPM25_obsAirnow.conf;;
esac

#############################
# run Point Stat Analysis
#############################

run_metplus.py -c ${CONFIGevs}/${point_stat_conf_file}
export err=$?; err_chk

exit

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

export model1=`echo ${MODELNAME} | tr a-z A-Z`

export CONFIGevs=${CONFIGevs:-${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}
export config_common=${PARMevs}/metplus_config/machine.conf

export METPLUS_PATH

grid2obs_list="aeronet airnow"

for OBTTYPE in ${grid2obs_list}; do
    export ${OBTTYPE}
    export obstype=`echo ${OBTTYPE} | tr a-z A-Z`

    case ${OBTTYPE} in
        aeronet) point_stat_conf_file=${CONFIGevs}/PointStat_fcstGEFSAero_obsAeronet.conf;;
        airnow)  export outtyp=pm25
                 point_stat_conf_file=${CONFIGevs}/PointStat_fcstGEFSAero_obsAirnow.conf;;
    esac

    #############################
    # run Point Stat Analysis
    #############################

    run_metplus.py ${point_stat_conf_file} ${config_common}
    export err=$?; err_chk

done
exit

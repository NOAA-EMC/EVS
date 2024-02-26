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
###   01/16/2024   Ho-Chun Huang  consolidate exevs_global_ens_chem_grid2obs scripts
###
########################################################################
set -x

cd ${DATA}

## For temporary stoage on the working dirary before moving to COMOUT
export finalstat=${DATA}/final
mkdir -p ${finalstat}

export model1=`echo ${MODELNAME} | tr a-z A-Z`

export CONFIGevs=${CONFIGevs:-${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}
export config_common=${PARMevs}/metplus_config/machine.conf

export METPLUS_PATH

grid2obs_list="aeronet airnow"

export mdl_cyc="00"

flag_send_message=NO
if [ -e mailmsg ]; then /bin/rm -f mailmsg; fi

for OBTTYPE in ${grid2obs_list}; do
    export ${OBTTYPE}
    export obstype=`echo ${OBTTYPE} | tr a-z A-Z`
    point_stat_conf_file=${CONFIGevs}/PointStat_fcstGEFSAero_obs${obstype}.conf;;

##    case ${OBTTYPE} in
##        aeronet) export outtype=aod;;
##        airnow)  export outtype=pm25;;
##    esac

    if [ "${OBTTYPE}" == "aeronet" ]; then
        outtype=aod
        check_file=${EVSINgefs}/${RUN}.${VDATE}/${MODELNAME}/aeronet_All_${VDATE}_lev15.nc
        num_obs_found=0
        if [ -s ${check_file} ]; then
          num_obs_found=1
        else
          echo "WARNING: Can not find pre-processed AEORNET Level 1.5 input ${check_file}"
          if [ "${SENDMAIL}" == "YES" ]; then 
            echo "WARNING: No pre-processed AEORNET Level 1.5 was available for ${VDATE} " >> mailmsg
            echo "Missing file is ${check_file}" >> mailmsg
            echo "==============" >> mailmsg
            flag_send_message=YES
          fi
        fi
        echo "index of daily aeronet obs found = ${num_obs_found}"
    elif [ "${OBTTYPE}" == "airnow" ]; then
        outtype=pm25

        cdate=${VDATE}${vhr}
        vld_date=$(${NDATE} -1 ${cdate} | cut -c1-8)
        vld_time=$(${NDATE} -1 ${cdate} | cut -c1-10)

        check_file=${EVSINaqm}/${RUN}.${vld_date}/${MODELNAME}/airnow_${HOURLY_INPUT_TYPE}_${vld_time}.nc
        num_obs_found=0
        if [ -s ${check_file} ]; then
          num_obs_found=1
        else
          echo "WARNING: Can not find pre-processed obs hourly input ${check_file}"
          if [ "${SENDMAIL}" == "YES" ]; then 
            echo "WARNING: No AQM ${HOURLY_INPUT_TYPE} was available for ${vld_date} ${vld_time}" >> mailmsg
            echo "Missing file is ${check_file}" >> mailmsg
            echo "==============" >> mailmsg
            flag_send_message=YES
          fi
        fi
        echo "index of hourly obs found = ${num_obs_found}"
    fi
    #############################
    # run Point Stat Analysis
    #############################
    #LEAD_SEQ = 0, 3, 6, 9, 12, 15, 18, 21
    checkfile=${COMINgefs}/${MODELNAME}.${VDATE}/${mdl_cyc}/${RUN}/pgrb2ap25
    checkfile=${MODELNAME}.${RUN}.${mdl_cyc}.a2d_0p25.f${filehr}.grib2
FCST_POINT_STAT_INPUT_TEMPLATE = {ENV[MODELNAME]}.{lead?fmt=%Y%m%d}/{ENV[mdl_cyc]}/{ENV[RUN]}/pgrb2ap25/{ENV[MODELNAME]}.{ENV[RUN]}.{cycle}.a2d_0p25.f{lead?fmt=%3H}.grib2
    run_metplus.py ${point_stat_conf_file} ${config_common}
    export err=$?; err_chk

done
if [ "${flag_send_message}" == "YES" ]; then
    export subject="pre-process AERONET or Hourly Observed AirNOW Missing for EVS ${COMPONENT}"
    echo "Job ID: ${jobid}" >> mailmsg
    cat mailmsg | mail -s "${subject}" ${MAILTO}
fi 
exit

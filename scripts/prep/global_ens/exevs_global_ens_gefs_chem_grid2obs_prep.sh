#!/bin/bash
########################################################################
###  UNIX Script Documentation Block
###                      .
### Script name:         exevs_global_ens_chem_grid2obs_prep.sh
### Script description:  To run grid-to-obs verification on GEFS-aerosol (chem-component)
### Original Author   :  Partha Bhattacharjee
###
###   Change Logs:
###
###   01/16/2024   Ho-Chun Huang  EVSv1.0 EE2 compliance
###   01/30/2024   Ho-Chun Huang  for a single email of missing files of both OBS and FCST
###
########################################################################
#
set -x

cd ${DATA}
########################################################################
## Pre-Processed Observations
########################################################################
#
## For temporary stoage on the working dirary before moving to COMOUT with SENDCOM setting
#
export finalprep=${DATA}/final
mkdir -p ${finalprep}

obstype="aeronet airnow"
export CONFIGevs=${CONFIGevs:-${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}
export config_common=${PARMevs}/metplus_config/machine.conf

flag_send_message=NO
if [ -e mailmsg ]; then /bin/rm -f mailmsg; fi

for OBTTYPE in ${obstype}; do
    export OBTTYPE
    export obstype=`echo ${OBTTYPE} | tr a-z A-Z`
    prep_config_file=${CONFIGevs}/ASCII2NC_obs${obstype}.conf

    if [ "${OBTTYPE}" == "aeronet" ]; then
        checkfile=${DCOMIN}/${VDATE}/validation_data/aq/${OBTTYPE}/${VDATE}.lev15
        if [ -s ${checkfile} ]; then
            if [ -s ${prep_config_file} ]; then
                run_metplus.py ${prep_config_file} ${config_common}
                export err=$?; err_chk
                if [ ${SENDCOM} = "YES" ]; then
                    cpfile=${finalprep}/${OBTTYPE}_All_${VDATE}_lev15.nc
                    if [ -e ${cpfile} ]; then
                        cp -v ${cpfile} ${COMOUTprep}
                    fi
                fi
            else
                echo "WARNING: can not find ${prep_config_file}"
            fi
        else
            if [ ${SENDMAIL} = "YES" ]; then
                echo "WARNING: No AEORNET Level 1.5 data was available for valid date ${VDATE}" >> mailmsg
                echo "Missing file is ${checkfile}" >> mailmsg
                echo "==============" >> mailmsg
                flag_send_message=YES
            fi
            echo "WARNING: No AEORNET Level 1.5 data was available for valid date ${VDATE}"
            echo "WARNING: Missing file is ${checkfile}"
        fi
    elif [ "${OBTTYPE}" == "airnow" ]; then
        airnow_hourly_type="aqobs"
        if [ "${airnow_hourly_type}" == "aqobs" ]; then
            export HOURLY_INPUT_TYPE=HourlyAQObs
            export HOURLY_OUTPUT_TYPE=hourly_aqobs
            export HOURLY_ASCII2NC_FORMAT=airnowhourlyaqobs
        else
            export HOURLY_INPUT_TYPE=HourlyData
            export HOURLY_OUTPUT_TYPE=hourly_data
            export HOURLY_ASCII2NC_FORMAT=airnowhourly
        fi
         
        ## Pre-Processed EPA AIRNOW ASCII input file to METPlus NetCDF input for PointStat
        ##
        ## Hourly AirNOW observation
        ##
        let ic=0
        let endvhr=23
        while [ ${ic} -le ${endvhr} ]; do
            vldhr=$(printf %2.2d ${ic})
            checkfile=${DCOMIN}/${VDATE}/airnow/${HOURLY_INPUT_TYPE}_${VDATE}${vldhr}.dat
            if [ -s ${checkfile} ]; then
                export VHOUR=${vldhr}
                if [ -s ${prep_config_file} ]; then
                    run_metplus.py ${prep_config_file} ${config_common}
                    export err=$?; err_chk
                    if [ ${SENDCOM} = "YES" ]; then
                        cpfile=${finalprep}/airnow_hourly_aqobs_${VDATE}${VHOUR}.nc 
                        if [ -e ${cpfile} ]; then cp -v ${cpfile} ${COMOUTprep}; fi
                    fi
                else
                    echo "WARNING: can not find ${prep_config_file}"
                fi
            else
                if [ ${SENDMAIL} = "YES" ]; then
                    echo "WARNING: No AIRNOW ASCII data was available for valid date ${VDATE}${vldhr}" >> mailmsg
                    echo "Missing file is ${checkfile}" >> mailmsg
                    echo "==============" >> mailmsg
                    flag_send_message=YES
                fi
        
                echo "WARNING: No AIRNOW ASCII data was available for valid date ${VDATE}${vldhr}"
                echo "WARNING: Missing file is ${checkfile}"
            fi
            ((ic++))
        done
    else
        echo "DEBUG :: OBTTYPE=${OBTTYPE} is not defined for ${COMPONENT}_${RUN} ${STEP} operationa"
    fi

done
#
########################################################################
## Backup GEFS-aerosol output for global_ens_chem_grid2obs stats step
########################################################################
if [ ${SENDCOM} = "YES" ]; then
    NOW=${VDATE}
    declare -a cyc_opt=( 00 06 12 18 )
    let inc=3
    for mdl_cyc in "${cyc_opt[@]}"; do
        com_gefs=${COMINgefs}/${MODELNAME}.${NOW}/${mdl_cyc}/${RUN}/pgrb2ap25
        if [ -d ${com_gefs} ]; then
            prep_gefs=${COMOUTprep}/${mdl_cyc}/${RUN}/pgrb2ap25
	    mkdir -p ${prep_gefs}
            let hour_now=3
            let max_hour=120
            while [ ${hour_now} -le ${max_hour} ]; do
                fhr=`printf %3.3d ${hour_now}`
                cpfile=${com_gefs}/${MODELNAME}.${RUN}.t${mdl_cyc}z.a2d_0p25.f${fhr}.grib2
                if [ -s ${cpfile} ]; then
                    cp -v ${cpfile} ${prep_gefs}
                else
                    if [ ${SENDMAIL} = "YES" ]; then
                        echo "WARNING: Can not find GEFS-aerosol forecast output" >> mailmsg
                        echo "Missing file is ${cpfile}" >> mailmsg
                        echo "==============" >> mailmsg
                        flag_send_message=YES
                    fi
                    echo "WARNING: Can not find GEFS-aerosol forecast output" >> mailmsg
                    echo "Missing file is ${cpfile}" >> mailmsg
                fi
                ((hour_now+=${inc}))
            done
        else
            if [ ${SENDMAIL} = "YES" ]; then
                echo "WARNING: Can not find GEFS-aerosol output directory ${com_gefs}" >> mailmsg
                echo "==============" >> mailmsg
                flag_send_message=YES
            fi
            echo "WARNING: Can not find GEFS-aerosol output directory ${com_gefs}" >> mailmsg
        fi
    done
fi
#
if [ "${flag_send_message}" == "YES" ]; then
    export subject="AEORNET Level 1.5 NC or AIRNOW ASCII Hourly Data Missing for EVS ${COMPONENT}_${RUN}"
    echo "Job ID: ${jobid}" >> mailmsg
    cat mailmsg | mail -s "${subject}" ${MAILTO}
fi 

exit

#######################################################################
# Define INPUT OBS DATA TYPE for ASCII2NC 
#######################################################################
#


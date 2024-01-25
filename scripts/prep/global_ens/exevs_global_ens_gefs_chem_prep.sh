#!/bin/bash
########################################################################
###  UNIX Script Documentation Block
###                      .
### Script name:         exevs_global_ens_chem_grid2obs_prep.sh
### Script description:  To run grid-to-grid verification on all global chem
### Original Author   :  Partha Bhattacharjee
###
###   Change Logs:
###
###   01/16/2024   Ho-Chun Huang  EVSv1.0 EE2 compliance
###
########################################################################
set -x

## For temporary stoage on the working dirary before moving to COMOUT
export finalprep=${DATA}/final
mkdir -p ${finalprep}

obstype="aeronet airnow"
export CONFIGevs=${CONFIGevs:-${PARMevs}/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}

for OBTTYPE in ${obstype}; do
    export OBTTYPE
    export obstype=`echo ${OBTTYPE} | tr a-z A-Z`
    config_file=${CONFIGevs}/ASCII2NC_obs${obstype}.conf

    if [ "${OBTTYPE}" == "aeronet" ]; then
        checkfile=${DCOMIN}/${VDATE}/validation_data/aq/${OBTTYPE}/${VDATE}.lev15
        if [ -s ${checkfile} ]; then
            if [ -s ${config_file} ]; then
                run_metplus.py ${config_file}
                export err=$?; err_chk
                if [ ${SENDCOM} = "YES" ]; then
                    cpfile=${finalprep}/${OBTTYPE}_All_${VDATE}_lev15.nc
                    if [ -e ${cpfile} ]; then
                        if [ ! -d ${COMOUTprep} ]; then mkdir -p ${COMOUTprep}; fi
                        cpreq ${cpfile} ${COMOUTprep}
                    fi
                fi
            else
                echo "WARNING: can not find ${config_file}"
            fi
        else
            if [ ${SENDMAIL} = "YES" ]; then
                export subject="AEORNET Level 1.5 NC file Missing for EVS ${COMPONENT}_${RUN}"
                echo "WARNING: No AEORNET Level 1.5 data was available for valid date ${VDATE}" > mailmsg
                echo "Missing file is ${checkfile}" >> mailmsg
                echo "Job ID: $jobid" >> mailmsg
                cat mailmsg | mail -s "$subject" $MAILTO 
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
        	if [ -s ${conf_file} ]; then
                    run_metplus.py ${conf_file}
        	    export err=$?; err_chk
        	    if [ ${SENDCOM} = "YES" ]; then
                        cpfile=${finalprep}/airnow_hourly_aqobs_${VDATE}${VHOUR}.nc 
                        if [ -e ${cpfile} ]; then cpreq ${cpfile} ${COMOUTprep}; fi
        	    fi
                else
                    echo "WARNING: can not find ${conf_file}"
        	fi
            else
                if [ ${SENDMAIL} = "YES" ]; then
                    export subject="AIRNOW ASCII Hourly Data Missing for EVS ${COMPONENT}_${RUN}"
                    echo "WARNING: No AIRNOW ASCII data was available for valid date ${VDATE}${vldhr}" > mailmsg
                    echo "Missing file is ${checkfile}" >> mailmsg
                    echo "Job ID: $jobid" >> mailmsg
                    cat mailmsg | mail -s "$subject" $MAILTO 
                fi
        
                echo "WARNING: No AIRNOW ASCII data was available for valid date ${VDATE}${vldhr}"
                echo "WARNING: Missing file is ${checkfile}"
            fi
            ((ic++))
        done
    else
	echo "DEBUG :: OBTTYPE=${OBTTYPE}" is not define for ${STEP} operationa"
    fi

done
exit

#######################################################################
# Define INPUT OBS DATA TYPE for ASCII2NC 
#######################################################################
#


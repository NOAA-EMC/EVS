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
        checkfile=${DCOMINaeronet}/${INITDATE}/validation_data/aq/${OBTTYPE}/${INITDATE}.lev15
        if [ -s ${checkfile} ]; then
            screen_file=${DATA}/checked_${OBTTYPE}_${INITDATE}.lev15
            python ${USHevs}/${COMPONENT}/screen_aeronet_aod_lev15.py ${checkfile} ${screen_file}
            export err=$?; err_chk
            number_of_record=$(wc -l ${screen_file} | awk -F" " '{print $1}')
            ## There is 6 comment and header lines 
            if [ ${number_of_record} -gt 6 ]; then
                if [ -s ${prep_config_file} ]; then
                    run_metplus.py ${prep_config_file} ${config_common}
                    export err=$?; err_chk
                    if [ ${SENDCOM} = "YES" ]; then
                        cpfile=${finalprep}/${OBTTYPE}_All_${INITDATE}_lev15.nc
                        if [ -e ${cpfile} ]; then
                            cp -v ${cpfile} ${COMOUTprep}
                        fi
                    fi
                else
                    echo "WARNING: can not find ${prep_config_file}"
                fi
            else
                if [ ${SENDMAIL} = "YES" ]; then
                    echo "DEBUG : There is no valid record to be processed for ${checkfile}" >> mailmsg
                    echo "File in question is ${checkfile}" >> mailmsg
                    echo "==============" >> mailmsg
                    flag_send_message=YES
                fi
                echo "DEBUG : There is no valid record to be processed for ${checkfile}"
            fi
        else
            if [ ${SENDMAIL} = "YES" ]; then
                echo "WARNING: No AEORNET Level 1.5 data was available for valid date ${INITDATE}" >> mailmsg
                echo "Missing file is ${checkfile}" >> mailmsg
                echo "==============" >> mailmsg
                flag_send_message=YES
            fi
            echo "WARNING: No AEORNET Level 1.5 data was available for valid date ${INITDATE}"
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
            checkfile=${DCOMINairnow}/${INITDATE}/${OBTTYPE}/${HOURLY_INPUT_TYPE}_${INITDATE}${vldhr}.dat
            if [ -s ${checkfile} ]; then
                screen_file=${DATA}/checked_${HOURLY_INPUT_TYPE}_${INITDATE}${vldhr}.dat
                python ${USHevs}/${COMPONENT}/screen_airnow_obs_hourly.py ${checkfile} ${screen_file}
                export err=$?; err_chk
                number_of_record=$(wc -l ${screen_file} | awk -F" " '{print $1}')
                ## There is 1 header lines 
                if [ ${number_of_record} -gt 1 ]; then
                    export VHOUR=${vldhr}
                    if [ -s ${prep_config_file} ]; then
                        run_metplus.py ${prep_config_file} ${config_common}
                        export err=$?; err_chk
                        if [ ${SENDCOM} = "YES" ]; then
                            cpfile=${finalprep}/airnow_hourly_aqobs_${INITDATE}${VHOUR}.nc 
                            if [ -e ${cpfile} ]; then cp -v ${cpfile} ${COMOUTprep}; fi
                        fi
                    else
                        echo "WARNING: can not find ${prep_config_file}"
                    fi
                else
                    if [ ${SENDMAIL} = "YES" ]; then
                        echo "DEBUG : There is no valid record to be processed for ${checkfile}" >> mailmsg
                        echo "File in question is ${checkfile}" >> mailmsg
                        echo "==============" >> mailmsg
                        flag_send_message=YES
                    fi
                    echo "DEBUG : There is no valid record to be processed for ${checkfile}"
                fi
            else
                if [ ${SENDMAIL} = "YES" ]; then
                    echo "WARNING: No AIRNOW ASCII data was available for valid date ${INITDATE}${vldhr}" >> mailmsg
                    echo "Missing file is ${checkfile}" >> mailmsg
                    echo "==============" >> mailmsg
                    flag_send_message=YES
                fi
        
                echo "WARNING: No AIRNOW ASCII data was available for valid date ${INITDATE}${vldhr}"
                echo "WARNING: Missing file is ${checkfile}"
            fi
            ((ic++))
        done
    else
        echo "DEBUG :: OBTTYPE=${OBTTYPE} is not defined for ${COMPONENT}_${RUN} ${STEP} step"
    fi

done
#
########################################################################
##  Extract variables from full GEFS-aerosol output to be verified
##    against observation and option to used already recuded
##    GEFS-aerosol output (suitable for restrospective run)
##  Backup GEFS-aerosol reduced output for global_ens_chem_grid2obs
##    stats step due to insuccficent retention time (at least 6 days)
########################################################################
match_aod_1=":AOTK:"
match_aod_2="aerosol=Total Aerosol"
match_aod_3="aerosol_size <2e-05"
match_aod_4="aerosol_wavelength >=5.45e-07,<=5.65e-07"
match_pm25_1="PMTF"
match_pm25_2="aerosol=Total Aerosol"
match_pm25_3="aerosol_size <2.5e-06"
declare -a cyc_opt=( 00 06 12 18 )
let inc=3
for mdl_cyc in "${cyc_opt[@]}"; do
    com_gefs=${COMINgefs}/${MODELNAME}.${INITDATE}/${mdl_cyc}/${RUN}/pgrb2ap25
    if [ -d ${com_gefs} ]; then
        prep_gefs=${COMOUTprep}/${mdl_cyc}/${RUN}/pgrb2ap25
        mkdir -p ${prep_gefs}
        let hour_now=0
        let max_hour=120
        while [ ${hour_now} -le ${max_hour} ]; do
            fhr=`printf %3.3d ${hour_now}`
            mdl_full_grib2=${MODELNAME}.${RUN}.t${mdl_cyc}z.a2d_0p25.f${fhr}.grib2
            reduced_rec_grib2=${MODELNAME}.${RUN}.t${mdl_cyc}z.a2d_0p25.f${fhr}.reduced.grib2
            check_full_file=${com_gefs}/${mdl_full_grib2}
            check_reduced_file=${com_gefs}/${reduced_rec_grib2}
            if [ -s ${check_reduced_file} ]; then
                echo "Found file ${check_reduced_file}"
                if [ ${SENDCOM} = "YES" ]; then
                    cp -v ${check_reduced_file} ${prep_gefs}
                fi
            elif [ -s ${check_full_file} ]; then
                if [ -e extract_aod ]; then /bin/rm -rf extract_aod; fi
                if [ -e extract_pm25 ]; then /bin/rm -rf extract_pm25; fi
                wgrib2 -match "${match_aod_1}" -match "${match_aod_2}" -match "${match_aod_3}" -match "${match_aod_4}" ${check_full_file} -grib extract_aod
                wgrib2 -match "${match_pm25_1}" -match "${match_pm25_2}" -match "${match_pm25_3}" ${check_full_file} -grib extract_pm25
                cat extract_aod extract_pm25 > ${reduced_rec_grib2}
                if [ ${SENDCOM} = "YES" ]; then
                    cp -v ${reduced_rec_grib2} ${prep_gefs}
                fi
            else
                if [ ${SENDMAIL} = "YES" ]; then
                    echo "WARNING: Can not find GEFS-aerosol forecast output" >> mailmsg
                    echo "Missing file is ${check_full_file}" >> mailmsg
                    echo "==============" >> mailmsg
                    flag_send_message=YES
                fi
                echo "WARNING: Can not find GEFS-aerosol forecast output" >> mailmsg
                echo "Missing file is ${check_full_file}" >> mailmsg
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

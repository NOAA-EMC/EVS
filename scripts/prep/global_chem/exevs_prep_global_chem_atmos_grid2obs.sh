#!/bin/bash
########################################################################
###  UNIX Script Documentation Block
###                      .
### Script name:         exevs_prep_global_chem_atmos_grid2obs.sh
### Script description:  To run grid-to-obs verification on Global Chemical modeling
### Original Author   :  Partha Bhattacharjee
###
###   Change Logs:
###
###   01/16/2024   Ho-Chun Huang  EVSv1.0 EE2 compliance
###   01/30/2024   Ho-Chun Huang  for a single email of missing files of both OBS and FCST
###   05/01/2025   Ho-Chun Huang  Remove email function for missing model forecast output
###   05/22/2025   Ho-Chun Huang  Move from global_ens chem to global_chem
###   10/07/2025   Ho-Chun Huang  Revise code for GCAFSv1 naming and data structure
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
                            mkdir -p ${COMOUTprepobs}
                            cp -v ${cpfile} ${COMOUTprepobs}
                        fi
                    fi
                fi
            else
                if [ ${SENDMAIL} = "YES" ]; then
                    echo "WARNING: There is no valid record to be processed, ${COMPONENT} ${MODELNAME} ${STEP} will skip ${checkfile}" >> mailmsg
                    echo "==============" >> mailmsg
                    flag_send_message=YES
                fi
                echo "WARNING: There is no valid record to be processed, ${COMPONENT} ${MODELNAME} ${STEP} will skip ${checkfile}"
            fi
        else
            if [ ${SENDMAIL} = "YES" ]; then
                echo "WARNING: ${checkfile} is missing, ${COMPONENT} ${MODELNAME} ${STEP} will skip this file for valid date ${INITDATE}" >> mailmsg
                echo "==============" >> mailmsg
                flag_send_message=YES
            fi
            echo "WARNING: ${checkfile} is missing, ${COMPONENT} ${MODELNAME} ${STEP} will skip this file for valid date ${INITDATE}"
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
        ##
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
                            if [ -e ${cpfile} ]; then
                                mkdir -p ${COMOUTprepobs}
                                cp -v ${cpfile} ${COMOUTprepobs}
                            fi
                        fi
                    fi
                else
                    if [ ${SENDMAIL} = "YES" ]; then
                        echo "WARNING: There is no valid record to be processed, ${COMPONENT} ${MODELNAME} ${STEP} will skip the ${checkfile}" >> mailmsg
                        echo "==============" >> mailmsg
                        flag_send_message=YES
                    fi
                    echo "WARNING: There is no valid record to be processed, ${COMPONENT} ${MODELNAME} ${STEP} will skip the ${checkfile}"
                fi
            else
                if [ ${SENDMAIL} = "YES" ]; then
                    echo "WARNING: ${checkfile} is missing, ${COMPONENT} ${MODELNAME} ${STEP} will skip this file for valid date ${INITDATE}" >> mailmsg
                    echo "==============" >> mailmsg
                    flag_send_message=YES
                fi
        
                echo "WARNING: ${checkfile} is missing, ${COMPONENT} ${MODELNAME} ${STEP} will skip this file for valid date ${INITDATE}"
            fi
            ((ic++))
        done
    else
        echo "DEBUG :: OBTTYPE=${OBTTYPE} is not defined for ${COMPONENT} ${MODELNAME} ${STEP} step"
    fi

done
#
########################################################################
##  Extract variables from full Global-Chemical output to be verified
##    against observation and option to used already recuded
##    Global-Chemical output (suitable for restrospective run)
##  Backup Global-Chemical reduced output for global_chem_atmos_grid2obs
##    stats step due to insuccficent retention time (at least 6 days)
########################################################################
readonly MATCH_AOD=("-match" ":AOTK:" "-match" "aerosol=Total Aerosol" "-match" "aerosol_size <2e-05" "-match" "aerosol_wavelength >=5.5e-07,<=5.5e-07")
readonly MATCH_PM25=("-match" "PMTF" "-match" "aerosol=Total Aerosol" "-match" "aerosol_size <2.5e-06")
readonly MATCH_PM10=("-match" "PMTC" "-match" "aerosol=Total Aerosol" "-match" "aerosol_size <1e-05")

declare -a cyc_opt=( 00 12 )
let inc=3
for mdl_cyc in "${cyc_opt[@]}"; do
    com_gc_mdl=${COMINgcafs}/${MODELNAME}.${INITDATE}/${mdl_cyc}/products/${RUN}/grib2/0p25
    if [ -d ${com_gc_mdl} ]; then
        prep_gc_mdl=${COMOUTprepmdl}/${mdl_cyc}/products/${RUN}/grib2/0p25
        mkdir -p ${prep_gc_mdl}
        let hour_now=0
        let max_hour=120
        while [ ${hour_now} -le ${max_hour} ]; do
            fhr=`printf %3.3d ${hour_now}`
            mdl_full_grib2="${MODELNAME}.t${mdl_cyc}z.pres_a.0p25.f${fhr}.grib2"
            mdl_trim_grib2="${MODELNAME}.${RUN}.t${mdl_cyc}z.0p25.f${fhr}.trim.grib2"
            check_full_file=${com_gc_mdl}/${mdl_full_grib2}
            check_trim_file=${com_gc_mdl}/${mdl_trim_grib2}
            if [ -s ${check_trim_file} ]; then
                echo "Found file ${check_trim_file}"
                if [ ${SENDCOM} = "YES" ]; then
                    cp -v ${check_trim_file} ${prep_gc_mdl}
                fi
            elif [ -s ${check_full_file} ]; then
                wgrib2 "${check_full_file}" "${MATCH_AOD[@]}" -grib "${mdl_trim_grib2}"
                wgrib2 "${check_full_file}" "${MATCH_PM25[@]}" -append -grib "${mdl_trim_grib2}"
                wgrib2 "${check_full_file}" "${MATCH_PM10[@]}" -append -grib "${mdl_trim_grib2}"
                if [ ${SENDCOM} = "YES" ]; then
                    cp -v ${mdl_trim_grib2} ${prep_gc_mdl}
                fi
            else
                echo "FCST_OUTPUT_MISSING: Global-Chemical forecast file ${check_full_file} is missing. The missing Global-Chemical forecast file will be skipped"
            fi
            ((hour_now+=${inc}))
        done
    else
        echo "FCST_OUTPUT_MISSING: Global-Chemical output directory ${com_gc_mdl} is missing. The missing Global-Chemical forecast files will be skipped"
    fi
done
#
if [ "${flag_send_message}" == "YES" ]; then
    export subject="AERONET Level 1.5 NC or AIRNOW ASCII Hourly Data Missing for EVS ${COMPONENT}_${RUN}"
    echo "Job ID: ${jobid}" >> mailmsg
    cat mailmsg | mail -s "${subject}" ${MAILTO}
fi 

exit

#######################################################################
# Define INPUT OBS DATA TYPE for ASCII2NC 
#######################################################################
#

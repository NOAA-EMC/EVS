#!/bin/bash
########################################################################
###  UNIX Script Documentation Block
###                      .
### Script name:         exevs_prep_cam_rrfs_chem_grid2obs.sh
### Script description:  To run grid-to-obs verification on RRFS-Smoke and Dust
### Original Author   :  Ho-Chun Huang
###
###   Change Logs:
###   03/20/2026   Ho-Chun Huang  Revised code for RRFS-Chem from AQM prep code
###
########################################################################
#
set -x

cd ${DATA}
#
########################################################################
## Pre-Processed Observations
########################################################################
#
########################################################################
## For temporary stoage on the working dirary before moving to COMOUT with SENDCOM setting
########################################################################
#
export finalprep=${DATA}/final
mkdir -p ${finalprep}

obstype="aeronet airnow"
export CONFIGevs=${CONFIGevs:-${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}
export config_common=${PARMevs}/metplus_config/machine.conf

flag_send_message=NO
email_msg=${DATA}/mailmsg
if [ -e ${email_msg} ]; then /bin/rm -f ${email_msg}; fi

check_restart=$( echo ${restart_mode} | tr a-z A-Z )

for OBTTYPE in ${obstype}; do
    export OBTTYPE
    export obstype=$( echo ${OBTTYPE} | tr a-z A-Z )
    prep_config_file=${CONFIGevs}/ASCII2NC_obs${obstype}.conf

    if [ "${OBTTYPE}" == "aeronet" ]; then
        flag_process_ascii_aeronet="YES"
        if [ "${check_restart}" == "YES" ]; then   ## Check ASCII2NC AERONET AOD file for RESTART ability
            checkfile=${COMOUTprepobs}/${OBTTYPE}_All_${INITDATE}_lev15.nc
            if [ -s ${checkfile} ]; then
                msg=$(ncdump -h ${checkfile} 1> /dev/null 2>&1 ; err=$? ; echo ${err} )
                if [ ${msg} -eq 0 ]; then flag_process_ascii_aeronet="NO"; fi
            fi
        fi
        ##
        ## Pre-Processed AERONET AOD input ascii file to METPlus NetCDF input for PointStat
        ##
        checkfile=${DCOMINaeronet}/${INITDATE}/validation_data/aq/${OBTTYPE}/${INITDATE}.lev15
        if [ -s ${checkfile} ] && [ "${flag_process_ascii_aeronet}" == "YES" ]; then
            screen_file=${DATA}/checked_${OBTTYPE}_${INITDATE}.lev15
            python ${USHevs}/${COMPONENT}/cam_chem_screen_aeronet_aod_lev15.py ${checkfile} ${screen_file}
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
                    echo "WARNING: There is no valid record to be processed, ${MODELNAME} ${RUN} ${STEP} will skip ${checkfile}" >> ${email_msg}
                    echo "==============" >> ${email_msg}
                    flag_send_message=YES
                fi
                echo "WARNING: There is no valid record to be processed, ${MODELNAME} ${RUN} ${STEP} will skip ${checkfile}"
            fi
        else
            if [ "${flag_process_ascii_aeronet}" == "NO" ]; then
                echo "DEBUG: ASCII2NC AERONET AOD files has been found.  RESTART Skip ASCII2NC processing"
            elif [ ! -s ${checkfile} ]; then
                if [ ${SENDMAIL} = "YES" ]; then
                    echo "WARNING: ${checkfile} is missing, ${MODELNAME} ${RUN} ${STEP} will skip this file for valid date ${INITDATE}" >> ${email_msg}
                    echo "==============" >> ${email_msg}
                    flag_send_message=YES
                fi
                echo "WARNING: ${checkfile} is missing, ${MODELNAME} ${RUN} ${STEP} will skip this file for valid date ${INITDATE}"
            fi
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

        let ic=0
        let endvhr=23
        let total_num_file=${endvhr}+1
  
        if [ "${check_restart}" == "YES" ]; then   ## Check ASCII2NC AIRNOW files for RESTART ability
            checkfile="${OBTTYPE}_${HOURLY_OUTPUT_TYPE}_*.nc"
            obs_file_count=$(find ${COMOUTprepobs} -name ${checkfile} | wc -l )
            if [ ${obs_file_count} -eq 0 ]; then
              let ic=0
            elif [ ${obs_file_count} -eq ${total_num_file} ]; then
              ## check corrupted ASCII2NC file
              vldhr=$(printf %2.2d ${endvhr})
              checkfile="${COMOUTprepobs}/${OBTTYPE}_${HOURLY_OUTPUT_TYPE}_${INITDATE}${vldhr}.nc"
              msg=$(ncdump -h ${checkfile} 1> /dev/null 2>&1 ; err=$? ; echo ${err} )
              if [ ${msg} -eq 0 ]; then
                let ic=${endvhr}+1   ## skip current AIRNOW Processing
                echo "DEBUG: RESTART Skip ASCII2NC Porcessing for ${obstype}"
              else
                let ic=${endvhr}     ## file corrupted re-do the last hour ASCII2NC process
                echo "DEBUG: RESTART ASCII2NC for ${obstype} from hour ${ic}"
              fi
            else
              let ic=${obs_file_count}-1
              echo "DEBUG: RESTART ASCII2NC for ${obstype} from ${ic}"
            fi
        fi
        ##
        ## Pre-Processed EPA AIRNOW ASCII input file to METPlus NetCDF input for PointStat
        ## Hourly AirNOW observation
        ##
        while [ ${ic} -le ${endvhr} ]; do
            vldhr=$(printf %2.2d ${ic})
            checkfile=${DCOMINairnow}/${INITDATE}/${OBTTYPE}/${HOURLY_INPUT_TYPE}_${INITDATE}${vldhr}.dat
            if [ -s ${checkfile} ]; then
                screen_file=${DATA}/checked_${HOURLY_INPUT_TYPE}_${INITDATE}${vldhr}.dat
                python ${USHevs}/${COMPONENT}/cam_chem_screen_airnow_obs_hourly.py ${checkfile} ${screen_file}
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
                        echo "WARNING: There is no valid record to be processed, ${MODELNAME} ${RUN} ${STEP} will skip the ${checkfile}" >> ${email_msg}
                        echo "==============" >> ${email_msg}
                        flag_send_message=YES
                    fi
                    echo "WARNING: There is no valid record to be processed, ${MODELNAME} ${RUN} ${STEP} will skip the ${checkfile}"
                fi
            else
                if [ ${SENDMAIL} = "YES" ]; then
                    echo "WARNING: ${checkfile} is missing, ${MODELNAME} ${RUN} ${STEP} will skip this file for valid date ${INITDATE}" >> ${email_msg}
                    echo "==============" >> ${email_msg}
                    flag_send_message=YES
                fi
        
                echo "WARNING: ${checkfile} is missing, ${MODELNAME} ${RUN} ${STEP} will skip this file for valid date ${INITDATE}"
            fi
            ((ic++))
        done
    else
        echo "DEBUG: OBTTYPE=${OBTTYPE} is not defined for ${COMPONENT}_${RUN} ${STEP} step"
    fi
done
#
########################################################################
## Pre-Processed Model output for EVS
########################################################################

# Define matching strings
match_aod="AOTK:entire atmosphere"
match_pm25="MASSDEN:8 m above ground:.*aerosol=Total Aerosol:.*aerosol_size <2.5e-06"
match_pm10="MASSDEN:8 m above ground:.*aerosol=Total Aerosol:.*aerosol_size <1e-05"

declare -a cyc_opt=( 00 06 12 18 )
let inc=1

for mdl_cyc in "${cyc_opt[@]}"; do
    com_rrfs_mdl=${COMINrrfs}/${MODELNAME}.${INITDATE}/${mdl_cyc}
    if [ -d "${com_rrfs_mdl}" ]; then
        prep_rrfs=${COMOUTprepmdl}/${mdl_cyc}
        mkdir -p "${prep_rrfs}"
        
        let hour_now=1
        let max_hour=84
  
        # --- RESTART Logic ---
        if [ "${check_restart}" == "YES" ]; then
            checkfile_pattern="${MODELNAME}.t${mdl_cyc}z.evsin.f*.trim.grib2"
            mdl_file_count=$(find "${prep_rrfs}" -name "${checkfile_pattern}" | wc -l)
            
            if [ ${mdl_file_count} -eq ${max_hour} ]; then
                # Check if the last file is healthy
                fhr3_last=$(printf %3.3d ${max_hour})
                last_file="${prep_rrfs}/${MODELNAME}.t${mdl_cyc}z.evsin.f${fhr3_last}.trim.grib2"
                if wgrib2 -V "${last_file}" > /dev/null 2>&1; then
                    echo "DEBUG :: Cycle ${mdl_cyc} complete. Skipping."
                    continue 
                fi
            fi
            hour_now=$((mdl_file_count > 0 ? mdl_file_count : 1))
        fi

        # --- Extraction Loop ---
        while [ ${hour_now} -le ${max_hour} ]; do
            fhr3=$(printf %3.3d ${hour_now})
            mdl_full_grib2="${MODELNAME}.t${mdl_cyc}z.2dfld.3km.f${fhr3}.na.grib2"
            mdl_trim_grib2="${MODELNAME}.t${mdl_cyc}z.evsin.f${fhr3}.trim.grib2"
            
            check_full_file="${com_rrfs_mdl}/${mdl_full_grib2}"
            check_trim_file="${com_rrfs_mdl}/${mdl_trim_grib2}"

            if [ -s "${check_trim_file}" ]; then
                echo "Found trim file: ${check_trim_file}"
                [ "${SENDCOM}" = "YES" ] && cp -v "${check_trim_file}" "${prep_rrfs}"
            elif [ -s "${check_full_file}" ]; then
                echo "Processing: ${mdl_full_grib2}"
                
                # Single-pass extraction for AOD, PM2.5, and PM10
                wgrib2 "${check_full_file}" \
                    -match "(${match_aod}|${match_pm25}|${match_pm10})" \
                    -grib "${mdl_trim_grib2}" > "${mdl_trim_grib2}.inv"

                num_rec=$(wc -l < "${mdl_trim_grib2}.inv")
                echo "DEBUG: Extracted ${num_rec} records for fhr ${fhr3}"
                
                # Cleanup inventory and move to final prep dir
                rm -f "${mdl_trim_grib2}.inv"
                
                if [ "${SENDCOM}" = "YES" ] && [ -s "${mdl_trim_grib2}" ]; then
                    cp -v "${mdl_trim_grib2}" "${prep_rrfs}"
                fi
            else
                echo "FCST_OUTPUT_MISSING: ${check_full_file} not found. Skipping."
            fi
            ((hour_now+=${inc}))
        done
    else
        echo "FCST_OUTPUT_MISSING: Directory ${com_rrfs_mdl} missing."
    fi
done
#
if [ "${flag_send_message}" == "YES" ]; then
    export subject="AEORNET or AIRNOW or RRFS model output Missing for EVS ${COMPONENT}_${RUN}"
    echo "Job ID: ${jobid}" >> ${email_msg}
    cat ${email_msg} | mail -s "${subject}" ${MAILTO}
fi 

exit

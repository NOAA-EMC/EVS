#!/bin/bash
########################################################################
###  UNIX Script Documentation Block
###                      .
### Script name:         exevs_cam_chem_rrfs_grid2obs_prep.sh
### Script description:  To run grid-to-obs verification on RRFS-SD (CAM chem-component)
### Original Author   :  Ho-Chun Huang
###
###   Change Logs:
###   04/30/2025   Ho-Chun Huang  Update warning message for dcom input obs
###                               and Remove sendmail for missing FCST model output
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
            checkfile=${COMOUTprep}/${OBTTYPE}_All_${INITDATE}_lev15.nc
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
                            cp -v ${cpfile} ${COMOUTprep}
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
            obs_file_count=$(find ${COMOUTprep} -name ${checkfile} | wc -l )
            if [ ${obs_file_count} -eq 0 ]; then
              let ic=0
            elif [ ${obs_file_count} -eq ${total_num_file} ]; then
              ## check corrupted ASCII2NC file
              vldhr=$(printf %2.2d ${endvhr})
              checkfile="${COMOUTprep}/${OBTTYPE}_${HOURLY_OUTPUT_TYPE}_${INITDATE}${vldhr}.nc"
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
        ##
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
                            if [ -e ${cpfile} ]; then cp -v ${cpfile} ${COMOUTprep}; fi
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
##  Extract variables from full RRFS CHEM output to be verified
##    against observation and option to used already recuded
##    RRFS CHEM output (suitable for restrospective run)
########################################################################
#
match_aod_1="AOTK"
match_aod_2="entire atmosphere"
#
match_pm25_1="MASSDEN"
match_pm25_2="8 m above ground"
match_pm25_3="aerosol=Missing"
match_pm25_4="aerosol_size <2.5e-06"
match_pm25_sp="aerosol=Total Aerosol"
#
match_pm10_1="MASSDEN"
match_pm10_2="8 m above ground"
match_pm10_3="aerosol=Missing"
match_pm10_4="aerosol_size <1e-05"
match_pm10_sp="aerosol=Total Aerosol"
#
declare -a cyc_opt=( 00 06 12 18 )
let inc=1
for mdl_cyc in "${cyc_opt[@]}"; do
    com_rrfs=${COMINrrfs}/${MODELNAME}.${INITDATE}/${mdl_cyc}
    if [ -d ${com_rrfs} ]; then
        prep_rrfs=${COMOUTprep}/${mdl_cyc}
        if [ ! -d ${prep_rrfs} ]; then mkdir -p ${prep_rrfs}; fi
        let hour_now=1
        let max_hour=84
        let total_num_file=${max_hour}
  
        if [ "${check_restart}" == "YES" ]; then   ## Check RRFS reduced grib2 files for RESTART ability
            checkfile="${MODELNAME}.t${mdl_cyc}z.prslev.f*.reduced.grib2"
            mdl_file_count=$(find ${prep_rrfs} -name ${checkfile} | wc -l )
            if [ ${mdl_file_count} -eq 0 ]; then
                let hour_now=1
            elif [ ${mdl_file_count} -eq ${total_num_file} ]; then
                ## check corrupted grib2 file
                fhr3=$(printf %3.3d ${max_hour})
                checkfile=${prep_rrfs}/${MODELNAME}.t${mdl_cyc}z.prslev.f${fhr3}.reduced.grib2
                msg=$(wgrib2 -V ${checkfile} 1> /dev/null 2>&1 ; err=$? ; echo ${err} )
                if [ ${msg} -eq 0 ]; then
                    let hour_now=${max_hour}+1   ## skip current RRFS reduced grib2 Processing
                    echo "DEBUG :: RESTART Skip RRFS reduced grib2 Porcessing for cycle ${mdl_cyc}"
                else
                    let hour_now=${max_hour}     ## file corrupted re-do the last hour grib2 process
                    echo "DEBUG :: RESTART RRFS reduced grib2 for cycle ${mdl_cyc} from hour ${hour_now}"
                fi
            else
                let hour_now=${mdl_file_count}
                echo "DEBUG :: RESTART RRFS reduced grib2 for cycle ${mdl_cyc} from hour ${hour_now}"
            fi
        fi
        while [ ${hour_now} -le ${max_hour} ]; do
            fhr3=`printf %3.3d ${hour_now}`
            mdl_full_grib2=${MODELNAME}.t${mdl_cyc}z.prslev.3km.f${fhr3}.na.grib2
            reduced_rec_grib2=${MODELNAME}.t${mdl_cyc}z.prslev.f${fhr3}.reduced.grib2
            check_full_file=${com_rrfs}/${mdl_full_grib2}
            check_reduced_file=${com_rrfs}/${reduced_rec_grib2}
            if [ -s ${check_reduced_file} ]; then
                echo "Found file ${check_reduced_file}"
                if [ ${SENDCOM} = "YES" ]; then
                    cp -v ${check_reduced_file} ${prep_rrfs}
                fi
            elif [ -s ${check_full_file} ]; then
                if [ -e extract_aod ]; then /bin/rm -rf extract_aod; fi
                if [ -e extract_pm25 ]; then /bin/rm -rf extract_pm25; fi
                if [ -e extract_pm10 ]; then /bin/rm -rf extract_pm10; fi
                wgrib2 -match "${match_aod_1}" -match "${match_aod_2}" ${check_full_file} -grib extract_aod
                wgrib2 -match "${match_pm25_1}" -match "${match_pm25_2}" -match "${match_pm25_3}" -match "${match_pm25_4}" ${check_full_file} -grib extract_pm25
		wgrib2 extract_pm25 > extract_pm25_rec
		number_of_record=$(wc -l extract_pm25_rec | awk -F" " '{print $1}')
		if [ "${number_of_record}" == "0" ]; then
                    wgrib2 -match "${match_pm25_1}" -match "${match_pm25_2}" -match "${match_pm25_sp}" -match "${match_pm25_4}" ${check_full_file} -grib extract_pm25
		fi
		wgrib2 extract_pm25 > extract_pm25_rec
		number_of_record=$(wc -l extract_pm25_rec | awk -F" " '{print $1}')
		echo "DEBUG: Number of extracted record is ${number_of_record} for file extract_pm25"
                wgrib2 -match "${match_pm10_1}" -match "${match_pm10_2}" -match "${match_pm10_3}" -match "${match_pm10_4}" ${check_full_file} -grib extract_pm10
		wgrib2 extract_pm10 > extract_pm10_rec
		number_of_record=$(wc -l extract_pm10_rec | awk -F" " '{print $1}')
		if [ "${number_of_record}" == "0" ]; then
                    wgrib2 -match "${match_pm10_1}" -match "${match_pm10_2}" -match "${match_pm10_sp}" -match "${match_pm10_4}" ${check_full_file} -grib extract_pm10
		fi
		wgrib2 extract_pm10 > extract_pm10_rec
		number_of_record=$(wc -l extract_pm10_rec | awk -F" " '{print $1}')
		echo "DEBUG: Number of extracted record is ${number_of_record} for file extract_pm10"
                cat extract_pm25 extract_pm10 extract_aod > ${reduced_rec_grib2}
                if [ ${SENDCOM} = "YES" ]; then
                    cp -v ${reduced_rec_grib2} ${prep_rrfs}
                fi
            else
                echo "FCST_OUTPUT_MISSING: RRFS-smoke and dust forecast file ${check_full_file} is missing. The missing RRFS-smoke and dust forecast file will be skipped"
            fi
            ((hour_now+=${inc}))
        done
    else
        echo "FCST_OUTPUT_MISSING: RRFS-smoke and dust output directory ${com_rrfs} is missing. The missing RRFS-smoke and dust forecast files will be skipped"
    fi
done
#
if [ "${flag_send_message}" == "YES" ]; then
    export subject="AEORNET or AIRNOW or RRFS model output Missing for EVS ${COMPONENT}_${RUN}"
    echo "Job ID: ${jobid}" >> ${email_msg}
    cat ${email_msg} | mail -s "${subject}" ${MAILTO}
fi 

exit

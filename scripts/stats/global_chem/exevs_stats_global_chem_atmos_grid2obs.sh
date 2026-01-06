#!/bin/bash
########################################################################
###  UNIX Script Documentation Block
###                      .
### Script name:         exevs_stats_global_chem_atmos_grid2obs.sh
### Script description:  To run grid-to-grid verification on all global chem
### Original Author   :  Partha Bhattacharjee
###
###   Change Logs:
###
###   01/16/2024   Ho-Chun Huang  consolidate exevs_global_ens_chem_grid2obs scripts
###   04/30/2025   Ho-Chun Huang  Remove email function for missing 
###                               pre-processed forecast output
###   06/04/2025   Ho-Chun Huang  mv from global_ens to global_chem
###   12/05/2025   Ho-Chun Huang  add restart function and non-zero size copying
###   01/06/2026   Ho-Chun Huang  remove init cycle 06Z and 18Z
###
########################################################################
set -x

cd ${DATA}

recorded_temp_list=${DATA}/fcstlist_in_metplus
#
## For temporary stoage on the working dirary before moving to COMOUT
#
export finalstat=${DATA}/final  # config variable
mkdir -p ${finalstat}

export CMODEL=`echo ${MODELNAME} | tr a-z A-Z`  # define config variable
vmodel=`echo ${gefs_ver} | awk -F"." '{print $1}'`
export VMODEL=${CMODEL}

export CONFIGevs=${CONFIGevs:-${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}
export config_common=${PARMevs}/metplus_config/machine.conf

export METPLUS_PATH

grid2obs_list="${DATA_TYPE}"

export init_cyc="00 12"

for ObsType in ${grid2obs_list}; do
    export ObsType
    case ${ObsType} in
        aeronet) export obs_var=aod
                 export VARID=`echo ${obs_var} | tr a-z A-Z`;;  # config variable
        airnow)  export obs_var=pm25
                 if [ "${airnow_hourly_type}" == "aqobs" ]; then
                   export HOURLY_INPUT_TYPE=hourly_aqobs
                 else
                   export HOURLY_INPUT_TYPE=hourly_data
                 fi
                 export VARID=`echo ${HOURLY_INPUT_TYPE} | tr a-z A-Z`;;  # config variable
        *)       echo " ObsType=${ObsType} is not defined, set to default aeronet"
                 export obs_var=aod
                 export VARID=`echo ${obs_var} | tr a-z A-Z`;;  # config variable
    esac

    export RUNTIME_STATS=${DATA}/point_stat/${MODELNAME}_${ObsType}  # config variable
    export OutputId=${MODELNAME}_${ObsType}_${obs_var}            # config variable
    export StatFileId=${NET}.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}_${ObsType}_${obs_var} # config variable
    export OBSTYPE=`echo ${ObsType} | tr a-z A-Z`    # config variable
    point_stat_conf_file="${CONFIGevs}/PointStat_fcst${CMODEL}Aero_obs${OBSTYPE}.conf"
    stat_analysis_conf_file="${CONFIGevs}/Statanalysis_fcst${CMODEL}Aero_obs${OBSTYPE}.conf"

    if [ "${ObsType}" == "aeronet" ]; then
        fcstmax=120
        check_file=${EVSINprep}/${RUN}.${VDATE}/obs/${ObsType}_All_${VDATE}_lev15.nc
        num_obs_found=0
        if [ -s ${check_file} ]; then
          num_obs_found=1
        else
          echo "PREP_OUTPUT_MISSING: Pre-processed ${OBSTYPE} Level 1.5 input ${check_file} is missing. The verification on ${VDATE} will be skipped"
        fi
        echo "DEBUG: index of daily aeronet obs found = ${num_obs_found}"
    elif [ "${ObsType}" == "airnow" ]; then
        fcstmax=120

        cdate=${VDATE}${vhr}
        vld_date=$(${NDATE} -1 ${cdate} | cut -c1-8)
        vld_time=$(${NDATE} -1 ${cdate} | cut -c1-10)

        check_file=${EVSINprep}/${RUN}.${vld_date}/obs/${ObsType}_${HOURLY_INPUT_TYPE}_${vld_time}.nc
        num_obs_found=0
        if [ -s ${check_file} ]; then
          num_obs_found=1
        else
          echo "PREP_OUTPUT_MISSING: Pre-processed ${OBSTYPE} hourly input ${check_file} is missing. The verification at ${vhr}Z will be skipped"
        fi
        echo "DEBUG: index of hourly AirNOW obs found = ${num_obs_found}"
    fi

    for mdl_cyc in ${init_cyc}; do
      export mdl_cyc    ## variable used in *.conf

      restart_status_file="${COMOUTsmall}/completed/run_${MODELNAME}_${ObsType}_init_hr_t${mdl_cyc}z_valid_hr_t${vhr}z_grid2obs.completed"
      if [ -s ${restart_status_file} ]; then
        echo "Found Restart status file - the ${MODELNAME} ${ObsType} init hr=t${mdl_cyc}z valid hr=t${vhr}z will be skipped"
      else
        let ihr=0
        num_fcst_in_metplus=0
        if [ -e ${recorded_temp_list} ]; then rm -f ${recorded_temp_list}; fi
        while [ ${ihr} -le ${fcstmax} ]; do
          filehr=$(printf %3.3d ${ihr})    ## fhr of grib2 filename is in 3 digit
          fhr=$(printf %2.2d ${ihr})       ## fhr for the processing valid hour is in 2 digit
          export fhr
    
          export datehr=${VDATE}${vhr}
          adate=`${NDATE} -${ihr} ${datehr}`
          aday=`echo ${adate} |cut -c1-8`
          acyc=`echo ${adate} |cut -c9-10`
          if [ "${acyc}" == "${mdl_cyc}" ]; then
            fcst_file=${EVSINprep}/${RUN}.${aday}/${MODELNAME}/${acyc}/${RUN}/pgrb2ap25/${MODELNAME}.${RUN}.t${acyc}z.a2d_0p25.f${filehr}.reduced.grib2
            if [ -s ${fcst_file} ]; then
              echo "${fhr} found"
              echo ${fhr} >> ${recorded_temp_list}
              let "num_fcst_in_metplus=num_fcst_in_metplus+1"
            else
              echo "PREP_OUTPUT_MISSING: Pre-processed Global-Chemical output ${fcst_file} is missing. The missing Global-Chemical forecast file will be skipped"
            fi 
          fi 
          let "ihr=ihr+3"
        done
        if [ -s ${recorded_temp_list} ]; then
          export fcsthours_list=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' ${recorded_temp_list}`
        fi
        if [ -e ${recorded_temp_list} ]; then rm -f ${recorded_temp_list}; fi
        export num_fcst_in_metplus
        echo "number of fcst lead in_metplus point_stat for ${CMODEL}-aerosol ${obs_var} == ${num_fcst_in_metplus}"
    
        if [ ${num_fcst_in_metplus} -gt 0 -a ${num_obs_found} -eq 1 ]; then
          export fcsthours=${fcsthours_list}
          #############################
          # run Point Stat Analysis
          #############################
          run_metplus.py ${point_stat_conf_file} ${config_common}
          export err=$?; err_chk
        else
          if [ ${num_obs_found} -eq 0 ]; then
              echo "DEBUG: There is no pre-processed ${OBSTYPE} OBS, the metplus stats process will be skipped"
          fi
          if [ ${num_fcst_in_metplus} -eq 0 ]; then
              echo "DEBUG: There is no pre-processed ${obs_var} ${CMODEL}-aerosol ${mdl_cyc} cycle forecast output validated at ${vhr}Z, the metplus stats process will be skipped"
          fi
        fi
        if [ "${SENDCOM}" == "YES" ]; then
          SOURCE_DIR=${RUNTIME_STATS}/${VDATE}.stat
          if [ -d ${SOURCE_DIR} ]; then      ## does not exist if run_metplus.py did not execute
            stat_file_count=$(
                find "$SOURCE_DIR" -type f -size +0c -name "*${OutputId}*" -printf "1\n" 2>/dev/null | wc -l
            )
            if [ ${stat_file_count} -ne 0 ]; then
              mkdir -p ${COMOUTsmall}
              mkdir -p ${COMOUTsmall}/completed
              find "$SOURCE_DIR" -type f -size +0c -name "*${OutputId}*" -exec cp -v {} "$COMOUTsmall/" \;
              echo "run ${MODELNAME} ${ObsType} init hr=t${mdl_cyc}z valid hr=t${vhr}z grid2obs completed" > ${restart_status_file}
            else
              echo "DEBUG: NO none-zero stats file *${OutputId}* found in ${SOURCE_DIR}"
            fi
          fi
        fi
      fi
    done   ## hour loop
    if [ "${vhr}" == "21" ]; then
      stat_file_count=$(find ${COMOUTsmall} -name "*${OutputId}*" | wc -l)
      if [ ${stat_file_count} -ne 0 ]; then
        cp -v ${COMOUTsmall}/*${OutputId}* ${finalstat}
        cd ${finalstat}
        run_metplus.py ${stat_analysis_conf_file} ${config_common}
        export err=$?; err_chk
        if [ "${SENDCOM}" == "YES" ]; then
          cpfile=${finalstat}/${StatFileId}.v${VDATE}.stat
          if [ -s ${cpfile} ]; then
            mkdir -p ${COMOUTfinal}
            cp -v ${cpfile} ${COMOUTfinal}
          fi
        fi
      fi
    fi

done
exit

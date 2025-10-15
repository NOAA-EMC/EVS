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
###   10/07/2025   Ho-Chun Huang  Revise code for GCAFSv1 naming and data structure
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
vmodel=`echo ${gcafs_ver} | awk -F"." '{print $1}'`
export VMODEL=${CMODEL}

export CONFIGevs=${CONFIGevs:-${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}
export config_common=${PARMevs}/metplus_config/machine.conf

export METPLUS_PATH

grid2obs_list="${DATA_TYPE}"

export init_cyc="00 12"

for ObsType in ${grid2obs_list}; do
    export ObsType
    case ${ObsType} in
        airnow_pm25) if [ "${airnow_hourly_type}" == "aqobs" ]; then
                   export HOURLY_INPUT_TYPE=hourly_aqobs
                 else
                   export HOURLY_INPUT_TYPE=hourly_data
                 fi
        airnow_pm10) if [ "${airnow_hourly_type}" == "aqobs" ]; then
                   export HOURLY_INPUT_TYPE=hourly_aqobs
                 else
                   export HOURLY_INPUT_TYPE=hourly_data
                 fi
        *)       export HOURLY_INPUT_TYPE="hourly_aod";;     # config variable
    esac

    export RUNTIME_STATS=${DATA}/point_stat/${MODELNAME}_${ObsType}  # config variable
    export OutputId=${MODELNAME}_${ObsType}                       # config variable
    export StatFileId=${NET}.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}_${ObsType}            # config variable
    export OBSTYPE=`echo ${ObsType} | tr a-z A-Z`    # config variable
    point_stat_conf_file="${CONFIGevs}/PointStat_fcst${CMODEL}_obs${OBSTYPE}.conf"
    stat_analysis_conf_file="${CONFIGevs}/Statanalysis_fcst${CMODEL}_obs${OBSTYPE}.conf"

    if [ "${ObsType}" == "aeronet_aod" ]; then
        fcstmax=120
        check_file=${EVSINprep}/${RUN}.${VDATE}/obs/aeronet_All_${VDATE}_lev15.nc
        num_obs_found=0
        if [ -s ${check_file} ]; then
          num_obs_found=1
        else
          echo "PREP_OUTPUT_MISSING: Pre-processed ${OBSTYPE} Level 1.5 input ${check_file} is missing. The verification on ${VDATE} will be skipped"
        fi
        echo "DEBUG: index of daily aeronet obs found = ${num_obs_found}"
    elif [ "${ObsType}" == "airnow_pm25" ] || [ "${ObsType}" == "airnow_pm10" ]; then
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
          fcst_file=${EVSINprep}/${RUN}.${aday}/${MODELNAME}/${acyc}/products/${RUN}/grib2/0p25/${MODELNAME}.${RUN}.t${acyc}z.0p25.f${filehr}.trim.grib2
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
      echo "number of fcst lead in_metplus point_stat for ${CMODEL} ${ObsType} == ${num_fcst_in_metplus}"
    
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
            echo "DEBUG: There is no pre-processed ${ObsType} ${CMODEL} ${mdl_cyc} cycle forecast output validated at ${vhr}Z, the metplus stats process will be skipped"
        fi
      fi
    done   ## hour loop
    if [ "${SENDCOM}" == "YES" ]; then
      if [ -d ${RUNTIME_STATS}/${VDATE}.stat ]; then      ## does not exist if run_metplus.py did not execute
        stat_file_count=$(find ${RUNTIME_STATS}/${VDATE}.stat -name "*${OutputId}*" | wc -l)
        if [ ${stat_file_count} -ne 0 ]; then
          mkdir -p ${COMOUTsmall}
          cp -v ${RUNTIME_STATS}/${VDATE}.stat/*${OutputId}* ${COMOUTsmall}
        fi
      fi
    fi
    if [ "${vhr}" == "21" ]; then
      stat_file_count=$(find ${COMOUTsmall} -name "*${OutputId}*" | wc -l)
      if [ ${stat_file_count} -ne 0 ]; then
        cp -v ${COMOUTsmall}/*${OutputId}* ${finalstat}
        cd ${finalstat}
        run_metplus.py ${stat_analysis_conf_file} ${config_common}
        export err=$?; err_chk
        if [ ${SENDCOM} = "YES" ]; then
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

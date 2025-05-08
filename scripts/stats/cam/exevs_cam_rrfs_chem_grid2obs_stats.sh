#!/bin/bash
########################################################################
###  UNIX Script Documentation Block
###                      .
### Script name:         exevs_cam_chem_rrfs_grid2obs_stats.sh
### Script description:  To run grid-to-grid verification on RRFS chem
###
###   Change Logs:
###
###   04/30/2025   Ho-Chun Huang  Remove email function for missing 
###                               Prep-Obs input and Fcst Mdl output
###                                 
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
vmodel=$( echo ${rrfs_ver} | awk -F"." '{print $1}' )
export VMODEL=${CMODEL}

export CONFIGevs=${CONFIGevs:-${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}
export config_common=${PARMevs}/metplus_config/machine.conf

export gridspec_conus=240
export gridspec=218

export METPLUS_PATH

grid2obs_list="${DATA_TYPE}"

export init_cyc="00 06 12 18"
let inc=1

check_restart=$( echo ${restart_mode} | tr a-z A-Z )

for ObsType in ${grid2obs_list}; do
    export ObsType
    export ObsSrc=$( echo ${ObsType} | awk -F"_" '{print $1}' )  # config variable
    export ObsVar=$( echo ${ObsType} | awk -F"_" '{print $2}' )
    export OBSTYPE=$( echo ${ObsType} | tr a-z A-Z )             # config variable
    case ${ObsType} in
        aeronet_aod) export OBS_STANLYS_TYPE="AERONET_AOD";;     # config variable
        airnow_pm25) if [ "${airnow_hourly_type}" == "aqobs" ]; then
                   export HOURLY_INPUT_TYPE="hourly_aqobs"       # config variable
                   export OBS_STANLYS_TYPE="AIRNOW_HOURLY_AQOBS" # config variable
                 else
                   export HOURLY_INPUT_TYPE="hourly_data"          # config variable
                   export OBS_STANLYS_TYPE="AIRNOW_HOURLY_AQDATA"  # config variable
                 fi;;
        airnow_pm10) if [ "${airnow_hourly_type}" == "aqobs" ]; then
                   export HOURLY_INPUT_TYPE="hourly_aqobs"        # config variable
                   export OBS_STANLYS_TYPE="AIRNOW_HOURLY_AQOBS"  # config variable
                 else
                   export HOURLY_INPUT_TYPE="hourly_data"          # config variable
                   export OBS_STANLYS_TYPE="AIRNOW_HOURLY_AQDATA"  # config variable
                 fi;;
        *)       echo "ObsType=${ObsType} is not defined, set to default aeronet"
                 export ObsType="aeronet_aod"
                 export ObsSrc=$( echo ${ObsType} | awk -F"_" '{print $1}' )  # config variable
                 export ObsVar=$( echo ${ObsType} | awk -F"_" '{print $2}' )
		 export OBSTYPE=$( echo ${ObsType} | tr a-z A-Z )
                 export OBS_STANLYS_TYPE="AERONET_AOD";;              # config variable
    esac

    export RUNTIME_STATS=${DATA}/point_stat/${MODELNAME}_${ObsType}               # config variable
    export OutputId=${MODELNAME}_${ObsType}                                       # config variable
    export StatFileId=${NET}.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}_${ObsType} # config variable
    point_stat_conf_file=${CONFIGevs}/PointStat_fcstRRFSAero_obs${OBSTYPE}.conf
    stat_analysis_conf_file=${CONFIGevs}/Statanalysis_fcstRRFSAero_obs${OBSTYPE}.conf

    if [ "${ObsSrc}" == "aeronet" ]; then
        check_file=${EVSINrrfs}/${RUN}.${VDATE}/${MODELNAME}/${ObsSrc}_All_${VDATE}_lev15.nc
        num_obs_found=0
        if [ -s ${check_file} ]; then
          num_obs_found=1
        else
          echo "PREP_OUTPUT_MISSING: Pre-processed ${ObsSrc} Level 1.5 input ${check_file} is missing. The verification on ${VDATE} will be skipped"
        fi
        echo "DEBUG: index of daily aeronet obs found = ${num_obs_found}"
    elif [ "${ObsSrc}" == "airnow" ]; then
        cdate=${VDATE}${vhr}
        vld_date=$(${NDATE} -1 ${cdate} | cut -c1-8)
        vld_time=$(${NDATE} -1 ${cdate} | cut -c1-10)

        check_file=${EVSINrrfs}/${RUN}.${vld_date}/${MODELNAME}/${ObsSrc}_${HOURLY_INPUT_TYPE}_${vld_time}.nc
        num_obs_found=0
        if [ -s ${check_file} ]; then
          num_obs_found=1
        else
          echo "PREP_OUTPUT_MISSING: Pre-processed ${ObsSrc} hourly input ${check_file} is missing. The verification at ${vhr}Z will be skipped"
        fi
        echo "DEBUG: index of hourly ${OBSTYPE} obs found = ${num_obs_found}"
    fi

    fcstmax=84
    for mdl_cyc in ${init_cyc}; do
      export mdl_cyc    ## variable used in *.conf

      let ihr=1
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
          fcst_file=${EVSINrrfs}/${RUN}.${aday}/${MODELNAME}/${acyc}/${MODELNAME}.t${acyc}z.prslev.f${filehr}.reduced.grib2
          if [ -s ${fcst_file} ]; then
            if [ "${check_restart}" == "YES" ]; then
              point_stat_file="${COMOUTsmall}/point_stat_${OutputId}_${fhr}0000L_${VDATE}_${vhr}0000V.stat"
              if [ -s ${point_stat_file} ]; then
                echo "DEBUG: Restart Mode; Found stats file, skip fcst hour ${fhr} processing"
              else
                echo ${fhr} >> ${recorded_temp_list}
                let "num_fcst_in_metplus=num_fcst_in_metplus+1"
	      fi
            else
              echo ${fhr} >> ${recorded_temp_list}
              let "num_fcst_in_metplus=num_fcst_in_metplus+1"
            fi
          else
            echo "PREP_OUTPUT_MISSING: Pre-processed RRFS-smoke and dust output ${fcst_file} is missing. The missing GEFS-aerosol forecast file will be skipped"
          fi 
        fi 
        ((ihr+=${inc}))
      done   ## fcst hour loop

      if [ -s ${recorded_temp_list} ]; then
        export fcsthours_list=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' ${recorded_temp_list}`
      fi
      if [ -e ${recorded_temp_list} ]; then rm -f ${recorded_temp_list}; fi
      export num_fcst_in_metplus
      echo "DEBUG: number of fcst lead in_metplus point_stat for ${CMODEL} ${ObsType} == ${num_fcst_in_metplus}"
    
      if [ ${num_fcst_in_metplus} -gt 0 -a ${num_obs_found} -eq 1 ]; then     ##  run Point Stat Analysis
        export fcsthours=${fcsthours_list}
        run_metplus.py ${point_stat_conf_file} ${config_common}
        export err=$?; err_chk
      else
        if [ ${num_obs_found} -eq 0 ]; then
            echo "DEBUG: There is no pre-processed ${ObsSrc} OBS, the metplus stats process will be skipped"
        fi
        if [ ${num_fcst_in_metplus} -eq 0 ]; then
            echo "DEBUG: There is no pre-processed ${ObsVar} ${CMODEL}-smoke and dust ${mdl_cyc} cycle forecast output validated at ${vhr}Z, the metplus stats process will be skipped"
        fi
      fi
      if [ "${SENDCOM}" == "YES" ]; then
        if [ -d ${RUNTIME_STATS}/${VDATE}.stat ]; then      ## does not exist if run_metplus.py did not execute
          stat_file_count=$(find ${RUNTIME_STATS}/${VDATE}.stat -name "*${OutputId}*" | wc -l)
          if [ ${stat_file_count} -ne 0 ]; then
            mkdir -p ${COMOUTsmall}
            cp -v ${RUNTIME_STATS}/${VDATE}.stat/*${OutputId}* ${COMOUTsmall}
          else
            echo "DEBUG: NO stats file *${OutputId}* found in ${RUNTIME_STATS}/${VDATE}.stat"
          fi
        fi
      fi
    done   ## init hour loop
    if [ "${vhr}" == "23" ]; then
      stat_file_count=$(find ${COMOUTsmall} -name "*${OutputId}*" | wc -l)
      if [ ${stat_file_count} -ne 0 ]; then
        cpreq ${COMOUTsmall}/*${OutputId}* ${finalstat}
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
done    ## loop over ObsType

exit

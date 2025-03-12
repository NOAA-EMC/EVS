#!/bin/bash
#######################################################################
##  UNIX Script Documentation Block
##                      .
## Script name:         exevs_aqm_grid2grid_stats.sh
## Script description:  Perform MetPlus GridStat of Air Quality Model.
##
##   Change Logs:
##
##   04/30/2024   Ho-Chun Huang  modification for using GOES-16 AOD
##
##   Note :  The lead hours specification is important to avoid the error generated 
##           by the MetPlus for not finding the input FCST or OBS files. The error
##           will lead to job crash by err_chk.
##
#######################################################################
#
set -x

export config=$PARMevs/evs_config/$COMPONENT/config.evs.aqm.prod
source $config

mkdir -p ${DATA}/logs
mkdir -p ${DATA}/stat
export finalstat=${DATA}/final_${VDATE}${vhr}
mkdir -p ${finalstat}

export conf_file_dir=${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}
#######################################################################
# Define INPUT OBS DATA TYPE for GridStat
#######################################################################
#
export dirname=aqm
export gridspec=793
export fcstmax=72
#
## export MASK_DIR is declared in the ~/EVS/jobs/JEVS_AQM_STATS 
#
export CMODEL=$(echo ${MODELNAME} | tr a-z A-Z)
echo ${CMODEL}

export CONFIGevs=${CONFIGevs:-${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}}
export config_common=${PARMevs}/metplus_config/machine.conf

if [ "${AOD_QC_NAME}" != "high" ] && [ "${AOD_QC_NAME}" != "medium" ]; then
    export AOD_QC_NAME="high"    # config variable, use default for QC not expected.
fi

declare -a grid2grid_list=( ${DATA_TYPE} )
num_obs=${#grid2grid_list[@]}

declare -a satellite_list=( join )
num_sat=${#satellite_list[@]}

declare -a goes_scan_list=( ${AOD_SCAN_TYPE} )
num_scan=${#goes_scan_list[@]}

export vld_cyc="06 12"

flag_send_message=NO
if [ -e mailmsg ]; then /bin/rm -f mailmsg; fi

for ObsType in "${grid2grid_list[@]}"; do
  export ObsType
  export OBSTYPE=`echo ${ObsType} | tr a-z A-Z`    # config variable

  case ${ObsType} in
       abi) export obs_var=aod;;
       viirs)  export obs_var=aod;;
       *)  export obs_var=aod;;
  esac

  export VarId=${obs_var}
  export VARID=$(echo ${VarId} | tr a-z A-Z)    # config variable

  for SatId in "${satellite_list[@]}"; do
    export SatId
    export SATID=$(echo ${SatId} | tr a-z A-Z)    # config variable

    for AOD_SCAN in "${goes_scan_list[@]}"; do
      export AOD_SCAN
      export Aod_Scan=$(echo ${AOD_SCAN} | tr A-Z a-z)    # config variable

      case ${VarId} in
           aod) grid_stat_conf_file=GridStat_fcst${VARID}_obs${OBSTYPE}.conf
                stat_analysis_conf_file=StatAnalysis_fcst${VARID}_obs${OBSTYPE}_GatherByDay.conf
                export FileinId=cmaq
                stat_output_index=aod;;
           *)   grid_stat_conf_file=GridStat_fcst${VARID}_obs${OBSTYPE}.conf
                stat_analysis_conf_file=StatAnalysis_fcst${VARID}_obs${OBSTYPE}_GatherByDay.conf
                export FileinId=cmaq
                stat_output_index=aod;;
      esac

      export RUNTIME_STATS=${DATA}/grid_stat/${ObsType}_${SatId}_${Aod_Scan}_${AOD_QC_NAME}_${VDATE}${vhr}  # config variable
      mkdir -p ${RUNTIME_STATS}
      recorded_temp_list=${RUNTIME_STATS}/fcstlist_in_metplus


      check_file=${EVSINaqm}/${RUN}.${VDATE}/${MODELNAME}/${ObsType}_${AOD_SCAN}_${MODELNAME}_${SatId}_${VDATE}_${vhr}_${AOD_QC_NAME}.nc
      obs_hourly_found=0
      if [ -s ${check_file} ]; then
        obs_hourly_found=1
      else
        echo "WARNING: Can not find pre-processed obs hourly input ${check_file}"
        if [ $SENDMAIL = "YES" ]; then 
          export subject="AQM Hourly Observed Missing for EVS ${COMPONENT}"
          echo "WARNING: No ${SatID} ${ObsType} ${VarId} was available for ${vld_date} ${vld_time}" > mailmsg
          echo "Missing file is ${check_file}" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
        fi
      fi
      echo "index of hourly obs found = ${obs_hourly_found}"

      # Verification to be done both on raw output files and bias-corrected files
    
      for biastyp in raw; do
        export biastyp
    
        if [ "${biastyp}" == "raw" ]; then
          export bctag=
        elif [ "${biastyp}" == "bc" ]; then
          export bctag="_${biastyp}"
        fi
        export bcout="_${biastyp}"
        export OutputId=${MODELNAME}_${biastyp}_${SatId}${Aod_Scan}            # config variable
        export StatFileId=${NET}.${STEP}.${MODELNAME}_${biastyp}.${RUN}.${VERIF_CASE}_${ObsType}_${SatId}${Aod_Scan} # config variable
    
        # check to see that model files exist, and list which forecast hours are to be used
        #
        # AQMv7 does not output IC, i.e., f000.  Thus the forecast file will be chekced from f001 to f072
        #
        for hour in ${vld_cyc}; do
          export hour
          export mdl_cyc=${hour}    ## is needed for *.conf

          let ihr=1
          num_fcst_in_metplus=0
          if [ -e ${recorded_temp_list} ]; then rm -f ${recorded_temp_list}; fi
          while [ ${ihr} -le ${fcstmax} ]; do
            filehr=$(printf %3.3d ${ihr})    ## fhr of grib2 filename is in 3 digit for aqmv7
            fhr=$(printf %2.2d ${ihr})       ## fhr for the processing valid hour is in 2 digit
            export fhr
    
            export datehr=${VDATE}${vhr}
            adate=`${NDATE} -${ihr} ${datehr}`
            aday=`echo ${adate} |cut -c1-8`
            acyc=`echo ${adate} |cut -c9-10`
            if [ ${acyc} = ${hour} ]; then
              fcst_file=${COMINaqm}/${dirname}.${aday}/${acyc}/aqm.t${acyc}z.${FileinId}${bctag}.f${filehr}.${gridspec}.grib2
              if [ -s ${fcst_file} ]; then
                echo "${fhr} found"
                echo ${fhr} >> ${recorded_temp_list}
                let "num_fcst_in_metplus=num_fcst_in_metplus+1"
              else
                if [ $SENDMAIL = "YES" ]; then
                  export subject="t${acyc}z ${FileinId}${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
                  echo "WARNING: No AQM ${FileinId}${bctag} forecast was available for ${aday} t${acyc}z" > mailmsg
                  echo "Missing file is ${fcst_file}" >> mailmsg
                  echo "Job ID: $jobid" >> mailmsg
                  cat mailmsg | mail -s "$subject" $MAILTO
                fi

                echo "WARNING: No AQM${bctag} ${SatId}${VarId} forecast was available for ${aday} t${acyc}z"
                echo "WARNING: Missing file is ${fcst_file}"
              fi 
            fi 
            ((ihr++))
          done
          if [ -s ${recorded_temp_list} ]; then
            export fcsthours_list=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' ${recorded_temp_list}`
          fi
          if [ -e ${recorded_temp_list} ]; then rm -f ${recorded_temp_list}; fi
          export num_fcst_in_metplus
          echo "number of fcst lead in_metplus grid_stat for ${VarId}${bctag} == ${num_fcst_in_metplus}"
    
          if [ ${num_fcst_in_metplus} -gt 0 -a ${obs_hourly_found} -eq 1 ]; then
            export fcsthours=${fcsthours_list}
            run_metplus.py ${conf_file_dir}/${grid_stat_conf_file} ${config_common}
            export err=$?; err_chk
          else
            echo "WARNING: NO ${VARID} FORECAST OR OBS TO VERIFY"
            echo "WARNING: NUM FCST=${num_fcst_in_metplus}, INDEX OBS=${obs_hourly_found}"
          fi
        done   ## hour loop
        mkdir -p ${COMOUTsmall}
        if [ ${SENDCOM} = "YES" ]; then
          cpdir=${RUNTIME_STATS}/${MODELNAME}
          if [ -d ${cpdir} ]; then      ## does not exist if run_metplus.py did not execute
            stat_file_count=$(find ${cpdir} -name "*${OutputId}*.stat" | wc -l)
            if [ ${stat_file_count} -ne 0 ]; then
              mkdir -p ${COMOUTsmall}
              cp -v ${cpdir}/*${OutputId}*.stat ${COMOUTsmall}
            fi
          fi
        fi
        if [ "${vhr}" == "23" ]; then
          mkdir -p ${COMOUTfinal}
          stat_file_count=$(find ${COMOUTsmall} -name "*${OutputId}*.stat" | wc -l)
          if [ ${stat_file_count} -ne 0 ]; then
            cpreq ${COMOUTsmall}/*${OutputId}*.stat ${finalstat}
            cd ${finalstat}
            run_metplus.py ${conf_file_dir}/${stat_analysis_conf_file} ${config_common}
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
      done  ## biastyp loop
    done  ## AOD_SCAN loop
  done  ## SatId loop
done  ## ObsType loop

exit

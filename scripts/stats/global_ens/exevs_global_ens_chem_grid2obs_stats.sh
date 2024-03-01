#!/bin/bash
########################################################################
###  UNIX Script Documentation Block
###                      .
### Script name:         exevs_global_ens_chem_grid2obs_stats.sh
### Script description:  To run grid-to-grid verification on all global chem
### Original Author   :  Partha Bhattacharjee
###
###   Change Logs:
###
###   01/16/2024   Ho-Chun Huang  consolidate exevs_global_ens_chem_grid2obs scripts
###
########################################################################
set -x

cd ${DATA}
#
## For temporary stoage on the working dirary before moving to COMOUT
#
export finalstat=${DATA}/final  # define config variable
mkdir -p ${finalstat}

export CMODEL=`echo ${MODELNAME} | tr a-z A-Z`  # define config variable

export CONFIGevs=${CONFIGevs:-${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}
export config_common=${PARMevs}/metplus_config/machine.conf

export METPLUS_PATH

grid2obs_list="aeronet airnow"

export vld_cyc="00"

flag_send_message=NO
if [ -e mailmsg ]; then /bin/rm -f mailmsg; fi

for ObsType in ${grid2obs_list}; do
    export MdlObsStat=${DATA}/point_stat/${MODELNAME}_${ObsType}  # define config variable
    export OutputId=${MODELNAME}_${ObsType}_${obs_var}            # define config variable
    export StatFileId=${NET}.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}_${ObsType}_${obs_var}
    export OBSTYPE=`echo ${ObsType} | tr a-z A-Z`
    point_stat_conf_file=${CONFIGevs}/PointStat_fcstGEFSAero_obs${OBSTYPE}.conf
    stat_analysis_conf_file=${CONFIGevs}/Statanalysis_fcstGEFSAero_obs${OBSTYPE}.conf

##    case ${ObsType} in
##        aeronet) export obs_var=aod;;
##        airnow)  export obs_var=pm25;;
##    esac

    if [ "${ObsType}" == "aeronet" ]; then
        fcstmax=24
        obs_var=aod
        check_file=${EVSINgefs}/${RUN}.${VDATE}/${MODELNAME}/${ObsType}_All_${VDATE}_lev15.nc
        num_obs_found=0
        if [ -s ${check_file} ]; then
          num_obs_found=1
        else
          echo "WARNING: Can not find pre-processed ${OBSTYPE} Level 1.5 input ${check_file}"
          if [ "${SENDMAIL}" == "YES" ]; then 
            echo "WARNING: No pre-processed ${OBSTYPE} Level 1.5 was available for ${VDATE} " >> mailmsg
            echo "Missing file is ${check_file}" >> mailmsg
            echo "==============" >> mailmsg
            flag_send_message=YES
          fi
        fi
        echo "index of daily aeronet obs found = ${num_obs_found}"
    elif [ "${ObsType}" == "airnow" ]; then
        fcstmax=24
        obs_var=pm25

        cdate=${VDATE}${vhr}
        vld_date=$(${NDATE} -1 ${cdate} | cut -c1-8)
        vld_time=$(${NDATE} -1 ${cdate} | cut -c1-10)

        check_file=${EVSINaqm}/${RUN}.${vld_date}/${MODELNAME}/${ObsType}_${HOURLY_INPUT_TYPE}_${vld_time}.nc
        num_obs_found=0
        if [ -s ${check_file} ]; then
          num_obs_found=1
        else
          echo "WARNING: Can not find pre-processed ${OBSTYPE} hourly input ${check_file}"
          if [ "${SENDMAIL}" == "YES" ]; then 
            echo "WARNING: No ${OBSTYPE} ${HOURLY_INPUT_TYPE} was available for ${vld_date} ${vld_time}" >> mailmsg
            echo "Missing file is ${check_file}" >> mailmsg
            echo "==============" >> mailmsg
            flag_send_message=YES
          fi
        fi
        echo "index of hourly AirNOW obs found = ${num_obs_found}"
    fi

    #LEAD_SEQ = 0, 3, 6, 9, 12, 15, 18, 21
    for hour in ${vld_cyc}; do
      export mdl_cyc=${hour}    ## is needed for *.conf

      let ihr=3
      num_fcst_in_metplus=0
      recorded_temp_list=${DATA}/fcstlist_in_metplus
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
          fcst_file=${COMINgefs}/${MODELNAME}.${aday}/${acyc}/${RUN}/pgrb2ap25/${MODELNAME}.${RUN}.t${acyc}z.a2d_0p25.f${filehr}.grib2
          if [ -s ${fcst_file} ]; then
            echo "${fhr} found"
            echo ${fhr} >> ${recorded_temp_list}
            let "num_fcst_in_metplus=num_fcst_in_metplus+1"
          else
            if [ $SENDMAIL = "YES" ]; then
              echo "WARNING: No ${model1} ${obs_var} forecast was available for ${aday} t${acyc}z" > mailmsg
              echo "Missing file is ${fcst_file}" >> mailmsg
              echo "==============" >> mailmsg
            fi

            echo "WARNING: No ${model1} ${obs_var} forecast was available for ${aday} t${acyc}z"
            echo "WARNING: Missing file is ${fcst_file}"
          fi 
        fi 
        ## ((ihr++))
        let "ihr=ihr+3"
      done
      if [ -s ${recorded_temp_list} ]; then
        export fcsthours_list=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' ${recorded_temp_list}`
      fi
      if [ -e ${recorded_temp_list} ]; then rm -f ${recorded_temp_list}; fi
      export num_fcst_in_metplus
      echo "number of fcst lead in_metplus point_stat for ${model1} ${obs_var} == ${num_fcst_in_metplus}"
    
      if [ ${num_fcst_in_metplus} -gt 0 -a ${num_obs_found} -eq 1 ]; then
        export fcsthours=${fcsthours_list}
        #############################
        # run Point Stat Analysis
        #############################
        run_metplus.py ${point_stat_conf_file} ${config_common}
        export err=$?; err_chk
      else
        echo "WARNING: NO ${model1} ${obs_var} FORECAST OR OBS TO VERIFY"
        echo "WARNING: NUM FCST=${num_fcst_in_metplus}, INDEX OBS=${num_obs_found}"
      fi
    done   ## hour loop
    mkdir -p ${COMOUTsmall}
    if [ ${SENDCOM} = "YES" ]; then
      if [ -d ${MdlObsStat} ]; then      ## does not exist if run_metplus.py did not execute
        stat_file_count=$(find ${MdlObsStat} -name "*${OutputId}*" | wc -l)
        if [ ${stat_file_count} -ne 0 ]; then
          cp -v ${MdlObsStat}/*${OutputId}* ${COMOUTsmall}
       	fi
      fi
    fi
    if [ "${vhr}" == "21" ]; then
      mkdir -p ${COMOUTfinal}
      stat_file_count=$(find ${COMOUTsmall} -name "*${OutputId}*" | wc -l)
      if [ ${stat_file_count} -ne 0 ]; then
        cpreq ${COMOUTsmall}/*${OutputId}* ${finalstat}
        cd ${finalstat}
        run_metplus.py ${stat_analysis_conf_file} ${config_common}
        export err=$?; err_chk
        if [ ${SENDCOM} = "YES" ]; then
          cpfile=${finalstat}/${StatFileId}.v${VDATE}.stat
          if [ -s ${cpfile} ]; then cp -v ${cpfile} ${COMOUTfinal}; fi
        fi
      fi
    fi

done
if [ "${flag_send_message}" == "YES" ]; then
    export subject="${OBSTYPE} Obs or ${CMODLE} Fcst files Missing for EVS ${COMPONENT} ${RUN} ${VERIF_CASE}"
    echo "Job ID: ${jobid}" >> mailmsg
    cat mailmsg | mail -s "${subject}" ${MAILTO}
fi 
exit
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

## For temporary stoage on the working dirary before moving to COMOUT
export finalstat=${DATA}/final
mkdir -p ${finalstat}

export model1=`echo ${MODELNAME} | tr a-z A-Z`

export CONFIGevs=${CONFIGevs:-${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}
export config_common=${PARMevs}/metplus_config/machine.conf

export METPLUS_PATH

grid2obs_list="aeronet airnow"

export vld_cyc="00"

flag_send_message=NO
if [ -e mailmsg ]; then /bin/rm -f mailmsg; fi

for OBTTYPE in ${grid2obs_list}; do
    export ${OBTTYPE}
    export obstype=`echo ${OBTTYPE} | tr a-z A-Z`
    point_stat_conf_file=${CONFIGevs}/PointStat_fcstGEFSAero_obs${obstype}.conf;;

##    case ${OBTTYPE} in
##        aeronet) export outtype=aod;;
##        airnow)  export outtype=pm25;;
##    esac

    if [ "${OBTTYPE}" == "aeronet" ]; then
        fcstmax=24
        outtype=aod
        check_file=${EVSINgefs}/${RUN}.${VDATE}/${MODELNAME}/aeronet_All_${VDATE}_lev15.nc
        num_obs_found=0
        if [ -s ${check_file} ]; then
          num_obs_found=1
        else
          echo "WARNING: Can not find pre-processed AEORNET Level 1.5 input ${check_file}"
          if [ "${SENDMAIL}" == "YES" ]; then 
            echo "WARNING: No pre-processed AEORNET Level 1.5 was available for ${VDATE} " >> mailmsg
            echo "Missing file is ${check_file}" >> mailmsg
            echo "==============" >> mailmsg
            flag_send_message=YES
          fi
        fi
        echo "index of daily aeronet obs found = ${num_obs_found}"
    elif [ "${OBTTYPE}" == "airnow" ]; then
        fcstmax=24
        outtype=pm25

        cdate=${VDATE}${vhr}
        vld_date=$(${NDATE} -1 ${cdate} | cut -c1-8)
        vld_time=$(${NDATE} -1 ${cdate} | cut -c1-10)

        check_file=${EVSINaqm}/${RUN}.${vld_date}/${MODELNAME}/airnow_${HOURLY_INPUT_TYPE}_${vld_time}.nc
        num_obs_found=0
        if [ -s ${check_file} ]; then
          num_obs_found=1
        else
          echo "WARNING: Can not find pre-processed obs hourly input ${check_file}"
          if [ "${SENDMAIL}" == "YES" ]; then 
            echo "WARNING: No AQM ${HOURLY_INPUT_TYPE} was available for ${vld_date} ${vld_time}" >> mailmsg
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
              echo "WARNING: No ${model1} ${outtype} forecast was available for ${aday} t${acyc}z" > mailmsg
              echo "Missing file is ${fcst_file}" >> mailmsg
              echo "==============" >> mailmsg
            fi

            echo "WARNING: No ${model1} ${outtype} forecast was available for ${aday} t${acyc}z"
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
      echo "number of fcst lead in_metplus point_stat for ${model1} ${outtype} == ${num_fcst_in_metplus}"
    
      if [ ${num_fcst_in_metplus} -gt 0 -a ${num_obs_found} -eq 1 ]; then
        export fcsthours=${fcsthours_list}
        #############################
        # run Point Stat Analysis
        #############################
        run_metplus.py ${point_stat_conf_file} ${config_common}
        export err=$?; err_chk
      else
        echo "WARNING: NO ${model1} ${outtype} FORECAST OR OBS TO VERIFY"
        echo "WARNING: NUM FCST=${num_fcst_in_metplus}, INDEX OBS=${num_obs_found}"
      fi
    done   ## hour loop
    mkdir -p ${COMOUTsmall}
    if [ ${SENDCOM} = "YES" ]; then
      cpdir=${DATA}/point_stat/${MODELNAME}
      if [ -d ${cpdir} ]; then      ## does not exist if run_metplus.py did not execute
        stat_file_count=$(find ${cpdir} -name "*${MODELNAME}_${OBTTYPE}_${outtype}*" | wc -l)
        if [ ${stat_file_count} -ne 0 ]; then cp -v ${cpdir}/*${MODELNAME}_${OBTTYPE}_${outtype}* ${COMOUTsmall}; fi
      fi
    fi
    if [ "${vhr}" == "21" ]; then
      mkdir -p ${COMOUTfinal}
      stat_file_count=$(find ${COMOUTsmall} -name "*${MODELNAME}_${OBTTYPE}_${outtype}*" | wc -l)
      if [ ${stat_file_count} -ne 0 ]; then
        cpreq ${COMOUTsmall}/*${outtyp}${outtype}* ${finalstat}
        cd ${finalstat}
        run_metplus.py ${conf_file_dir}/${stat_analysis_conf_file} ${PARMevs}/metplus_config/machine.conf
        export err=$?; err_chk
        if [ ${SENDCOM} = "YES" ]; then
          cpfile=${finalstat}/evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}_${OBTTYPE}_${outtype}.v${VDATE}.stat
          if [ -s ${cpfile} ]; then cp -v ${cpfile} ${COMOUTfinal}; fi
        fi
      fi
    fi

done
if [ "${flag_send_message}" == "YES" ]; then
    export subject="pre-process AERONET or Hourly Observed AirNOW Missing for EVS ${COMPONENT}"
    echo "Job ID: ${jobid}" >> mailmsg
    cat mailmsg | mail -s "${subject}" ${MAILTO}
fi 
exit

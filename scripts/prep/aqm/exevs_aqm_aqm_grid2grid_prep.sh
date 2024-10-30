#!/bin/bash
#######################################################################
##  UNIX Script Documentation Block
##                      .
## Script name:         exevs_aqm_aqm_grid2grid_prep.sh
## Script description:  Pre-processed input data for the MetPlus GridStat 
##                      of Air Quality Model.
## Original Author   :  Ho-Chun Huang
##
##   Change Logs:
##
##   02/21/2024   Ho-Chun Huang  modify for AQMv7 verification
##   09/30/2024   Ho-Chun Huang  modify for GOES-EAST/WEST and SCAN-MODE
##                               gridded AOD (L3)
##   10/20/2024   Ho-Chun Huang  modify for combined GOES-EAST/WEST L3 AOD
##   10/31/2024   Ho-Chun Huang  Add Restart ability
##
##
#######################################################################
#
set -x

cd ${DATA}

export config=${PARMevs}/evs_config/${COMPONENT}/config.evs.aqm.prod
source ${config}

flag_send_message=NO
if [ -e mailmsg ]; then /bin/rm -f mailmsg; fi

#######################################################################
# Define INPUT OBS DATA TYPE for ASCII2NC 
#######################################################################
export OBSTYPE=$(echo ${DATA_TYPE} | tr a-z A-Z)    # config variable

#
conf_dir=${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}
config_file=Point2Grid_hourly_obs${OBSTYPE}.conf
config_common=${PARMevs}/metplus_config/machine.conf
 
export dirname=aqm
export gridspec=793

export CMODEL=$(echo ${MODELNAME} | tr a-z A-Z)
echo ${CMODEL}

export jday=$(date2jday.sh ${VDATE})        # need module load prod_util

declare -a grid2grid_list=( ${DATA_TYPE} )
num_obs=${#grid2grid_list[@]}

declare -a satellite_list=( ${GOES_EAST} ${GOES_WEST} )
num_sat=${#satellite_list[@]}
if [ "${num_sat}"  != "2" ]; then
    echo "WARNING :: number of satellites ${num_sat} is not 2, expected elements is sat id for GOES-EAST and GOES-West"
    exit
fi

declare -a goes_scan_list=( ${AOD_SCAN_TYPE} )
num_scan=${#goes_scan_list[@]}

export output_var="aod"
export VARID=$(echo ${output_var} | tr a-z A-Z)    # config variable

# AOD quality flag 0:high 1:medium 3:low 0,1: high+medium,...etc
if [ "${AOD_QC_NAME}" == "high" ]; then       # high quality AOD only
    export AOD_QC_FLAG="0"                    # config variable
elif [ "${AOD_QC_NAME}" == "medium" ]; then   # high+medium quality AOD
    export AOD_QC_FLAG="0,1"                  # config variable
else
    echo "AOD quality usage = ${AOD_QC_NAME} is not defined, use high as default"
    export AOD_QC_NAME="high"                 # config variable
    export AOD_QC_FLAG="0"                    # config variable
fi

num_mdl_grid=0
declare -a cyc_opt=( 06 12 )
for mdl_cyc in "${cyc_opt[@]}"; do
    let ic=1
    let endvhr=72
    while [ ${ic} -le ${endvhr} ]; do
        filehr=$(printf %3.3d ${ic})
        checkfile=${COMINaqm}/${dirname}.${VDATE}/${mdl_cyc}/${MODELNAME}.t${mdl_cyc}z.cmaq.f${filehr}.${gridspec}.grib2
        if [ -s ${checkfile} ]; then
            export filein_mdl_grid=${checkfile}    # config variable
            num_mdl_grid=1
            break
        fi
        ((ic++))
    done
    if [ "${num_mdl_grid}" == "1" ]; then break; fi
done
#
## Pre-Processed GOES ABI high qualtiy AOD for GridStat for individual
## SatId (GOES-East and GOES-West)
#
if [ "${num_mdl_grid}" != "0" ]; then
  let nobs=0
  for ObsType in "${grid2grid_list[@]}"; do
    export ObsType
    export OBSTYPE=`echo ${ObsType} | tr a-z A-Z`    # config variable
    let nobs=${nobs}+1

    export RUNTIME_PREP_DIR=${DATA}/prepsave/${ObsType}_${AOD_QC_NAME}_${VDATE}
    mkdir -p ${RUNTIME_PREP_DIR}

    let nsat=0
    for SatId in "${satellite_list[@]}"; do
      export SatId
      export SATID=$(echo ${SatId} | tr a-z A-Z)    # config variable
      let nsat=${nsat}+1

      let nscan=0
      for AOD_SCAN in "${goes_scan_list[@]}"; do
        export AOD_SCAN
        export Aod_Scan=$(echo ${AOD_SCAN} | tr A-Z a-z)    # config variable
        let nscan=${nscan}+1

        ##
        ######################################################
        ## Check gridded L3 AOD files for restart ability
        ######################################################
        ##
        let ic=0
        let endvhr=23

        export out_file_prefix=${ObsType}_${AOD_SCAN}_${MODELNAME}_${SatId}
        checkfile="${out_file_prefix}_${VDATE}_*_${AOD_QC_NAME}.nc"
        obs_file_count=$(find ${COMOUTproc} -name ${checkfile} | wc -l )
        if [ ${obs_file_count} -eq 0 ]; then
          let ic=0
        elif [ ${obs_file_count} -eq 24 ]; then
          if [ ${nscan} -lt ${num_scan} ]; then    ## check whether vldhr=00 of next scan_mode and/or next satid
            export out_file_prefix=${ObsType}_${goes_scan_list[${nscan}]}_${MODELNAME}_${SatId}
            checkfile=${COMOUTproc}/${out_file_prefix}_${VDATE}_00_${AOD_QC_NAME}.nc
            if [ -s ${checkfile} ]; then
              let ic=${endvhr}+1      ## skip current AOD_SCAN PROCESSING
            else
              ## re-do the last hour in case it is corrupted during copying
              let ic=${endvhr}
              echo "DEBUG :: Restart ASCII2NC from ${ObsType} ${SatId} ${AOD_SCAN} hour ${ic}"
            fi
          else
            if [ ${nsat} -lt ${num_sat} ]; then
              out_file_prefix=${ObsType}_${goes_scan_list[0]}_${MODELNAME}_${satellite_list[${nstat}]}
              checkfile=${COMOUTproc}/${out_file_prefix}_${VDATE}_00_${AOD_QC_NAME}.nc
              if [ -s ${checkfile} ]; then
                let ic=${endvhr}+1      ## skip current AOD_SCAN PROCESSING
              else
                let ic=${endvhr}
                echo "DEBUG :: Restart ASCII2NC from ${ObsType} ${SatId} ${AOD_SCAN} hour ${ic}"
              fi
            else     ## Last SatID and AodScan file found
              ## check whether the first integrated AOD file existed or not
              export out_file_prefix=${ObsType}_${goes_scan_list[0]}_${MODELNAME}_join
              checkfile=${COMOUTproc}/${out_file_prefix}_${VDATE}_00_${AOD_QC_NAME}.nc
              if [ -s ${checkfile} ]; then
                let ic=${endvhr}+1      ## skip current AOD_SCAN PROCESSING
                echo "DEBUG :: *** Restart skip ASCII2NC for ObsType SatId AOD_SCAN ***"
              else
                ## re-do the last hour in case it is corrupted during copying
                let ic=${endvhr}
                echo "DEBUG :: Restart ASCII2NC from ${ObsType} ${SatId} ${AOD_SCAN} hour ${ic}"
              fi
            fi
          fi
        else
          let ic=${obs_file_count}-1
          echo "DEBUG :: Restart ASCII2NC from ${ObsType} ${SatId} ${AOD_SCAN} hour ${ic}"
        fi
        ######################################################
        ## Check gridded L3 AOD files for restart ability
        ######################################################
        ##
	#
	## The cutoff time is linked to the usage of
	## time_offset_warning and OBS_WINDOW_* currently
	## set as +- 15 mins
	#
	let forward_search_cutoff_time=1500
	let backward_search_cutoff_time=4500
	#
        while [ ${ic} -le ${endvhr} ]; do
          vldhr=$(printf %2.2d ${ic})
	  export VHOUR=${vldhr}    # config variable
          flag_find_abi=no
          flag_reverse_find=no
          idir=${DCOMINabi}/${VDATE}/goes_abi/GOES_${AOD_SCAN}
          if [ -d ${idir} ]; then
            checkfile="OR_${OBSTYPE}-L2-${AOD_SCAN}-M*_${SATID}_s${jday}${vldhr}*.nc"
            obs_file_count=$(find ${idir} -name ${checkfile} | wc -l )
            if [ ${obs_file_count} -gt 0 ]; then
              ls ${idir}/${checkfile} > all_hourly_aod_file
              export filein_aod=$(head -n1 all_hourly_aod_file)    # config variable
              extract_file=$( basename ${filein_aod} )
              scan_start_time=$(echo ${extract_file} | awk -F"_" '{print $4}')
              check_digit11=$(echo "${scan_start_time}" | cut -c11-11)
              if [ "${check_digit11}" == "0" ]; then
                check_digit12=$(echo "${scan_start_time}" | cut -c12-12)
                if [ "${check_digit12}" == "0" ]; then
                  minsec=$(echo "${scan_start_time}" | cut -c13-14)
                else
                  minsec=$(echo "${scan_start_time}" | cut -c12-14)
                fi
              else
                  minsec=$(echo "${scan_start_time}" | cut -c11-14)
              fi
              let scan_min_sec=${minsec}
              if [ ${scan_min_sec} -gt ${forward_search_cutoff_time} ]; then
                echo "DEBUG :: NO valid aod file within time limit; start reverse search"
                flag_reverse_find=yes
              else
                echo "DEBUG :: Find ${filein_aod} for valid hour ${vldhr}"
                flag_find_abi=yes
              fi
            else
              echo "DEBUG :: NO available ${SATID} GOES_${AOD_SCAN} for hour ${vldhr} in forward search"
              flag_reverse_find=yes
            fi
            if [ "${flag_reverse_find}" == "yes" ]; then
              VDATEm1=$(${NDATE} -1 ${VDATE}${vldhr} | cut -c1-8)
              vldhrm1=$(${NDATE} -1 ${VDATE}${vldhr} | cut -c9-10)
              jdaym1=$(date2jday.sh ${VDATEm1})
              echo "DEBUG ::  reverse search start; checking file for ${jdaym1}${vldhrm1}"
              idirm1=${DCOMINabi}/${VDATEm1}/goes_abi/GOES_${AOD_SCAN}
              if [ -d ${idirm1} ]; then
                checkfile="OR_${OBSTYPE}-L2-${AOD_SCAN}-M*_${SATID}_s${jdaym1}${vldhrm1}*.nc"
                obs_file_count=$(find ${idirm1} -name ${checkfile} | wc -l )
                if [ ${obs_file_count} -gt 0 ]; then
                  ls ${idirm1}/${checkfile} > all_hourly_aod_file
                  export filein_aod=$(tail -n1 all_hourly_aod_file)    # config variable
                  extract_file=$( basename ${filein_aod} )
                  scan_start_time=$(echo ${extract_file} | awk -F"_" '{print $4}')
                  check_digit11=$(echo "${scan_start_time}" | cut -c11-11)
                  if [ "${check_digit11}" == "0" ]; then
                    check_digit12=$(echo "${scan_start_time}" | cut -c12-12)
                    if [ "${check_digit12}" == "0" ]; then
                      minsec=$(echo "${scan_start_time}" | cut -c13-14)
                    else
                      minsec=$(echo "${scan_start_time}" | cut -c12-14)
                    fi
                  else
                    minsec=$(echo "${scan_start_time}" | cut -c11-14)
                  fi
                  let scan_min_sec=${minsec}
                  if [ ${scan_min_sec} -lt ${backward_search_cutoff_time} ]; then
                    echo "DEBUG :: NO valid aod file within time limit in reverse search"
                  else
                    echo "DEBUG :: Find ${filein_aod} for valid hour ${vldhr}"
                    flag_find_abi=yes
                  fi
                else
                  echo "DEBUG :: NO available ${SATID} GOES_${AOD_SCAN} for hour ${VDATEm1} ${vldhrm1}"
                fi
              else
                echo "DEBUG :: Can not find ${idirm1}, skip reverse search for hour ${VDATE} ${vldhr}"
              fi
            fi
            if [ "${flag_find_abi}" == "yes" ];then
              if [ -s ${conf_dir}/${config_file} ]; then
                ## check corrupted input file
                msg=$(ncdump -h ${filein_aod} 1> /dev/null 2>&1 ; err=$? ; echo ${err} )
		if [ ${msg} -eq 0 ]; then
                  run_metplus.py ${conf_dir}/${config_file} ${config_common}
                  export err=$?; err_chk

                  if [ "${SENDCOM}" = "YES" ]; then
                    cpfile=${RUNTIME_PREP_DIR}/${out_file_prefix}_${VDATE}_${VHOUR}_${AOD_QC_NAME}.nc
                    if [ -s ${cpfile} ]; then cp -v ${cpfile} ${COMOUTproc}; fi
                  fi
                else
                  if [ "${SENDMAIL}" = "YES" ]; then
                    echo "WARNING :: Detected a corrupted input file ${filein_aod} for ${VDATE} ${vldhr}" >> mailmsg
                    echo "==============" >> mailmsg
                    flag_send_message=YES
                  fi
                fi
              else
                echo "WARNING: can not find ${conf_dir}/${config_file}"
              fi
            else
              if [ "${SENDMAIL}" = "YES" ]; then
                echo "DEBUG :: NO available ${SATID} GOES_${AOD_SCAN} for hour ${VDATE} ${vldhr}" >> mailmsg
                echo "==============" >> mailmsg
                flag_send_message=YES
              fi
            fi
          else
            if [ "${vldhr}" == "00" ]; then
              VDATEm1=$(${NDATE} -1 ${VDATE}${vldhr} | cut -c1-8)
              vldhrm1=$(${NDATE} -1 ${VDATE}${vldhr} | cut -c9-10)
              jdaym1=$(date2jday.sh ${VDATEm1})
              echo "DEBUG ::  reverse search start; checking file for ${jdaym1}${vldhrm1}"
              idirm1=${DCOMINabi}/${VDATEm1}/goes_abi/GOES_${AOD_SCAN}
              if [ -d ${idirm1} ]; then
                checkfile="OR_${OBSTYPE}-L2-${AOD_SCAN}-M*_${SATID}_s${jdaym1}${vldhrm1}*.nc"
                obs_file_count=$(find ${idirm1} -name ${checkfile} | wc -l )
                if [ ${obs_file_count} -gt 0 ]; then
                  ls ${idirm1}/${checkfile} > all_hourly_aod_file
                  export filein_aod=$(tail -n1 all_hourly_aod_file)    # config variable
                  extract_file=$( basename ${filein_aod} )
                  scan_start_time=$(echo ${extract_file} | awk -F"_" '{print $4}')
                  check_digit11=$(echo "${scan_start_time}" | cut -c11-11)
                  if [ "${check_digit11}" == "0" ]; then
                    check_digit12=$(echo "${scan_start_time}" | cut -c12-12)
                    if [ "${check_digit12}" == "0" ]; then
                      minsec=$(echo "${scan_start_time}" | cut -c13-14)
                    else
                      minsec=$(echo "${scan_start_time}" | cut -c12-14)
                    fi
                  else
                    minsec=$(echo "${scan_start_time}" | cut -c11-14)
                  fi
                  let scan_min_sec=${minsec}
                  if [ ${scan_min_sec} -lt ${backward_search_cutoff_time} ]; then
                    echo "DEBUG :: NO valid aod file within time limit in reverse search"
                  else
                    echo "DEBUG :: Find ${filein_aod} for valid hour ${vldhr}"
                    flag_find_abi=yes
                  fi
                else
                  echo "DEBUG :: NO available ${SATID} GOES_${AOD_SCAN} for hour ${VDATEm1} ${vldhrm1}"
                fi
              else
                echo "DEBUG :: Can not find ${idirm1}, skip reverse search for hour ${VDATE} ${vldhr}"
              fi
            fi
            if [ "${flag_find_abi}" == "yes" ];then
              if [ -s ${conf_dir}/${config_file} ]; then
                ## check corrupted input file
                msg=$(ncdump -h ${filein_aod} 1> /dev/null 2>&1 ; err=$? ; echo ${err} )
		if [ ${msg} -eq 0 ]; then
                  run_metplus.py ${conf_dir}/${config_file} ${config_common}
                  export err=$?; err_chk
                  if [ "${SENDCOM}" = "YES" ]; then
                    cpfile=${RUNTIME_PREP_DIR}/${out_file_prefix}_${VDATE}_${VHOUR}_${AOD_QC_NAME}.nc
                    if [ -s ${cpfile} ]; then cp -v ${cpfile} ${COMOUTproc}; fi
                  fi
                else
                  if [ "${SENDMAIL}" = "YES" ]; then
                    echo "WARNING :: Detected a corrupted input file ${filein_aod} for ${VDATE} ${vldhr}" >> mailmsg
                    echo "==============" >> mailmsg
                    flag_send_message=YES
                  fi
                fi
              else
                echo "WARNING: can not find ${conf_dir}/${config_file}"
              fi
            else
              if [ "${SENDMAIL}" = "YES" ]; then
                echo "DEBUG :: Can not find ${idir} for ${VDATE} ${vldhr}" >> mailmsg
                echo "==============" >> mailmsg
                flag_send_message=YES
              fi
            fi
            echo "DEBUG :: Can not find ${idir} for ${VDATE} ${vldhr}, skip ro next valid hour"
          fi  ## find idir
          ((ic++))
        done  # vldhr
      done  # AOD_SCAN
    done  # SatId
    #
    ## Integrate East and West point2grid nc into a single nc file for stats per valid hours
    #
    let nscan=0
    for AOD_SCAN in "${goes_scan_list[@]}"; do
      let nscan=${nscan}+1

      goes_east_aod_prefix=${ObsType}_${AOD_SCAN}_${MODELNAME}_${satellite_list[0]}_${VDATE}
      goes_west_aod_prefix=${ObsType}_${AOD_SCAN}_${MODELNAME}_${satellite_list[1]}_${VDATE}

      ##
      ######################################################
      ## Check gridded L3 AOD MERGED files for restart ability
      ######################################################
      ##
      let ic=0
      let endvhr=23

      checkfile="${ObsType}_${AOD_SCAN}_${MODELNAME}_join_${VDATE}_*_${AOD_QC_NAME}.nc"
      join_file_count=$(find ${COMOUTproc} -name ${checkfile} | wc -l )
      if [ ${join_file_count} -eq 0 ]; then
        let ic=0
      elif [ ${join_file_count} -eq 24 ]; then
        if [ ${nscan} -lt ${num_scan} ]; then    ## check whether vldhr=00 of next scan_mode
          out_file_prefix=${ObsType}_${goes_scan_list[${nscan}]}_${MODELNAME}_join
          checkfile=${COMOUTproc}/${out_file_prefix}_${VDATE}_00_${AOD_QC_NAME}.nc
          if [ -s ${checkfile} ]; then
            let ic=${endvhr}+1      ## skip current AOD Merge PROCESSING
          else
            ## re-do the last hour in case it is corrupted during copying
            let ic=${endvhr}
            echo "DEBUG :: Restart AOD Merge process from ${ObsType} ${SatId} ${AOD_SCAN} hour ${ic}"
          fi
        else     ## Last integrated AodScan file found
          if [ ${nobs} -lt ${num_obs} ]; then    ## check whether vldhr=00 of next obs
            out_file_prefix=${grid2grid_list[nobs]}_${goes_scan_list[0]}_${MODELNAME}_join
            checkfile=${COMOUTproc}/${out_file_prefix}_${VDATE}_00_${AOD_QC_NAME}.nc
            if [ -s ${checkfile} ]; then
              let ic=${endvhr}+1      ## skip current AOD_SCAN PROCESSING
            else
              ## re-do the last hour in case it is corrupted during copying
              let ic=${endvhr}
              echo "DEBUG :: Restart AOD integrated process from ${ObsType} ${AOD_SCAN} hour ${ic}"
            fi
          else
            ## re-do the last hour in case it is corrupted during copying
            let ic=${endvhr}
            echo "DEBUG :: Restart AOD integrted process from ${ObsType} ${AOD_SCAN} hour ${ic}"
          fi
        fi
      else
        let ic=${join_file_count}-1
        echo "DEBUG :: Restart AOD integrated process from ${ObsType} ${AOD_SCAN} hour ${ic}"
      fi
      ######################################################
      ## Check gridded L3 AOD files for restart ability
      ######################################################
      ##
      while [ ${ic} -le ${endvhr} ]; do
        vldhr=$(printf %2.2d ${ic})
        goes_east_aod=${goes_east_aod_prefix}_${vldhr}_${AOD_QC_NAME}.nc
        goes_west_aod=${goes_west_aod_prefix}_${vldhr}_${AOD_QC_NAME}.nc

        goes_east_aod_file=${RUNTIME_PREP_DIR}/${goes_east_aod}
        goes_west_aod_file=${RUNTIME_PREP_DIR}/${goes_west_aod}

        if [ ! -s ${goes_east_aod_file} ] && [ -s ${COMOUTproc}/${goes_east_aod} ]; then
            cpreq ${COMOUTproc}/${goes_east_aod} ${RUNTIME_PREP_DIR}
        fi

        if [ ! -s ${goes_west_aod_file} ] && [ -s ${COMOUTproc}/${goes_west_aod} ]; then
            cpreq ${COMOUTproc}/${goes_west_aod} ${RUNTIME_PREP_DIR}
        fi

        join_script_name=${USHevs}/${COMPONENT}/integrate_goes_east_west_aod.py
        export join_aod_file=${RUNTIME_PREP_DIR}/${ObsType}_${AOD_SCAN}_${MODELNAME}_join_${VDATE}_${vldhr}_${AOD_QC_NAME}.nc
        if [ -s ${goes_east_aod_file} ] && [ -s ${goes_west_aod_file} ]; then
            python ${join_script_name} ${goes_east_aod_file} ${goes_west_aod_file} ${join_aod_file}
        elif [ -s ${goes_east_aod_file} ] && [ ! -s ${goes_west_aod_file} ]; then
            cp ${goes_east_aod_file} ${join_aod_file}
        elif [ ! -s ${goes_east_aod_file} ] && [ -s ${goes_west_aod_file} ]; then
            cp ${goes_west_aod_file} ${join_aod_file}
        else
            echo "DEBUG ::  No GOES-East and GOES-West point2grid ABI L3 AOD files for ${VDATE} ${vldhr}"
        fi

        if [ "${SENDCOM}" = "YES" ]; then
            if [ -s ${join_aod_file} ]; then cp -v ${join_aod_file} ${COMOUTproc}; fi
        fi
        ((ic++))
      done  # vldhr
    done  # AOD_SCAN
  done  # ObsType
else
    if [ "${SENDMAIL}" = "YES" ]; then
        echo "WARNING: No ${MODELNAME} ${VARID} grib2 output was avaiable as POINT2GRID template valid ${VDATE}" > mailmsg
        echo "==============" >> mailmsg
        flag_send_message=YES
    fi

    echo "WARNING: No ${MODELNAME} ${VARID} grib2 was available as POINT2GRID template for valid date ${VDATE}"
fi

if [ "${flag_send_message}" == "YES" ]; then
    export subject="${MODELNAME} ${AOD_SCAN} PROCESSING ISSUES for EVS ${COMPONENT}"
    echo "Job ID: $jobid" >> mailmsg
    cat mailmsg | mail -s "$subject" $MAILTO 
fi
exit


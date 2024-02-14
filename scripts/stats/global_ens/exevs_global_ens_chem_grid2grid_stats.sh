#!/bin/bash
########################################################################
###  UNIX Script Documentation Block
###                      .
### Script name:         exevs_global_ens_chem_grid2grid_stats.sh
### Script description:  To run grid-to-grid verification on all global chem
### Original Author   :  Partha Bhattacharjee
###
###   Change Logs:
###
###   01/16/2024   Ho-Chun Huang  consolidate exevs_global_ens_chem_grid2grid scripts
###
########################################################################
set -x

## For temporary stoage on the working dirary before moving to COMOUT
export finalstat=${DATA}/final
mkdir -p ${finalstat}

export model1=`echo ${MODELNAME} | tr a-z A-Z`

export CONFIGevs=${CONFIGevs:-${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}
export config_common=${PARMevs}/metplus_config/machine.conf

export METPLUS_PATH

export obstype=`echo ${OBTTYPE} | tr a-z A-Z`
export RUNnow=${OBTTYPE}

if [ -e mailmsg ]; then /bin/rm -f mailmsg; fi

case ${OBTTYPE} in
    abi)   flag_send_message=NO
           grid_stat_conf_file=${CONFIGevs}/SeriesAnalysis_fcstGEFS_obs${obstype}.conf
           export mdl_cyc=00
           ## check valid time observation input VDATE 00, 03, 06, 09, 12, 15, 18, 21 Z and
           ## corresponding fcst file for each LEAD_SEQ 00, 03, 06, 09, 12, 15, 18, 21
           ## since th mdl_cyc is t00z, it is essentiall one fcst file versue 1 observation input
           export vlddate=$(VDATE}
           OBSIN=${DCOMIN}/${vlddate}/validation_data/aq/${OBTTYPE}
           let tnow=0
           while [ ${tnow} -le 21 ]; do   ## check valid time observation input
               num_obs=0
               export vldhr=$(printf %2.2d ${tnow})
               checkfile=${OBSIN}/ABI-L3-AOD_GEFS_${vlddate}_${vldhr}0000.nc
               if [ -s ${checkfile} ]; then
                   ((num_obs++))
                   export datehr=${vlddate}${vldhr}
                   num_fcst_in_metplus=0
                   recorded_temp_list=${DATA}/fcstlist_in_metplus
                   if [ -e ${recorded_temp_list} ]; then rm -f ${recorded_temp_list}; fi
                   let ihr=0
                   while [ ${ihr} -le 21 ]; do    ## check lead seq input fcst file validated at datehr
                       fnum=$(printf %3.3d ${ihr})
                       fhr=$(printf %2.2d ${ihr})
		       adate=$(${NDATE} -${ihr} ${datehr})
                       aday=`echo ${adate} |cut -c1-8`
                       acyc=`echo ${adate} |cut -c9-10`
                       if [ "${acyc}" == "${mdl_cyc}" ]; then
                           mdlfcst=${COMINgefs}/${MODELNAME}.${aday}/${acyc}/chem/pgrb2ap25
                           checkfile=${mdlfcst}/${MODELNAME}.chem.t${acyc}z.a2d_0p25.f${fnum}.grib2
                           if [ -s ${checkfile} ]; then
                               echo "${checkfile} found"
                               echo ${fhr} >> ${recorded_temp_list}
			       ((num_fcst_in_metplus++))
                           else
                               if [ ${SENDMAIL} = "YES" ]; then
                                   echo "WARNING: No GEFS 00Z chem/pgrb2ap25 file was available for valid date ${VDATE}" >> mailmsg
                                   echo "Missing file is ${checkfile}" >> mailmsg
                                   echo "==============" >> mailmsg
                                   flag_send_message=YES
                               fi
    
                               echo "WARNING: No GEFS 00Z chem/pgrb2ap25 file was available for valid date ${VDATE}"
                               echo "WARNING: Missing file is ${checkfile}"
                           fi
                       fi
                       let ihr=${ihr}+3
                   done
               else
                   if [ ${SENDMAIL} = "YES" ]; then
                       echo "WARNING: No "GOES L3 AOD file was available for valid date ${vlddate}" >> mailmsg
                       echo "Missing file is ${checkfile}" >> mailmsg
                       echo "==============" >> mailmsg
                       flag_send_message=YES
                   fi
    
                   echo "WARNING: No "GOES L3 AOD file was available for valid date ${VDATE}"
                   echo "WARNING: Missing file is ${checkfile}"
               fi
               if [ -s ${recorded_temp_list} ]; then
                 export fcsthours_list=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' ${recorded_temp_list}`
               fi
               if [ -e ${recorded_temp_list} ]; then rm -f ${recorded_temp_list}; fi
               export num_fcst_in_metplus
               echo "number of fcst lead in_metplus series_stat for ${OBTTYPE} == ${num_fcst_in_metplus}"
               echo "index of hourly obs_found == ${obs_num}"
               if [ ${num_fcst_in_metplus} -gt 0 -a ${obs_num} -gt 0 ]; then 
                 export fcsthours=${fcsthours_list}
                 run_metplus.py ${grid_stat_conf_file} ${config_common}
                 export err=$?; err_chk
               else
                 echo "WARNING: NO ${obstype} OBS OR MODEL DATA"
                 echo "WARNING: NUM FCST=${num_fcst_in_metplus}, INDEX OBS=${num_obs}"
               fi
           done   ## loop by valid obs vldhr
           if [ ${SENDCOM} = "YES" ]; then
               cpdir=${finalstat}/${STEP}/${OBTTYPE}/${RUN}.${vlddate}
               if [ -d ${cpdir} ]; then      ## does not exist if run_metplus.py did not execute
                   stat_file_count=$(find ${cpdir} -name "*${OBTTYPE}*" | wc -l)   ## all vldhr statistic in vlddate
                   if [ ${stat_file_count} -ne 0 ]; then cpreq ${cpdir}/*${OBTTYPE}* ${COMOUTsmall}; fi
               fi
           fi
           stat_file_count=$(find ${COMOUTsmall} -name "*${OBTTYPE}*" | wc -l)
           if [ ${stat_file_count} -ne 0 ]; then  ## run stat_analysis for one daily stat file
               cpreq ${COMOUTsmall}/*${OBTTYPE}* ${finalstat}
               run_metplus.py ${CONFIGevs}/${stat_analysis_conf_file} ${config_common}
               export err=$?; err_chk
               if [ ${SENDCOM} = "YES" ]; then
                   cpfile=${finalstat}/evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}_${OBTTYPE}.v${vlddate}.stat
                   if [ -e ${cpfile} ]; then cpreq ${cpfile} ${COMOUTfinal}; fi
               fi
           fi
           ;;
    geos5) flag_send_message=NO
           num_obs=0
           let tnow=1
           while [ ${tnow} -le 22 ]; do
               vldhr=$(printf %2.2d ${tnow})
               checkfile=${OBSIN}/GEOS.fp.asm.tavg3_2d_aer_Nx.{VDATE}_${vldhr)30.V01.nc4
               if [ -s ${checkfile} ]; then
                   ((num_obs++))
               else
               fi
               let icnt=1
               while [ ${icnt} -le 23 ]; do
                   fnum=$(printf %2.2d ${icnt})
                   checkfile=${OBSIN}/GEOS.fp.asm.tavg3_2d_aer_Nx.{VDATE}_${vldhr)30.V01.nc4.${fnum}
                   if [ -s ${checkfile} ]; then
                       ((num_obs++))
                   else
                       if [ ${SENDMAIL} = "YES" ]; then
                           echo "WARNING: No GEOS5 validation NC file was available for valid date ${VDATE}" >> mailmsg
                           echo "Missing file is ${checkfile}" >> mailmsg
                           echo "==============" >> mailmsg
                           flag_send_message=YES
                       fi
    
                       echo "WARNING: No GEOS5 validation NC file was available for valid date ${VDATE}"
                       echo "WARNING: Missing file is ${checkfile}"
                   fi
                   ((icnt++))
               done
               let tnow=${tnow}+3
           done
           export stats_var="taod daod ocaod bcaod suaod ssaod"
           file_header=GridStat_fcstGEFS_obs${obstype};;
    icap)  flag_send_message=NO
           num_obs=0
           for ivar in dustaod550 modeaod550 pm seasaltaod550 seasaltaod550; do 
               checkfile=${OBSIN}/icap_${VDATE}00_c4_${ivar}.nc
               if [ -s ${checkfile} ]; then
                   ((num_obs++))
               else
                   if [ ${SENDMAIL} = "YES" ]; then
                       echo "WARNING: No ICAP validation NC file was available for valid date ${VDATE}" >> mailmsg
                       echo "Missing file is ${checkfile}" >> mailmsg
                       echo "==============" >> mailmsg
                       flag_send_message=YES
                   fi
    
                   echo "WARNING: No ICAP validation NC file was available for valid date ${VDATE}"
                   echo "WARNING: Missing file is ${checkfile}"
               fi
           done
           export stats_var="taod daod"
           export PDYHHm3=$($NDATE -72 $PDYHH)
           export cyc=00
           export maskpath=$MASKS
           file_header=GridStat_fcstGEFS_obs${obstype};;
    viirs) flag_send_message=NO
           let tnow=0
           while [ ${tnow} -le 21 ]; do
               vldhr=$(printf %2.2d ${tnow})
               checkfile=${OBSIN}/VIIRS-L3-AOD_GEFS_1HR_${VDATE}_${vldhr}0000.nc
               if [ -s ${checkfile} ]; then
                   ((num_obs++))
               else
                   if [ ${SENDMAIL} = "YES" ]; then
                       echo "WARNING: No VIIRS L3 AOD file was available for valid date ${VDATE}" >> mailmsg
                       echo "Missing file is ${checkfile}" >> mailmsg
                       echo "==============" >> mailmsg
                       flag_send_message=YES
                   fi
    
                   echo "WARNING: No VIIRS L3 AOD file was available for valid date ${VDATE}"
                   echo "WARNING: Missing file is ${checkfile}"
               fi
               let tnow=${tnow}+3
           done
           grid_stat_conf_file=${CONFIGevs}/SeriesAnalysis_fcstGEFS_obs${obstype}.conf
           export mdl_cyc=00
           export VDATE2=$PDYm3
           mdlfcst=${COMINgefs}/${MODELNAME}.${VDATE}/${mdl_cyc}/chem/pgrb2ap25
           num_fcst_in_metplus=0
           recorded_temp_list=${DATA}/fcstlist_in_metplus
           if [ -e ${recorded_temp_list} ]; then rm -f ${recorded_temp_list}; fi
           let tnow=0
           while [ ${tnow} -le 21 ]; do
               fnum=$(printf %3.3d ${tnow})
               fhr=$(printf %2.2d ${tnow})
               checkfile=${mdlfcst}/${MODELNAME}.chem.t${mdl_cyc}z.a2d_0p25.f${fnum}.grib2
               if [ -s ${checkfile} ]; then
                   echo "${checkfile} found"
                   echo ${fhr} >> ${recorded_temp_list}
                   let "num_fcst_in_metplus=num_fcst_in_metplus+1"
               else
                   if [ ${SENDMAIL} = "YES" ]; then
                       echo "WARNING: No GEFS 00Z chem/pgrb2ap25 file was available for valid date ${VDATE}" >> mailmsg
                       echo "Missing file is ${checkfile}" >> mailmsg
                       echo "==============" >> mailmsg
                       flag_send_message=YES
                   fi
    
                   echo "WARNING: No GEFS 00Z chem/pgrb2ap25 file was available for valid date ${VDATE}"
                   echo "WARNING: Missing file is ${checkfile}"
               fi
               let tnow=${tnow}+3
           done
           if [ -s ${recorded_temp_list} ]; then
             export fcsthours_list=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' ${recorded_temp_list}`
           fi
           if [ -e ${recorded_temp_list} ]; then rm -f ${recorded_temp_list}; fi
           export num_fcst_in_metplus
           echo "number of fcst lead in_metplus series_stat for ${OBTTYPE} == ${num_fcst_in_metplus}"
           echo "index of 3-hourly obs_found == ${obs_num}"
           if [ ${num_fcst_in_metplus} -gt 0 -a ${obs_num} -gt 0 ]; then 
             export fcsthours=${fcsthours_list}
             run_metplus.py ${grid_stat_conf_file} ${config_common}
             export err=$?; err_chk
           else
             echo "WARNING: NO ${obstype} OBS OR MODEL DATA"
             echo "WARNING: NUM FCST=${num_fcst_in_metplus}, INDEX OBS=${num_obs}"
           fi
           if [ ${SENDCOM} = "YES" ]; then
               cpdir=${finalstat}/${STEP}/${OBTTYPE}/${RUN}.${VDATE}
               if [ -d ${cpdir} ]; then      ## does not exist if run_metplus.py did not execute
                   stat_file_count=$(find ${cpdir} -name "*${OBTTYPE}*" | wc -l)
                   if [ ${stat_file_count} -ne 0 ]; then cpreq ${cpdir}/*${OBTTYPE}* ${COMOUTsmall}; fi
               fi
           fi
           stat_file_count=$(find ${COMOUTsmall} -name "*${OBTTYPE}*" | wc -l)
           if [ ${stat_file_count} -ne 0 ]; then
               cpreq ${COMOUTsmall}/*${OBTTYPE}* ${finalstat}
               run_metplus.py ${stat_analysis_conf_file} ${config_common}
               export err=$?; err_chk
               if [ ${SENDCOM} = "YES" ]; then
                   cpfile=${finalstat}/evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}_${OBTTYPE}.v${VDATE}.stat
                   if [ -e ${cpfile} ]; then cpreq ${cpfile} ${COMOUTfinal}; fi
               fi
           fi
           ;;
esac
if [ "${flag_send_message}" = "YES" ]; then
                                   export subject="GEFS 00Z chem/pgrb2ap25 file Missing for EVS ${COMPONENT}"
                       export subject="GOES L3 AOD file Missing for EVS ${COMPONENT}"
                           export subject="GEOS5 validation NC file Missing for EVS ${COMPONENT}"
                       export subject="ICAP validation NC file Missing for EVS ${COMPONENT}"
                       export subject="VIIRS L3 AOD file Missing for EVS ${COMPONENT}"
                       export subject="GEFS 00Z chem/pgrb2ap25 file Missing for EVS ${COMPONENT}"
              export subject="t${acyc}z ${outtyp}${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
    echo "Job ID: $jobid" >> mailmsg
    cat mailmsg | mail -s "$subject" $MAILTO 
fi


#############################
# run Series/Grid Analysis
#############################

if [ "${num_var}" != "1" ]; then
    for ivar in ${stats_var}; do
        grid_stat_conf_file=${file_header}_${ivar}.conf
        METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/metplus_chem.conf \
             -c ${CONFIGevs}/${grid_stat_conf_file} ${config_common}
        export err=$?; err_chk"
    done
else
    METPLUS_PATH}/ush/run_metplus.py -c ${CONFIGevs}/metplus_chem.conf \
        -c ${CONFIGevs}/${grid_stat_conf_file} ${config_common}
    export err=$?; err_chk
fi
      export hour
      export mdl_cyc=${hour}    ## is needed for *.conf

      let ihr=1
      num_fcst_in_metplus=0
      recorded_temp_list=${DATA}/fcstlist_in_metplus
      if [ -e ${recorded_temp_list} ]; then rm -f ${recorded_temp_list}; fi
      while [ ${ihr} -le ${fcstmax} ]; do
        filehr=$(printf %3.3d ${ihr})    ## fhr of grib2 filename is in 3 digit for aqmv7
        fhr=$(printf %2.2d ${ihr})       ## fhr for the processing valid hour is in 2 digit
        export fhr
    
          if [ -s ${fcst_file} ]; then
            echo "${fhr} found"
            echo ${fhr} >> ${recorded_temp_list}
            let "num_fcst_in_metplus=num_fcst_in_metplus+1"
          else
            if [ $SENDMAIL = "YES" ]; then
              echo "WARNING: No AQM ${outtyp}${bctag} forecast was available for ${aday} t${acyc}z" > mailmsg
              echo "Missing file is ${fcst_file}" >> mailmsg
              echo "Job ID: $jobid" >> mailmsg
              cat mailmsg | mail -s "$subject" $MAILTO
            fi

            echo "WARNING: No AQM ${outtyp}${bctag} forecast was available for ${aday} t${acyc}z"
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
      echo "number of fcst lead in_metplus point_stat for ${outtyp}${bctag} == ${num_fcst_in_metplus}"
    
      if [ ${num_fcst_in_metplus} -gt 0 -a ${obs_hourly_found} -eq 1 ]; then
        export fcsthours=${fcsthours_list}
        run_metplus.py ${point_stat_conf_file} ${config_common}
        export err=$?; err_chk
      else
        echo "WARNING: NO ${cap_outtyp} FORECAST OR OBS TO VERIFY"
        echo "WARNING: NUM FCST=${num_fcst_in_metplus}, INDEX OBS=${obs_hourly_found}"
      fi
    done   ## hour loop

exit

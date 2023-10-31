#!/bin/ksh
#######################################################################
##  UNIX Script Documentation Block
##                      .
## Script name:         exevs_aqm_grid2obs_stats.sh
## Script description:  Perform MetPlus PointStat of Air Quality Model.
## Original Author   :  Perry Shafran
##
##   Change Logs:
##
##   04/26/2023   Ho-Chun Huang  modification for using AirNOW ASCII2NC
##   05/22/2023   Ho-Chun Huang  separate hourly ozone by model verified time becasuse
##                               of directory path depends on model verified hour.
##   10/31/2023   Ho-Chun Huang  Update EVS model input directory structure from AQMv6 to AQMv7
##
##
#######################################################################
#
set -x

mkdir -p ${DATA}/logs
mkdir -p ${DATA}/stat
export finalstat=${DATA}/final
mkdir -p ${DATA}/final

#######################################################################
# Define INPUT OBS DATA TYPE for PointStat
#######################################################################
#
if [ "${airnow_hourly_type}" == "aqobs" ]; then
    export HOURLY_INPUT_TYPE=hourly_aqobs
else
    export HOURLY_INPUT_TYPE=hourly_data
fi

export dirname=aqm
export gridspec=793
export fcstmax=72
#
## export MASK_DIR is declared in the ~/EVS/jobs/JEVS_AQM_STATS 
#
export model1=`echo ${MODELNAME} | tr a-z A-Z`
echo ${model1}

# Begin verification of both the hourly data of ozone and PM
#
# The valid time of forecast model output is the reference here in PointStat
# Because of the valid time definition between forecat output and observation is different
#     For average concentration of a period [ vhr-1 to vhr ], aqm output is defined at vhr Z
#     while observation is defined at vhr-1 Z
# Thus, the one hour back OBS input will be checked and used in PointStat
#     [OBS_POINT_STAT_INPUT_TEMPLATE=****_{valid?fmt=%Y%m%d%H?shift=-3600}.nc]
#
cdate=${VDATE}${vhr}
vld_date=$(${NDATE} -1 ${cdate} | cut -c1-8)
vld_time=$(${NDATE} -1 ${cdate} | cut -c1-10)

VDAYm1=$(${NDATE} -24 ${cdate} | cut -c1-8)
VDAYm2=$(${NDATE} -48 ${cdate} | cut -c1-8)
VDAYm3=$(${NDATE} -72 ${cdate} | cut -c1-8)

check_file=${EVSINaqm}/${RUN}.${vld_date}/${MODELNAME}/airnow_${HOURLY_INPUT_TYPE}_${vld_time}.nc
obs_hourly_found=0
if [ -s ${check_file} ]; then
  obs_hourly_found=1
else
  echo "WARNING: Can not find pre-processed obs hourly input ${check_file}"
  if [ $SENDMAIL = "YES" ]; then 
    export subject="AQM Hourly Observed Missing for EVS ${COMPONENT}"
    echo "WARNING: No AQM ${HOURLY_INPUT_TYPE} was available for ${vld_date} ${vld_time}" > mailmsg
    echo "Missing file is ${check_file}" >> mailmsg
    echo "Job ID: $jobid" >> mailmsg
    cat mailmsg | mail -s "$subject" $maillist
  fi
fi
echo "obs_hourly_found = ${obs_hourly_found}"

for hour in 06 12; do

    export hour
    export mdl_cyc=${hour}

    for outtyp in awpozcon pm25; do
    
    # Verification to be done both on raw output files and bias-corrected files
    
      for biastyp in raw bc; do
    
        export outtyp
        export biastyp
        echo ${biastyp}
    
        if [ ${biastyp} = "raw" ]; then
          export bctag=
          export bcout=_raw
        fi
    
        if [ ${biastyp} = "bc" ]; then
          export bctag=_bc
          export bcout=_bc
        fi
    
    # check to see that model files exist, and list which forecast hours are to be used
    #
    # AQMv7 does not output IC, i.e., f000.  Thus the forecast file will be chekced from f001 to f072
    #
        let ihr=1
        numo3fcst=0
        numpmfcst=0
        while [ ${ihr} -le ${fcstmax} ]; do
          filehr=$(printf %3.3d ${ihr})    ## fhr of grib2 filename is in 3 digit for aqmv7 and 2 digit for aqmv6
          fhr=$(printf %2.2d ${ihr})       ## fhr for the processing valid hour is in 2 digit
          export fhr
    
          export datehr=${VDATE}${vhr}
          adate=`${NDATE} -${ihr} ${datehr}`
          aday=`echo ${adate} |cut -c1-8`
          acyc=`echo ${adate} |cut -c9-10`
          if [ ${acyc} = ${hour} ]; then
            fcst_file=${COMINaqm}/${dirname}.${aday}/${acyc}/aqm.t${acyc}z.awpozcon${bctag}.f${filehr}.${gridspec}.grib2
            if [ -s ${fcst_file} ]; then
              echo "${fhr} found"
              echo ${fhr} >> ${DATA}/fcstlist_o3
              let "numo3fcst=numo3fcst+1"
            else
              if [ $SENDMAIL = "YES" ]; then
                export subject="t${acyc}z ozone${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
                echo "WARNING: No AQM awpozcon${bctag} forecast was available for ${aday} t${acyc}z" > mailmsg
                echo "Missing file is ${fcst_file}" >> mailmsg
                echo "Job ID: $jobid" >> mailmsg
                cat mailmsg | mail -s "$subject" $maillist
              fi

              echo "WARNING: No AQM awpozcon${bctag} forecast was available for ${aday} t${acyc}z"
              echo "WARNING: Missing file is ${fcst_file}"
            fi 

            fcst_file=${COMINaqm}/${dirname}.${aday}/${acyc}/aqm.t${acyc}z.pm25${bctag}.f${filehr}.${gridspec}.grib2
            if [ -s ${fcst_file} ]; then
              echo "${fhr} found"
              echo ${fhr} >> ${DATA}/fcstlist_pm
              let "numpmfcst=numpmfcst+1"
            else
              if [ $SENDMAIL = "YES" ]; then
                export subject="t${acyc}z pm25${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
                echo "WARNING: No AQM pm25${bctag} forecast was available for ${aday} t${acyc}z" > mailmsg
                echo "Missing file is ${fcst_file}" >> mailmsg
                echo "Job ID: $jobid" >> mailmsg
                cat mailmsg | mail -s "$subject" $maillist
	      fi

              echo "WARNING: No AQM pm25${bctag} forecast was available for ${aday} t${acyc}z"
              echo "WARNING: Missing file is ${fcst_file}"
            fi 
          fi
          ((ihr++))
        done
        export fcsthours_o3=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' ${DATA}/fcstlist_o3`
        export fcsthours_pm=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' ${DATA}/fcstlist_pm`
        export numo3fcst
        export numpmfcst
        rm ${DATA}/fcstlist_o3 ${DATA}/fcstlist_pm
        echo "numo3fcst,numpmfcst", ${numo3fcst}, ${numpmfcst}
    
        case $outtyp in
    
            awpozcon) if [ ${numo3fcst} -gt 0 -a ${obs_hourly_found} -eq 1 ]; then
                        export fcsthours=${fcsthours_o3}
                        run_metplus.py ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/PointStat_fcstOZONE_obsAIRNOW.conf ${PARMevs}/metplus_config/machine.conf
                        export err=$?; err_chk
                        mkdir -p ${COMOUTsmall}
                        if [ ${SENDCOM} = "YES" ]; then
                          cp ${DATA}/point_stat/${MODELNAME}/* ${COMOUTsmall}
                        fi
                        if [ ${vhr} = 23 ]; then
                          mkdir -p ${COMOUTfinal}
                          cp ${COMOUTsmall}/*${outtyp}${bcout}* ${finalstat}
                          cd ${finalstat}
                          run_metplus.py ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstOZONE_obsAIRNOW_GatherByDay.conf ${PARMevs}/metplus_config/machine.conf
                          export err=$?; err_chk
                          if [ ${SENDCOM} = "YES" ]; then
                            cp ${finalstat}/evs.${STEP}.${COMPONENT}${bcout}.${RUN}.${VERIF_CASE}_ozone.v${VDATE}.stat ${COMOUTfinal}
                          fi
                        fi
                      else
                        echo "WARNING: NO O3 FORECAST OR OBS TO VERIFY"
                        echo "WARNING: NUM FCST, NUM OBS", ${numo3fcst}, ${obs_hourly_found}
                      fi
                      ;;
          pm25) if [ ${numpmfcst} -gt 0 -a ${obs_hourly_found} -eq 1 ]; then
                  export fcsthours=${fcsthours_pm}
                  run_metplus.py ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/PointStat_fcstPM2p5_obsAIRNOW.conf ${PARMevs}/metplus_config/machine.conf
                  export err=$?; err_chk
                  mkdir -p ${COMOUTsmall}
                  if [ ${SENDCOM} = "YES" ]; then
                    cp ${DATA}/point_stat/${MODELNAME}/* ${COMOUTsmall}
                  fi
                  if [ ${vhr} = 23 ]; then
                     mkdir -p ${COMOUTfinal}
                     cp ${COMOUTsmall}/*${outtyp}${bcout}* ${finalstat}
                     run_metplus.py ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstPM_obsANOWPM_GatherByDay.conf ${PARMevs}/metplus_config/machine.conf
                     export err=$?; err_chk
                     if [ ${SENDCOM} = "YES" ]; then
                       cp ${finalstat}/evs.${STEP}.${COMPONENT}${bcout}.${RUN}.${VERIF_CASE}_pm25.v${VDATE}.stat ${COMOUTfinal}
                     fi
                  fi
                else
                  echo "WARNING: NO PM FORECAST OR OBS TO VERIFY"
                  echo "WARNING: NUM FCST, NUM OBS", ${numpmfcst}, ${obs_hourly_found}
                fi
                ;;
        esac
    
      done
    
    done
done

# Daily verification of the daily maximum of 8-hr ozone
# Verification being done on both raw and bias-corrected output data

check_file=${EVSINaqm}/${RUN}.${VDATE}/${MODELNAME}/airnow_daily_${VDATE}.nc
obs_daily_found=0
if [ -s ${check_file} ]; then
  obs_daily_found=1
else
  echo "WARNING: Can not find pre-processed obs daily input ${check_file}"
  if [ $SENDMAIL = "YES" ]; then
    export subject="AQM Daily Observed Missing for EVS ${COMPONENT}"
    echo "WARNING: No AQM Daily Observed file was available for ${VDATE}" > mailmsg
    echo "Missing file is ${check_file}" >> mailmsg
    echo "Job ID: $jobid" >> mailmsg
    cat mailmsg | mail -s "$subject" $maillist
  fi
fi
echo "obs_daily_found = ${obs_daily_found}"


if [ ${vhr} = 11 ]; then

  fcstmax=48
  for biastyp in raw bc; do

    export biastyp
    echo ${biastyp}

    if [ ${biastyp} = "raw" ]; then
      export bctag=
      export bcout=_raw
    fi

    if [ ${biastyp} = "bc" ]; then
      export bctag=_bc
      export bcout=_bc
    fi

    for hour in 06 12; do

      export hour
      export mdl_cyc=${hour}

      ##  search for processed daily 8-hr ozone max model files

      ozmax8=0
      for chk_date in ${VDAYm1} ${VDAYm2} ${VDAYm3}; do
        ozmax8_preprocessed_file=${EVSINaqm}/atmos.${chk_date}/aqm/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2
        if [ -s ${ozmax8_preprocessed_file} ]; then
          let "ozmax8=ozmax8+1"
        else
          if [ $SENDMAIL = "YES" ]; then
            export subject="ozmax8${bctag} AQM Daily Forecast Data Missing for EVS ${COMPONENT}"
            echo "WARNING: No AQM ozmax8${bctag} daily forecast was available for ${chk_date} t${hour}z" > mailmsg
            echo "Missing file is ${ozmax8_preprocessed_file}" >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $maillist
          fi
          echo "WARNING: No AQM max_8hr_o3${bctag} forecast was available for ${chk_date} t${hour}z"
          echo "WARNING: Missing file is ${ozmax8_preprocessed_file}"
        fi
      done
      echo "ozmax8, obs_daily_found=",${ozmax8},${obs_daily_found}
      if [ ${ozmax8} -gt 0 -a ${obs_daily_found} -gt 0 ]; then 
        run_metplus.py ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/PointStat_fcstOZONEMAX_obsAIRNOW.conf ${PARMevs}/metplus_config/machine.conf
	export err=$?; err_chk
        if [ ${SENDCOM} = "YES" ]; then
          cp ${DATA}/point_stat/${MODELNAME}/* ${COMOUTsmall}
        fi
        export outtyp=OZMAX8
        cp ${COMOUTsmall}/*${outtyp}${bcout}* ${finalstat}
        run_metplus.py ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstOZONEMAX_obsAIRNOW_GatherByDay.conf ${PARMevs}/metplus_config/machine.conf
	export err=$?; err_chk
	if [ ${SENDCOM} = "YES" ]; then
          cp ${finalstat}/evs.${STEP}.${COMPONENT}${bcout}.${RUN}.${VERIF_CASE}_ozmax8.v${VDATE}.stat ${COMOUTfinal}
        fi	 
      else
        echo "WARNING: NO OZMAX8 OBS OR MODEL DATA"
        echo "WARNING: OZMAX8, OBS_DAILY_FOUND", ${ozmax8}, ${obs_daily_found}
      fi
    done

  done

fi

# Daily verification of the daily average of PM2.5
# Verification is being done on both raw and bias-corrected output data

if [ ${vhr} = 04 ]; then

  fcstmax=48
  for biastyp in raw bc; do

    export biastyp
    echo ${biastyp}

    if [ ${biastyp} = "raw" ]; then
      export bctag=
      export bcout=_raw
    fi

    if [ ${biastyp} = "bc" ]; then
      export bctag=_bc
      export bcout=_bc
    fi

    for hour in 06 12; do

      export hour
      export mdl_cyc=${hour}

      ##  search for forecast daily average PM model files

      pmave1=0
      for chk_date in ${VDAYm1} ${VDAYm2} ${VDAYm3}; do
        fcst_file=${COMINaqm}/${dirname}.${chk_date}/${hour}/aqm.t${hour}z.ave_24hr_pm25${bctag}.${gridspec}.grib2
        if [ -s ${fcst_file} ]; then
          let "pmave1=pmave1+1"
        else
          if [ $SENDMAIL = "YES" ]; then
            export subject="t${hour}z PMAVE${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
            echo "WARNING: No AQM ave_24hr_pm25${bctag} forecast was available for ${chk_date} t${hour}z" > mailmsg
            echo "Missing file is $fcst_file}" >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $maillist
          fi

          echo "WARNING: No AQM ave_24hr_pm25${bctag} forecast was available for ${chk_date} t${hour}z"
          echo "WARNING: Missing file is $fcst_file}"
        fi
      done
      echo "pmave1, obs_daily_found=",${pmave1},${obs_daily_found}
      if [ ${pmave1} -gt 0 -a ${obs_daily_found} -gt 0 ]; then
        run_metplus.py ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/PointStat_fcstPMAVE_obsANOWPM.conf ${PARMevs}/metplus_config/machine.conf
	export err=$?; err_chk
        if [ ${SENDCOM} = "YES" ]; then
          cp ${DATA}/point_stat/${MODELNAME}/* ${COMOUTsmall}
        fi
        export outtyp=PMAVE
        cp ${COMOUTsmall}/*${outtyp}${bcout}* ${finalstat}
        run_metplus.py ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstPMAVE_obsANOWPM_GatherByDay.conf ${PARMevs}/metplus_config/machine.conf
	export err=$?; err_chk
	if [ ${SENDCOM} = "YES" ]; then
          cp ${finalstat}/evs.${STEP}.${COMPONENT}${bcout}.${RUN}.${VERIF_CASE}_pmave.v${VDATE}.stat ${COMOUTfinal}
	fi
       else
         echo "WARNING: NO PMAVE OBS OR MODEL DATA"
         echo "WARNING: PMAVE1, OBS_DAILY_FOUND", ${pmave1}, ${obs_daily_found}
       fi
    done

  done

fi

exit


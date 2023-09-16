#!/bin/ksh
#######################################################################
##  UNIX Script Documentation Block
##                      .
## Script name:         exevs_aqmv_grid2obs_stats.sh
## Script description:  Perform MetPlus PointStat of Air Quality Model.
## Original Author   :  Perry Shafran
##
##   Change Logs:
##
##   04/26/2023   Ho-Chun Huang  modification for using AirNOW ASCII2NC
##
##
#######################################################################
#
set -x

mkdir -p $DATA/logs
mkdir -p $DATA/stat
export finalstat=$DATA/final
mkdir -p $DATA/final

#######################################################################
# Define INPUT OBS DATA TYPE for PointStat
#######################################################################
#
if [ "${airnow_hourly_type}" == "aqobs" ]; then
    export HOURLY_INPUT_TYPE=hourly_aqobs
else
    export HOURLY_INPUT_TYPE=hourly_data
fi
## 
## Note the v6 and v7 comout directory structure are different
## Check for correct scripts called
##
    export dirname=cs
    export gridspec=148
export fcstmax=72
#
## export MASK_DIR is declared in the ~/EVS/jobs/aqm/stats/JEVS_AQM_STATS 
#
export model1=`echo $MODELNAME | tr a-z A-Z`
echo $model1

# Begin verification of both the hourly data of ozone and PM
#
# The valid time of forecast model output is the reference here in PointStat
# Because of the valid time definition between forecat output and observation is different
#     For average concentration of a period [ cyc-1 to cyc ], aqm output is defined at cyc Z
#     while observation is defined at cyc-1 Z
# Thus, the one hour back OBS input will be checked and used in PointStat
#     [OBS_POINT_STAT_INPUT_TEMPLATE=****_{valid?fmt=%Y%m%d%H?shift=-3600}.nc]
#
cdate=${VDATE}${cyc}
vld_date=$(${NDATE} -1 ${cdate} | cut -c1-8)
vld_time=$(${NDATE} -1 ${cdate} | cut -c1-10)

VDAYm1=$(${NDATE} -24 ${cdate} | cut -c1-8)
VDAYm2=$(${NDATE} -48 ${cdate} | cut -c1-8)
VDAYm3=$(${NDATE} -72 ${cdate} | cut -c1-8)

check_file=${COMINaqmproc}/${RUN}.${vld_date}/${MODELNAME}/airnow_${HOURLY_INPUT_TYPE}_${vld_time}.nc
obs_hourly_found=0
if [ -s ${check_file} ]; then
    obs_hourly_found=1
else
    echo "Can not find pre-processed obs hourly input ${check_file}"
    ## add email function here
fi
echo "obs_hourly_found = ${obs_hourly_found}"

for outtyp in awpozcon pm25
do

# Verification to be done both on raw output files and bias-corrected files

  for biastyp in raw bc
  do

    export outtyp
    export biastyp
    echo $biastyp

    if [ $biastyp = "raw" ]
    then
      export bctag=
      export bcout=_raw
    fi

    if [ $biastyp = "bc" ]
    then
      export bctag=_bc
      export bcout=_bc
    fi

# check to see that model files exist, and list which forecast hours are to be used
#
# AQMv6 does not output IC, i.e., f00.  Thus the forecast file will be chekced from f01 to f72
#
    let ihr=1
    numo3fcst=0
    numpmfcst=0
    while [ ${ihr} -le $fcstmax ]
    do
      filehr=$(printf %2.2d ${ihr})    ## fhr of grib2 filename is in 3 digit for aqmv7 and 2 digit for aqmv6
      fhr=$(printf %2.2d ${ihr})       ## fhr for the processing valid hour is in 2 digit
      export fhr

      export datehr=${VDATE}${cyc}
      adate=`$NDATE -${ihr} $datehr`
      aday=`echo $adate |cut -c1-8`
      acyc=`echo $adate |cut -c9-10`
      if [ $acyc = 06 -o $acyc = 12 ]
      then
        fcst_file=$COMINaqm/${dirname}.${aday}/aqm.t${acyc}z.awpozcon${bctag}.f${filehr}.${gridspec}.grib2
        if [ -s ${fcst_file} ]
        then
          echo "$fhr found"
          echo $fhr >> $DATA/fcstlist_o3
          let "numo3fcst=numo3fcst+1"
        else
          export subject="t${acyc}z ozone${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
          echo "Warning: No AQM awpozcon${bctag} forecast was available for ${aday} t${acyc}z" > mailmsg
          echo "Missing file is ${fcst_file}" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist

          echo "Warning: No AQM awpozcon${bctag} forecast was available for ${aday} t${acyc}z"
          echo "Missing file is ${fcst_file}"
        fi 

        fcst_file=$COMINaqm/${dirname}.${aday}/aqm.t${acyc}z.pm25${bctag}.f${filehr}.${gridspec}.grib2
        if [ -s ${fcst_file} ]
        then
          echo "$fhr found"
          echo $fhr >> $DATA/fcstlist_pm
          let "numpmfcst=numpmfcst+1"
        else
          export subject="t${acyc}z pm25${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
          echo "Warning: No AQM pm${bctag} forecast was available for ${aday} t${acyc}z" > mailmsg
          echo "Missing file is ${fcst_file}" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist

          echo "Warning: No AQM pm25${bctag} forecast was available for ${aday} t${acyc}z"
          echo "Missing file is ${fcst_file}"
        fi

      fi
      ((ihr++))
    done
    export fcsthours_o3=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/fcstlist_o3`
    export fcsthours_pm=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/fcstlist_pm`
    export numo3fcst
    export numpmfcst
    rm $DATA/fcstlist_o3 $DATA/fcstlist_pm
    echo "numo3fcst,numpmfcst", $numo3fcst, $numpmfcst

    case $outtyp in

        awpozcon) if [ $numo3fcst -gt 0 -a $obs_hourly_found -eq 1 ]
                  then
                  export fcsthours=$fcsthours_o3
                  run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstOZONE_obsAIRNOW.conf $PARMevs/metplus_config/machine.conf
                  export err=$?; err_chk
                  mkdir -p $COMOUTsmall
		  if [ $SENDCOM = "YES" ]; then
                   cp $DATA/point_stat/$MODELNAME/* $COMOUTsmall
		  fi
                  if [ $cyc = 23 ]
                  then
                    mkdir -p $COMOUTfinal
		    cp $COMOUTsmall/*${outtyp}${bcout}* $finalstat
		    cd $finalstat
                    run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstOZONE_obsAIRNOW_GatherByDay.conf $PARMevs/metplus_config/machine.conf
                    export err=$?; err_chk
		    if [ $SENDCOM = "YES" ]; then
		     cp $finalstat/evs.stats.${COMPONENT}${bcout}.${RUN}.${VERIF_CASE}_ozone.v${VDATE}.stat $COMOUTfinal
		    fi
                  fi
                  else
                  echo "NO O3 FORECAST OR OBS TO VERIFY"
                  echo "NUM FCST, NUM OBS", $numo3fcst, $obs_hourly_found
                  fi
                  ;;
      pm25) if [ $numpmfcst -gt 0 -a $obs_hourly_found -eq 1 ]
            then
            export fcsthours=$fcsthours_pm
            run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstPM2p5_obsAIRNOW.conf $PARMevs/metplus_config/machine.conf
            export err=$?; err_chk
            mkdir -p $COMOUTsmall
	    if [ $SENDCOM = "YES" ]; then
             cp $DATA/point_stat/$MODELNAME/* $COMOUTsmall
	    fi
            if [ $cyc = 23 ]
            then
               mkdir -p $COMOUTfinal
	       cp $COMOUTsmall/*${outtyp}${bcout}* $finalstat
               run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstPM_obsANOWPM_GatherByDay.conf $PARMevs/metplus_config/machine.conf
               export err=$?; err_chk
	       if [ $SENDCOM = "YES" ]; then
		cp $finalstat/evs.stats.${COMPONENT}${bcout}.${RUN}.${VERIF_CASE}_pm25.v${VDATE}.stat $COMOUTfinal
	       fi
            fi
            else
            echo "NO PM FORECAST OR OBS TO VERIFY"
            echo "NUM FCST, NUM OBS", $numpmfcst, $obs_hourly_found
            fi
            ;;
    esac

  done

done
# Daily verification of the daily maximum of 8-hr ozone
# Verification being done on both raw and bias-corrected output data

check_file=${COMINaqmproc}/${RUN}.${VDATE}/${MODELNAME}/airnow_daily_${VDATE}.nc
obs_daily_found=0
if [ -s ${check_file} ]; then
    obs_daily_found=1
else
    echo "Can not find pre-processed obs daily input ${check_file}"
    ## add email function here
fi
echo "obs_daily_found = ${obs_daily_found}"


if [ $cyc = 11 ]
then
   
  fcstmax=48

  for biastyp in raw bc
  do

    export biastyp
    echo $biastyp

    if [ $biastyp = "raw" ]
    then
      export bctag=
      export bcout=_raw
    fi

    if [ $biastyp = "bc" ]
    then
      export bctag=_bc
      export bcout=_bc
    fi

    for hour in 06 12
    do

      export hour

#  search for model file and 2nd obs file for the daily 8-hr ozone max

      ozmax8=0
      ozmax8_preprocessed_file=$COMINaqmproc/atmos.${VDAYm1}/aqm/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2
      if [ -s ${ozmax8_preprocessed_file} ]
      then
        ozmax8=1
      else
        ## This is checking output from the PREP step, thus no email will be sent but for logile meaasge
        echo "Warning: No AQM max_8hr_o3${bctag} forecast was available for ${VDAYm1} t${hour}z"
        echo "Missing file is ${ozmax8_preprocessed_file}"
      fi
      ozmax8_preprocessed_file=$COMINaqmproc/atmos.${VDAYm2}/aqm/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2
      if [ -s ${ozmax8_preprocessed_file} ]
      then
       let "ozmax8=ozmax8+1"
      else
        ## This is checking output from the PREP step, thus no email will be sent but for logile meaasge
        echo "Warning: No AQM max_8hr_o3${bctag} forecast was available for ${VDAYm2} t${hour}z"
        echo "Missing file is ${ozmax8_preprocessed_file}"
      fi
      ozmax8_preprocessed_file=$COMINaqmproc/atmos.${VDAYm3}/aqm/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2
      if [ -s ${ozmax8_preprocessed_file} ]
      then
        let "ozmax8=ozmax8+1"
      else
        ## This is checking output from the PREP step, thus no email will be sent but for logile meaasge
        echo "Warning: No AQM max_8hr_o3${bctag} forecast was available for ${VDAYm3} t${hour}z"
        echo "Missing file is ${ozmax8_preprocessed_file}"
      fi
      echo "ozmax8, obs_daily_found=",$ozmax8,$obs_daily_found
      if [ $ozmax8 -gt 0 -a $obs_daily_found -gt 0 ]
      then 
        run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstOZONEMAX_obsAIRNOW.conf $PARMevs/metplus_config/machine.conf
	export err=$?; err_chk
	if [ $SENDCOM = "YES" ]; then
         cp $DATA/point_stat/$MODELNAME/* $COMOUTsmall
	fi
        export outtyp=OZMAX8
	cp $COMOUTsmall/*${outtyp}${bcout}* $finalstat
        run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstOZONEMAX_obsAIRNOW_GatherByDay.conf $PARMevs/metplus_config/machine.conf
	export err=$?; err_chk
	if [ $SENDCOM = "YES" ]; then
         cp $finalstat/evs.stats.${COMPONENT}${bcout}.${RUN}.${VERIF_CASE}_ozmax8.v${VDATE}.stat $COMOUTfinal
        fi	 
       else
         echo "NO OZMAX8 OBS OR MODEL DATA"
         echo "OZMAX8, OBS_DAILY_FOUND", $ozmax8, $obs_daily_found
       fi
    done

  done

fi

# Daily verification of the daily average of PM2.5
# Verification is being done on both raw and bias-corrected output data

if [ $cyc = 04 ]
then
  fcstmax=48

  for biastyp in raw bc
  do

    export biastyp
    echo $biastyp

    if [ $biastyp = "raw" ]
    then
      export bctag=
      export bcout=_raw
    fi

    if [ $biastyp = "bc" ]
    then
      export bctag=_bc
      export bcout=_bc
    fi

    for hour in 06 12
    do

      export hour

#  search for model file and 2nd obs file for the daily average PM

      pmave1=0
      fcst_file=$COMINaqm/${dirname}.${VDAYm1}/aqm.t${hour}z.ave_24hr_pm25${bctag}.${gridspec}.grib2
      if [ -s ${fcst_file} ]
      then
        pmave1=1
      else
        export subject="t${hour}z PMAVE${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
        echo "Warning: No AQM ave_24hr_pm25${bctag} forecast was available for ${VDAYm1} t${hour}z" > mailmsg
        echo "Missing file is $fcst_file}" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist

        echo "Warning: No AQM ave_24hr_pm25${bctag} forecast was available for ${VDAYm1} t${hour}z"
        echo "Missing file is $fcst_file}"
      fi
      fcst_file=$COMINaqm/${dirname}.${VDAYm2}/aqm.t${hour}z.ave_24hr_pm25${bctag}.${gridspec}.grib2
      if [ -s ${fcst_file} ]
      then
       let "pmave1=pmave1+1" 
      else
        export subject="t${hour}z PMAVE${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
        echo "Warning: No AQM ave_24hr_pm25${bctag} forecast was available for ${VDAYm2} t${hour}z" > mailmsg
        echo "Missing file is $fcst_file}" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist

        echo "Warning: No AQM ave_24hr_pm25${bctag} forecast was available for ${VDAYm2} t${hour}z"
        echo "Missing file is $fcst_file}"
      fi
      fcst_file=$COMINaqm/${dirname}.${VDAYm3}/aqm.t${hour}z.ave_24hr_pm25${bctag}.${gridspec}.grib2
      if [ -s ${fcst_file} ]
      then
        let "pmave1=pmave1+1"
      else
        export subject="t${hour}z PMAVE${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
        echo "Warning: No AQM ave_24hr_pm25${bctag} forecast was available for ${VDAYm3} t${hour}z" > mailmsg
        echo "Missing file is $fcst_file}" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist

        echo "Warning: No AQM ave_24hr_pm25${bctag} forecast was available for ${VDAYm3} t${hour}z"
        echo "Missing file is $fcst_file}"
      fi
      echo "pmave1, obs_daily_found=",$pmave1,$obs_daily_found
      if [ $pmave1 -gt 0 -a $obs_daily_found -gt 0 ]
      then
        run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstPMAVE_obsANOWPM.conf $PARMevs/metplus_config/machine.conf
	export err=$?; err_chk
	if [ $SENDCOM = "YES" ]; then
         cp $DATA/point_stat/$MODELNAME/* $COMOUTsmall
	fi
        export outtyp=PMAVE
	cp $COMOUTsmall/*${outtyp}${bcout}* $finalstat
        run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstPMAVE_obsANOWPM_GatherByDay.conf $PARMevs/metplus_config/machine.conf
	export err=$?; err_chk
	if [ $SENDCOM = "YES" ]; then
        	cp $finalstat/evs.stats.${COMPONENT}${bcout}.${RUN}.${VERIF_CASE}_pmave.v${VDATE}.stat $COMOUTfinal
	fi
       else
         echo "NO PMAVE OBS OR MODEL DATA"
         echo "PMAVE1, OBS_DAILY_FOUND", $pmave1, $obs_daily_found
       fi
    done

  done

fi

exit


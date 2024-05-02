#!/bin/bash
#######################################################################
##  UNIX Script Documentation Block
##                      .
## Script name:         exevs_aqm_prep.sh
## Script description:  Pre-processed input data for the MetPlus PointStat 
##                      of Air Quality Model.
## Original Author   :  Perry Shafran
##
##   Change Logs:
##
##   04/26/2023   Ho-Chun Huang  add AirNOW ASCII2NC processing
##   05/01/2023   Ho-Chun Huang  separate v6 and v7 version becasuse
##                               of directory path difference
##   10/31/2023   Ho-Chun Huang  Update EVS model input directory
##                               structure from AQMv6 to AQMv7
##   11/14/2023   Ho-Chun Huang  Replace cp with cpreq
##   01/05/2024   Ho-Chun Huang  modify for AQMv6 verification
##   02/02/2024   Ho-Chun Huang  Replace cpreq with cp to copy file from DATA to COMOUT
##   02/21/2024   Ho-Chun Huang  modify for AQMv7 verification
##
##
#######################################################################
#
set -x

export config=$PARMevs/evs_config/$COMPONENT/config.evs.aqm.prod
source $config

#######################################################################
# Define INPUT OBS DATA TYPE for ASCII2NC 
#######################################################################
#
if [ "${airnow_hourly_type}" == "aqobs" ]; then
    export HOURLY_INPUT_TYPE=HourlyAQObs
    export HOURLY_OUTPUT_TYPE=hourly_aqobs
    export HOURLY_ASCII2NC_FORMAT=airnowhourlyaqobs
else
    export HOURLY_INPUT_TYPE=HourlyData
    export HOURLY_OUTPUT_TYPE=hourly_data
    export HOURLY_ASCII2NC_FORMAT=airnowhourly
fi
 
export dirname=aqm
export gridspec=793

export PREP_SAVE_DIR=${DATA}/prepsave
mkdir -p ${PREP_SAVE_DIR}


export model1=`echo $MODELNAME | tr a-z A-Z`
echo $model1

## Pre-Processed EPA AIRNOW ASCII input file to METPlus NetCDF input for PointStat
##
## Hourly AirNOW observation
##
let ic=0
let endvhr=23
conf_dir=${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}
while [ ${ic} -le ${endvhr} ]; do
    vldhr=$(printf %2.2d ${ic})
    checkfile=${DCOMIN}/${VDATE}/airnow/${HOURLY_INPUT_TYPE}_${VDATE}${vldhr}.dat
    if [ -s ${checkfile} ]; then
        export VHOUR=${vldhr}
	if [ -s ${conf_dir}/Ascii2Nc_hourly_obsAIRNOW.conf ]; then
            run_metplus.py ${conf_dir}/Ascii2Nc_hourly_obsAIRNOW.conf ${PARMevs}/metplus_config/machine.conf
	    export err=$?; err_chk
	    if [ ${SENDCOM} = "YES" ]; then
                cpfile=${PREP_SAVE_DIR}/airnow_hourly_aqobs_${VDATE}${VHOUR}.nc 
                if [ -s ${cpfile} ]; then cp -v ${cpfile} ${COMOUTproc}; fi
	    fi
        else
            echo "WARNING: can not find ${conf_dir}/Ascii2Nc_hourly_obsAIRNOW.conf"
	fi
    else
        if [ ${SENDMAIL} = "YES" ]; then
            export subject="AIRNOW ASCII Hourly Data Missing for EVS ${COMPONENT}"
            echo "WARNING: No AIRNOW ASCII data was available for valid date ${VDATE}${vldhr}" > mailmsg
            echo "Missing file is ${checkfile}" >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO 
        fi

        echo "WARNING: No AIRNOW ASCII data was available for valid date ${VDATE}${vldhr}"
        echo "WARNING: Missing file is ${checkfile}"
    fi
    ((ic++))
done
##
## Daily (MAX/AVG) AirNOW observation
##
checkfile=${DCOMIN}/${VDATE}/airnow/daily_data_v2.dat
if [ -s ${checkfile} ]; then
    if [ -s ${conf_dir}/Ascii2Nc_daily_obsAIRNOW.conf ]; then
        run_metplus.py ${conf_dir}/Ascii2Nc_daily_obsAIRNOW.conf ${PARMevs}/metplus_config/machine.conf
        export err=$?; err_chk
	if [ ${SENDCOM} = "YES" ]; then
            cpfile=${PREP_SAVE_DIR}/airnow_daily_${VDATE}.nc
            if [ -s ${cpfile} ]; then cp -v ${cpfile} ${COMOUTproc};fi
	fi
    else
        echo "WARNING: can not find ${conf_dir}/Ascii2Nc_daily_obsAIRNOW.conf"
    fi
else
    if [ ${SENDMAIL} = "YES" ]; then
        export subject="AIRNOW ASCII Daily Data Missing for EVS ${COMPONENT}"
        echo "WARNING: No AIRNOW ASCII data was available for valid date ${VDATE}" > mailmsg
        echo "Missing file is ${checkfile}" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO 
    fi

    echo "WARNING: No AIRNOW ASCII data was available for valid date ${VDATE}"
    echo "WARNING: Missing file is ${checkfile}"
fi
#
##
## Pre-Processed Daily Max 8HR-AVG ozone to have a consistent averaging period
##
mkdir -p $DATA/modelinput
cd $DATA/modelinput

## mkdir -p $COMOUT.${VDATE}/${MODELNAME}

for hour in 06 12; do

    for biastyp in raw bc; do

        export biastyp
        echo $biastyp

        if [ $biastyp = "raw" ]; then
            export bctag=
        elif [ $biastyp = "bc" ]; then
            export bctag=_bc
        fi

        if [ $hour -eq 06 ]; then
            ozmax8_file=${COMINaqm}/${dirname}.${VDATE}/${hour}/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2
            if [ -s ${ozmax8_file} ]; then
                wgrib2 -d 1 ${ozmax8_file} -set_ftime "6-29 hour ave fcst"  -grib out1.grb2
                wgrib2 -d 2 ${ozmax8_file} -set_ftime "30-53 hour ave fcst" -grib out2.grb2
                wgrib2 -d 3 ${ozmax8_file} -set_ftime "54-77 hour ave fcst" -grib out3.grb2
		comout_file=aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2
                cat out1.grb2 out2.grb2 out3.grb2 > ${comout_file}
        	if [ ${SENDCOM} = "YES" ]; then
                    if [ -s ${comout_file} ]; then cp -v ${comout_file} ${COMOUTproc}; fi
        	fi
            else
                if [ ${SENDMAIL} = "YES" ]; then
                    export subject="t${hour}z OZMAX8${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
                    echo "WARNING: No AQM OZMAX8${bctag} forecast was available for ${VDATE} t${hour}z" > mailmsg
                    echo "Missing file is ${ozmax8_file}" >> mailmsg
                    echo "Job ID: $jobid" >> mailmsg
                    cat mailmsg | mail -s "$subject" $MAILTO
                fi
        
                echo "WARNING: No AQM OZMAX8${bctag} forecast was available for ${VDATE} t${hour}z"
                echo "WARNING: Missing file is ${ozmax8_file}"
            fi
        fi
        
        
        if [ $hour -eq 12 ]; then
            ozmax8_file=${COMINaqm}/${dirname}.${VDATE}/${hour}/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2
            if [ -s ${ozmax8_file} ]; then
                wgrib2 -d 1 ${ozmax8_file} -set_ftime "0-23 hour ave fcst" -grib out1.grb2
                wgrib2 -d 2 ${ozmax8_file} -set_ftime "24-47 hour ave fcst" -grib out2.grb2
                wgrib2 -d 3 ${ozmax8_file} -set_ftime "48-71 hour ave fcst" -grib out3.grb2
		comout_file=aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2
                cat out1.grb2 out2.grb2 out3.grb2 > ${comout_file}
        	if [ ${SENDCOM} = "YES" ]; then
                    if [ -s ${comout_file} ]; then cp -v ${comout_file} ${COMOUTproc}; fi
        	fi
            else
                if [ ${SENDMAIL} = "YES" ]; then
                    export subject="t${hour}z OZMAX8${bctag} AQM Forecast Data Missing for EVS ${COMPONENT}"
                    echo "WARNING: No AQM OZMAX8${bctag} forecast was available for ${VDATE} t${hour}z" > mailmsg
                    echo "Missing file is ${ozmax8_file}" >> mailmsg
                    echo "Job ID: $jobid" >> mailmsg
                    cat mailmsg | mail -s "$subject" $MAILTO
                fi
        
                echo "WARNING: No AQM OZMAX8${bctag} forecast was available for ${VDATE} t${hour}z"
                echo "WARNING: Missing file is ${ozmax8_file}"
            fi
        fi
    done
done
log_dir="$DATA/logs/${model1}"
if [ -d $log_dir ]; then
    log_file_count=$(find $log_dir -type f | wc -l)
    if [[ $log_file_count -ne 0 ]]; then
       log_files=("$log_dir"/*)
       for log_file in "${log_files[@]}"; do
          if [ -f "$log_file" ]; then
             echo "Start: $log_file"
             cat "$log_file"
             echo "End: $log_file"
          fi
      done
  fi
fi
exit


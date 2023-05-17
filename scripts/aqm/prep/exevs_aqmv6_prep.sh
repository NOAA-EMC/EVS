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
##
##
#######################################################################
#
set -x

#######################################################################
# Define INPUT OBS DATA TYPE for ASCII2NC 
#######################################################################
#
hourly_type=aqobs
if [ "${hourly_type}" == "aqobs" ]; then
    export HOURLY_INPUT_TYPE=HourlyAQObs
    export HOURLY_OUTPUT_TYPE=hourly_aqobs
    export HOURLY_ASCII2NC_FORMAT=airnowhourlyaqobs
else
    export HOURLY_INPUT_TYPE=HourlyData
    export HOURLY_OUTPUT_TYPE=hourly_data
    export HOURLY_ASCII2NC_FORMAT=airnowhourly
fi
#
export PREP_SAVE_DIR=${COMOUT}/${RUN}.${VDATE}/${MODELNAME}
export dirname=cs
export gridspec=148

export model1=`echo $MODELNAME | tr a-z A-Z`
echo $model1

## Pre-Processed EPA AIRNOW ASCII input file to METPlus NetCDF input for PointStat
##
## Hourly AirNOW observation
##
let ic=0
let endvhr=23
conf_dir=$PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}
while [ ${ic} -le ${endvhr} ]; do
    vldhr=$(printf %2.2d ${ic})
    checkfile=${COMINobs}/${VDATE}/airnow/${HOURLY_INPUT_TYPE}_${VDATE}${vldhr}.dat
    if [ -s ${checkfile} ]; then
        export VHOUR=${vldhr}
	if [ -s ${conf_dir}/Ascii2Nc_hourly_obsAIRNOW.conf ]; then
            run_metplus.py ${conf_dir}/Ascii2Nc_hourly_obsAIRNOW.conf $PARMevs/metplus_config/machine.conf
        else
            echo "can not find ${conf_dir}/Ascii2Nc_hourly_obsAIRNOW.conf"
	fi
    else
	## add email function
        echo "can not find ${checkfile}"
    fi
    ((ic++))
done
##
## Daily (MAX/AVG) AirNOW observation
##
checkfile=${COMINobs}/${VDATE}/airnow/daily_data_v2.dat
if [ -s ${checkfile} ]; then
    if [ -s ${conf_dir}/Ascii2Nc_daily_obsAIRNOW.conf ]; then
        run_metplus.py ${conf_dir}/Ascii2Nc_daily_obsAIRNOW.conf $PARMevs/metplus_config/machine.conf
    else
        echo "can not find ${conf_dir}/Ascii2Nc_daily_obsAIRNOW.conf"
    fi
else
    ## add email function
    echo "can not find ${checkfile}"
fi
#
##
## Pre-Processed Daily Max 8HR-AVG ozone to have a consistent averaging period
##
mkdir -p $DATA/modelinput
cd $DATA/modelinput

mkdir -p $COMOUT.${VDATE}/${MODELNAME}

for hour in 06 12
do

for biastyp in raw bc
do

export biastyp
echo $biastyp

if [ $biastyp = "raw" ]
then
export bctag=
fi

if [ $biastyp = "bc" ]
then
export bctag=_bc
fi


if [ $hour -eq 06 ]
then
wgrib2 -d 1 $COMINaqm/${dirname}.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2 -set_ftime "6-29 hour ave fcst"  -grib out1.grb2
wgrib2 -d 2 $COMINaqm/${dirname}.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2 -set_ftime "30-53 hour ave fcst" -grib out2.grb2
wgrib2 -d 3 $COMINaqm/${dirname}.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2 -set_ftime "54-77 hour ave fcst" -grib out3.grb2
cat out1.grb2 out2.grb2 out3.grb2 > ${PREP_SAVE_DIR}/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2
fi


if [ $hour -eq 12 ]
then
wgrib2 -d 1 $COMINaqm/${dirname}.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2 -set_ftime "0-23 hour ave fcst" -grib out1.grb2
wgrib2 -d 2 $COMINaqm/${dirname}.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2 -set_ftime "24-47 hour ave fcst" -grib out2.grb2
wgrib2 -d 3 $COMINaqm/${dirname}.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2 -set_ftime "48-71 hour ave fcst" -grib out3.grb2
cat out1.grb2 out2.grb2 out3.grb2 > ${PREP_SAVE_DIR}/aqm.t${hour}z.max_8hr_o3${bctag}.${gridspec}.grib2
fi

done
done

exit


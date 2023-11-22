#!/bin/ksh
#************************************************************************************************************
# Purpose: Dynamically create NAEFS member files based on prep bias_corrected GEFS APCP member files
#          for NAEFS precip verification and save them in $WORK/naefs_precip sub-directory
#
# Last update: 11/16/2023, by Binbin Zhou Lynker@EMC/NCEP
#
#************************************************************************************************************
set -x

fhrs="24 36 48 60 72 84 96 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384" 

mkdir -p $WORK/naefs_precip
cd $WORK/naefs_precip

if [ $gefs_number = 20 ] ; then
  gefs_mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20"
elif [ $gefs_number = 30 ] ; then
  gefs_mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30"
fi
cmce_mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20"

#*********************************************
# For 24h APCP verification
#********************************************
for vhour in 00 12 ; do   

 for lead in $fhrs ; do
   obsv_time=${vday}${vhour}     #validation time: xxxx.tvhourz.f00
   fcst_time=`$NDATE -$lead $obsv_time`
   fyyyymmdd=${fcst_time:0:8}
   ihour=${fcst_time:8:2}
   fhr=$lead
   typeset -Z3 fhr

   for mbr in $gefs_mbrs ; do
       #******************************************************************
       #GEFS bias-corrected precip has 24h APCP, so directly use them:
       #******************************************************************
       if [ -s ${EVSIN}.${fyyyymmdd}/gefs_bc/gefs_bc.ens${mbr}.t${ihour}z.grid3.24h.f${fhr}.grib2 ]; then 
         ln -sf  ${EVSIN}.${fyyyymmdd}/gefs_bc/gefs_bc.ens${mbr}.t${ihour}z.grid3.24h.f${fhr}.grib2  naefs.ens${mbr}.${fyyyymmdd}.t${ihour}z.grid3.24h.f${fhr}.grib2
       fi
   done #gefs_mbrs
    
   #*****************************************************************************************
   # Note: Since CMCE has no bias-corrected precip,  NAEFS precip verification is actually 
   #       verifying the GEFS bias-corrected precip forecasts
   #*****************************************************************************************
  
 done #fhrs

done #vhours

cd $WORK

#!/bin/ksh

set -x


fhrs="24 36 48 60 72 84 96 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384" 

mkdir -p $WORK/naefs_precip

 cd $WORK/naefs_precip

for vcyc in 00 12 ; do   #for 6h APCP  verification
#for vcyc in  12 ; do      #for 24h APCP verification, only validate at 12Z

 for lead in $fhrs ; do
   obsv_cyc=${vday}${vcyc}     #validation time: xxxx.tvcycz.f00
   fcst_time=`$NDATE -$lead $obsv_cyc`
   fyyyymmdd=${fcst_time:0:8}
   fcyc=${fcst_time:8:2}
  
   fhr=$lead
   typeset -Z3 fhr

   if [ $gefs_number = 20 ] ; then
        mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20"
   elif [ $gefs_number = 30 ] ; then
        mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30"
   fi


   for mbr in $mbrs ; do

     #if [ $vcyc = 12 ] ; then 

       #ln -sf  ${EVSIN}.${fyyyymmdd}/gefs/gefs.ens${mbr}.t${fcyc}z.grid3.24h.f${fhr}.nc  naefs.ens${mbr}.${fyyyymmdd}.t${fcyc}z.grid3.24h.f${fhr}.nc
       #GEFS bias-corrected precip has 24h APCP, so directly use them:  
       ln -sf  ${EVSIN}.${fyyyymmdd}/gefs_bc/gefs_bc.ens${mbr}.t${fcyc}z.grid3.24h.f${fhr}.grib2  naefs.ens${mbr}.${fyyyymmdd}.t${fcyc}z.grid3.24h.f${fhr}.grib2

     #fi 

   done

# CMCE has no bias-corrected precip 
#   for mb in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 ; do 
#     mbr=$mb
#     typeset -Z2 mbr
#     mbr40=$((mb+30))
#     if [ $vcyc = 12 ] ; then
#       ln -sf  ${EVSIN}.${fyyyymmdd}/cmce/cmce.ens${mbr}.t${fcyc}z.grid3.24h.f${fhr}.nc  naefs.ens${mbr40}.${fyyyymmdd}.t${fcyc}z.grid3.24h.f${fhr}.nc
#
#     fi
#   done

  
 done
done

cd $WORK



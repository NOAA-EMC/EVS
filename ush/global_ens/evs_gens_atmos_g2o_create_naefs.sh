#!/bin/ksh

#Note: For grid2obs verification, adjustment of CMCE is not required like it is in grid2grid.
#      So for grid2obs, just re-name (softlink)  gefs members and cmce members to be naefs members 

set -x


fhrs="00 12 24 36 48 60 72 84 96 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384" 

mkdir -p $WORK/naefs_g2o

 cd $WORK/naefs_g2o

for vhour in 00 12 ; do 

 for lead in $fhrs ; do
   obsv_time=${vday}${vhour}     #validation time: xxxx.tvhourz.f00
   fcst_time=`$NDATE -$lead $obsv_time`
   fyyyymmdd=${fcst_time:0:8}
   ihour=${fcst_time:8:2}
  
   fhr=$lead
   typeset -Z3 fhr

   if [ $gefs_number = 20 ] ; then
     mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20"
   elif [ $gefs_number = 30 ] ; then
     mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30"
   fi 

   for mbr in $mbrs ; do
     ln -sf  ${EVSIN}.${fyyyymmdd}/gefs_bc/gefs_bc.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2  naefs.ens${mbr}.${fyyyymmdd}.t${ihour}z.grid3.f${fhr}.grib2
   done

   for mb in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 ; do 
     mbr=$mb
     typeset -Z2 mbr
     if [ $gefs_number = 20 ] ; then
       mbr40=$((mb+20))
     elif [ $gefs_number = 30 ] ; then
       mbr40=$((mb+30))
     fi

     ln -sf  ${EVSIN}.${fyyyymmdd}/cmce_bc/cmce_bc.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2  naefs.ens${mbr40}.${fyyyymmdd}.t${ihour}z.grid3.f${fhr}.grib2
   done

  
 done
done

cd $WORK



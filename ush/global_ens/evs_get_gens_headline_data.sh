#!/bin/ksh

set -x

cd $EVSINcmce
cmcanl=cmcanl.t00z.grid3.f000.grib2
$WGRIB2  $cmcanl|grep "HGT:500 mb"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $COMOUTcmce/cmcanl.t00z.grid3.f000.grib2

cd $EVSINcmce_bc
for hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do
  for mbr in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do
    cmce=cmce_bc.ens${mbr}.t00z.grid3.f${hhh}.grib2
    $WGRIB2  $cmce|grep "HGT:500 mb"|$WGRIB2 -i $cmce -grib $COMOUTcmce/cmce.ens${mbr}.t00z.grid3.f${hhh}.grib2
  done
done

cd $EVSINgefs
gfsanl=gfsanl.t00z.grid3.f000.grib2
$WGRIB2  $gfsanl|grep "HGT:500 mb"|$WGRIB2 -i $gfsanl -grib $COMOUTgefs/gfsanl.t00z.grid3.f000.grib2

cd $EVSINgefs_bc

if [ $gefs_number = 30 ] ; then
  mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30"
elif [ $gefs_number = 20 ] ; then
  mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20"
fi 

for hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do
  for mbr in $mbrs ; do
      gefs=gefs_bc.ens${mbr}.t00z.grid3.f${hhh}.grib2
      $WGRIB2  $gefs|grep "HGT:500 mb"|$WGRIB2 -i $gefs -grib $COMOUTgefs/gefs.ens${mbr}.t00z.grid3.f${hhh}.grib2
  done
done

cd $EVSINgefs
for hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do
   cp gfs.t00z.grid3.f${hhh}.grib2 $COMOUTgefs/.
done

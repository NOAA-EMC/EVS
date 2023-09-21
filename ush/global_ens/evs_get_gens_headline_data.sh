#!/bin/ksh

set -x

cd $COMIN_cmce
cmcanl=cmcanl.t00z.grid3.f000.grib2
$WGRIB2  $cmcanl|grep "HGT:500 mb"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $COMOUT_cmce/cmcanl.t00z.grid3.f000.grib2

cd $COMIN_cmce_bc
for hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do
  for mbr in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do
    cmce=cmce_bc.ens${mbr}.t00z.grid3.f${hhh}.grib2
    $WGRIB2  $cmce|grep "HGT:500 mb"|$WGRIB2 -i $cmce -grib $COMOUT_cmce/cmce.ens${mbr}.t00z.grid3.f${hhh}.grib2
  done
done

cd $COMIN_gefs
gfsanl=gfsanl.t00z.grid3.f000.grib2
$WGRIB2  $gfsanl|grep "HGT:500 mb"|$WGRIB2 -i $gfsanl -grib $COMOUT_gefs/gfsanl.t00z.grid3.f000.grib2

cd $COMIN_gefs_bc

if [ $gefs_number = 30 ] ; then
  mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30"
elif [ $gefs_number = 20 ] ; then
  mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20"
fi 

for hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do
  for mbr in $mbrs ; do
      gefs=gefs_bc.ens${mbr}.t00z.grid3.f${hhh}.grib2
      $WGRIB2  $gefs|grep "HGT:500 mb"|$WGRIB2 -i $gefs -grib $COMOUT_gefs/gefs.ens${mbr}.t00z.grid3.f${hhh}.grib2
  done
done

cd $COMIN_gefs
for hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do
  [[ $SENDCOM="YES" ]] && cp gfs.t00z.grid3.f${hhh}.grib2 $COMOUT_gefs/.
done

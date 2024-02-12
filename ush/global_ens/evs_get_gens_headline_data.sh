#!/bin/ksh
#**************************************************************************************
# Purpose:    1. Further retrieve 500hPa Height from GEFS and CMCE analysis 
#                (in prep/atmos.YYYYMMDD/gefs and cmce) and bias-corrected GEFS and CMCE  
#                 member files (in prep/atmos.YYYYMMDD/gefs_bc cmce_bc) to 
#                 form even smaller grib2 files
#             2. Stored the even smaller grib files in prep/global_ens/headline.YYYYMMDD
#
# Last updated 11/15/2023: by  Binbin Zhou, Lynker@EMC/NCEP
#******************************************************************************************

set -x

cmcanl=$EVSINcmce/cmcanl.t00z.grid3.f000.grib2
if [ -s $cmcanl ]; then
  $WGRIB2  $cmcanl|grep "HGT:500 mb"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/cmcanl.t00z.grid3.f000.grib2
  if [ $SENDCOM="YES" ] ; then
      if [ -s $WORK/cmcanl.t00z.grid3.f000.grib2 ]; then
          cp -v $WORK/cmcanl.t00z.grid3.f000.grib2 $COMOUTcmce/cmcanl.t00z.grid3.f000.grib2
      fi
  fi
else
  echo "WARNING: $cmcanl does not exist"
fi

for hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do
  for mbr in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do
    cmce=$EVSINcmce_bc/cmce_bc.ens${mbr}.t00z.grid3.f${hhh}.grib2
    if [ -s $cmce ]; then
      $WGRIB2  $cmce|grep "HGT:500 mb"|$WGRIB2 -i $cmce -grib $WORK/cmce.ens${mbr}.t00z.grid3.f${hhh}.grib2
      if [ $SENDCOM="YES" ] ; then
          if [ -s $WORK/cmce.ens${mbr}.t00z.grid3.f${hhh}.grib2 ]; then
              cp -v $WORK/cmce.ens${mbr}.t00z.grid3.f${hhh}.grib2 $COMOUTcmce/cmce.ens${mbr}.t00z.grid3.f${hhh}.grib2
          fi
      fi
    else
      echo "WARNING: $cmce does not exist"
    fi
  done
done

gfsanl=$EVSINgefs/gfsanl.t00z.grid3.f000.grib2
if [ -s $gfsanl ]; then
  $WGRIB2  $gfsanl|grep "HGT:500 mb"|$WGRIB2 -i $gfsanl -grib $WORK/gfsanl.t00z.grid3.f000.grib2
  if [ $SENDCOM="YES" ] ; then
      if [ -s $WORK/gfsanl.t00z.grid3.f000.grib2 ]; then 
          cp -v $WORK/gfsanl.t00z.grid3.f000.grib2 $COMOUTgefs/gfsanl.t00z.grid3.f000.grib2
      fi
  fi
else
  echo "WARNING: $gfsanl does not exist"
fi

if [ $gefs_number = 30 ] ; then
  mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30"
elif [ $gefs_number = 20 ] ; then
  mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20"
fi 
for hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do
  for mbr in $mbrs ; do
      gefs=$EVSINgefs_bc/gefs_bc.ens${mbr}.t00z.grid3.f${hhh}.grib2
      if [ -s $gefs ]; then
        $WGRIB2  $gefs|grep "HGT:500 mb"|$WGRIB2 -i $gefs -grib $WORK/gefs.ens${mbr}.t00z.grid3.f${hhh}.grib2
        if [ $SENDCOM="YES" ] ; then
            if [ -s $WORK/gefs.ens${mbr}.t00z.grid3.f${hhh}.grib2 ]; then
                cp -v $WORK/gefs.ens${mbr}.t00z.grid3.f${hhh}.grib2 $COMOUTgefs/gefs.ens${mbr}.t00z.grid3.f${hhh}.grib2
            fi
        fi
      else
        echo "WARNING: $gefs does not exist"
      fi
  done
done

for hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do
   if [ -s $EVSINgefs/gfs.t00z.grid3.f${hhh}.grib2 ]; then
     cpreq -v $EVSINgefs/gfs.t00z.grid3.f${hhh}.grib2 $WORK/gfs.t00z.grid3.f${hhh}.grib2
     if [ $SENDCOM="YES" ] ; then
         if [ -s $WORK/gfs.t00z.grid3.f${hhh}.grib2 ]; then
             cp -v $WORK/gfs.t00z.grid3.f${hhh}.grib2 $COMOUTgefs/gfs.t00z.grid3.f${hhh}.grib2
         fi
     fi
   else
     echo "WARNING: $EVSINgefs/gfs.t00z.grid3.f${hhh}.grib2 does not exist"
   fi
done

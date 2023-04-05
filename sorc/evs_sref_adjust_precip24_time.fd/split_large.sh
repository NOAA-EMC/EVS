#!/bin/ksh

vday=20230221

COMINsref=/lfs/h1/ops/prod/com/sref/v7.1

for cyc in 09 15 ; do
  large=$COMINsref/sref.${vday}/${cyc}/ensprod/sref.t${cyc}z.pgrb212.mean_3hrly.grib2
  fhr=3
  while [ $fhr -le 87 ] ; do
    fhr_3=$((fhr-3))
    string="APCP:surface:${fhr_3}-${fhr} hour"
    hh=$fhr
    typeset -Z2 hh
    $WGRIB2 $large|grep "$string"|$WGRIB2 -i $large -grib sref.t${cyc}z.pgrb212.mean.fhr${hh}.grib2
    fhr=$((fhr+3))
  done
done


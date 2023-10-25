#!/bin/ksh

set -x


typeset -Z2 vhr

vhr=00
missing=0 
while [ $vhr -le 23 ] ; do 
  if [ ! -s $COMINobsproc/rap.${vday}/rap.t${vhr}z.prepbufr.tm00.nr ] ; then
    missing=$((missing + 1 ))
  fi
  vhr=$((vhr+1))
done

echo "Missing prepbufr files = " $missing
if [ $missing -eq 24  ] ; then
  echo "all of the preppbufr files are missing, exit execution!!!"
  exit
else
  echo "Continue check NARRE mean files...." 
fi

typeset -Z2 fvhr

for grid in 130 242 ; do 
 for vhr in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 ; do 

  has_narre=0
  obsv_vhr=${vday}${vhr}

  for fhr in 01 02 03 04 05 06 07 08 09 10 11 12 ; do

    fcst_time=`$NDATE -$fhr $obsv_vhr`
    fday=${fcst_time:0:8}
    fvhr=${fcst_time:8:2}

    narre_mean=$COMINnarre/narre.${fday}/ensprod/narre.t${fvhr}z.mean.grd${grid}.f${fhr}.grib2
    if [ -s $narre_mean ] ; then
       has_narre=$((has_narre+1))
    fi	      
  done

  echo "For vhr" $vhr " and  grid" $grid " has_narre = " $has_narre

  if [ $has_narre -eq 0 ] ; then
     echo "All narre files are missing for vhr " $vhr "  exit execution !!!"
     exit
  fi

 done
done

echo "COntinue run METplus ..." 



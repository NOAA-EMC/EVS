#!/bin/ksh

set +x

#vday=20221003
#COMINobs=/lfs/h1/ops/prod/com/obsproc/v1.0
#COMINnarre=/lfs/h1/ops/prod/com/narre/v1.2

typeset -Z2 cyc

cyc=00
missing=0 
while [ $cyc -le 23 ] ; do 
  if [ ! -s $COMINobs/rap.${vday}/rap.t${cyc}z.prepbufr.tm00.nr ] ; then
    missing=$((missing + 1 ))
  fi
  cyc=$((cyc+1))
done

echo "Missing prepbufr files = " $missing
if [ $missing -eq 24  ] ; then
  echo "all of the preppbufr files are missing, exit execution!!!"
  exit
else
  echo "Continue check NARRE mean files...." 
fi

typeset -Z2 fcyc

for grid in 130 242 ; do 
 for cyc in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 ; do 

  has_narre=0
  obsv_cyc=${vday}${cyc}

  for fhr in 01 02 03 04 05 06 07 08 09 10 11 12 ; do

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    narre_mean=$COMINnarre/narre.${fday}/ensprod/narre.t${fcyc}z.mean.grd${grid}.f${fhr}.grib2
    if [ -s $narre_mean ] ; then
       has_narre=$((has_narre+1))
    fi	      
  done

  echo "For cyc" $cyc " and  grid" $grid " has_narre = " $has_narre

  if [ $has_narre -eq 0 ] ; then
     echo "All narre files are missing for cyc " $cyc "  exit execution !!!"
     exit
  fi

 done
done

echo "COntinue run METplus ..." 



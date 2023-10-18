#!/bin/ksh

set -x

typeset -Z2 cyc

missing=0 
for cyc in 00 06 12 18 ; do
  if [ ! -s $COMINobsproc/gfs.${vday}/${cyc}/atmos/gfs.t${cyc}z.prepbufr ] ; then
    missing=$((missing + 1 ))
  fi
done

echo "Missing prepbufr files = " $missing
if [ $missing -eq 4  ] ; then
  echo "all of the preppbufr files are missing, exit execution!!!"
  exit
else
  echo "Continue check CCAP files...." 
fi

missing=0
DAY1=`$NDATE +24 ${vday}12`
next=`echo ${DAY1} | cut -c 1-8`
for cyc in 00 03 06 09 12 15 18 21 ; do
  if [ $cyc = 00 ] ; then
    cyc_dir=00
    init=$vday
  elif [ $cyc = 03 ] || [ $cyc = 06 ] ; then
    cyc_dir=06
    init=$vday
  elif [ $cyc = 09 ] || [ $cyc = 12 ] ; then
    cyc_dir=12
    init=$vday
  elif [ $cyc = 15 ] || [ $cyc = 18 ] ; then
    cyc_dir=18
    init=$vday
  elif [ $cyc = 21 ] ; then
    cyc_dir=00
    init=$next
  fi	      
  ccpa=$COMINccpa/ccpa.${init}/${cyc_dir}/ccpa.t${cyc}z.03h.hrap.conus.gb2
  echo $ccpa

  if [ ! -s $ccpa ] ; then
      missing=$((missing + 1 ))
  fi
done

echo "Missing ccpa  files = " $missing
if [ $missing -eq 8  ] ; then
  echo "all of the ccpa files are missing, exit execution!!!"
  exit
else
  echo "Continue check SREF files...."
fi




typeset -Z2 fcyc

for cyc in  00 06 12 18 ; do #SREF grid2obs validation is by gfs prepbufr
	                     #So validation cyc is at 00 06 12 and 18Z

  obsv_cyc=${vday}${cyc}
  typeset -Z2 fhr
  
  fhr=03
  while [ $fhr -le 84 ] ; do

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    sref_mbrs=0
    for model in arw nmb ; do
      for mb in n1 n2 n3 n4 n5 n6 p1 p2 p3 p4 p5 p6 ctl ; do 
        sref=$COMINsref/sref.${fday}/${fcyc}/pgrb/sref_${model}.t${fcyc}z.pgrb212.${mb}.f${fhr}.grib2
        echo $sref
	if [ -s $sref ] ; then
           sref_mbrs=$((sref_mbrs+1))
        fi	    
      done
    done

    if [ $sref_mbrs -lt 26 ] ; then
      echo "SREF members = " $sref_mbrs " which < 26, exit METplus execution !!!"
      exit
    fi

    fhr=$((fhr+6))

  done

done

echo "All SREF member files are available. COntinue running  METplus ..." 



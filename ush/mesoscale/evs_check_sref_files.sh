#!/bin/ksh
#**************************************************************************
#  Purpose: check the required input forecast and validation data files
#           for sref stat jobs
#  Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************
#
set -x


typeset -Z2 vhr

vday=$VDATE

missing=0 
for vhr in 00 06 12 18 ; do
  if [ ! -s $COMINobsproc/gfs.${vday}/${vhr}/atmos/gfs.t${vhr}z.prepbufr ] ; then
    missing=$((missing + 1 ))
    echo "WARNING: $COMINobsproc/gfs.${vday}/${vhr}/atmos/gfs.t${vhr}z.prepbufr is missing"
  fi
done

echo "Missing prepbufr files = " $missing
if [ $missing -eq 4  ] ; then
  echo "WARNING: all of the preppbufr files ${COMINobsproc}/gfs.${vday}/??/atmos/gfs.t??z.prepbufr are missing"
  >$DATA/prepbufr.missing
  if [ $SENDMAIL = YES ] ; then
     export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
     echo "WARNING: all of the prepbufr files are missing" > mailmsg
     echo "Missing file is ${COMINobsproc}/gfs.${vday}/??/atmos/gfs.t??z.prepbufr"  >> mailmsg
     echo "Job ID: $jobid" >> mailmsg
     cat mailmsg | mail -s "$subject" $MAILTO
  fi

else
  echo "Continue check CCAP files...." 
fi

missing=0
DAY1=`$NDATE +24 ${vday}12`
next=`echo ${DAY1} | cut -c 1-8`
for vhr in 00 03 06 09 12 15 18 21 ; do
  if [ $vhr = 00 ] ; then
    vhr_dir=00
    init=$vday
  elif [ $vhr = 03 ] || [ $vhr = 06 ] ; then
    vhr_dir=06
    init=$vday
  elif [ $vhr = 09 ] || [ $vhr = 12 ] ; then
    vhr_dir=12
    init=$vday
  elif [ $vhr = 15 ] || [ $vhr = 18 ] ; then
    vhr_dir=18
    init=$vday
  elif [ $vhr = 21 ] ; then
    vhr_dir=00
    init=$next
  fi	      
  ccpa=$COMINccpa/ccpa.${init}/${vhr_dir}/ccpa.t${vhr}z.03h.hrap.conus.gb2
  echo $ccpa

  if [ ! -s $ccpa ] ; then
      missing=$((missing + 1 ))
      echo "WARNING: $ccpa is missing"
  fi
done

echo "Missing ccpa  files = " $missing
if [ $missing -eq 8  ] ; then
  echo "WARNING: all of the ccpa files $COMINccpa/ccpa.${vday}/??/ccpa.t??z.03h.hrap.conus.gb2 are missing"
  >$DATA/ccpa.missing
  if [ $SENDMAIL = YES ] ; then
     export subject="CCPA Data Missing for EVS ${COMPONENT}"
     echo "WARNING: all of the ccpa files are missing" > mailmsg
     echo "Missing file is $COMINccpa/ccpa.${vday}/??/ccpa.t??z.03h.hrap.conus.gb2"  >> mailmsg
     echo "Job ID: $jobid" >> mailmsg
     cat mailmsg | mail -s "$subject" $MAILTO
  fi

else
  echo "Continue check SREF files...."
fi




typeset -Z2 fvhr

for vhr in  00 06 12 18 ; do #SREF grid2obs validation is by gfs prepbufr
	                     #So validation vhr is at 00 06 12 and 18Z

  obsv_vhr=${vday}${vhr}
  typeset -Z2 fhr
  
  fhr=03
  while [ $fhr -le 84 ] ; do

    fcst_time=`$NDATE -$fhr $obsv_vhr`
    fday=${fcst_time:0:8}
    fvhr=${fcst_time:8:2}

    sref_mbrs=0
    for model in arw nmb ; do
      for mb in n1 n2 n3 n4 n5 n6 p1 p2 p3 p4 p5 p6 ctl ; do 
        sref=$COMINsref/sref.${fday}/${fvhr}/pgrb/sref_${model}.t${fvhr}z.pgrb212.${mb}.f${fhr}.grib2
        echo $sref
	if [ -s $sref ] ; then
           sref_mbrs=$((sref_mbrs+1))
        else
	   echo "WARNING: $sref is missing"
        fi	    
      done
    done

    if [ $sref_mbrs -lt 26 ] ; then
      echo "SREF members = " $sref_mbrs " which < 26"
      >$DATA/sref_mbrs.missing
    fi

    fhr=$((fhr+6))

  done

done



#!/bin/bash

set -x

mkdir -p $DATA/logs
mkdir -p $DATA/stat
mkdir -p $DATA/statanalysis

export OBSDIR=OBS
mkdir -p $DATA/$OBSDIR
export modsys=nam
export regionnest=firewxnest
export outtyp=hiresf

model1=`echo $MODELNAME | tr a-z A-Z`
export model1

export grid=G221
export fcstmax=$g2os_sfc_fhr_max

fhr=0
shr=0
fcstnum=0
obfound=0
while [ $shr -le $fcstmax ]
do
     fhr=$shr
     if [ $shr -lt 10 ]
     then
       fhr=0$shr
     fi
     export fhr

     export datehr=${VDATE}${cyc}
     adate=`$NDATE -$fhr $datehr`
     aday=`echo $adate |cut -c1-8`
     acyc=`echo $adate |cut -c9-10`
     if [ -e $COMINnam/nam.${aday}/nam.t${acyc}z.${regionnest}.${outtyp}${fhr}.tm00.grib2 ]
     then
       echo $fhr >> $DATA/fcstlist
       let "fcstnum=fcstnum+1"
     else
       if [ $acyc = 00 -o $acyc = 06 -o $acyc = 12 -o $acyc = 18 ]
       then
       export subject="NAM Firewx File Missing for EVS ${COMPONENT}"
       echo "Warning: The NAM Firewx file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
       echo "Missing file is $COMINnam/nam.${aday}/nam.t${acyc}z.${regionnest}.${outtyp}${fhr}.tm00.grib2" >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       fi
     fi
     let "shr=shr+1"
done
export fcsthours=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/fcstlist`
echo $fcsthours, $fcstnum

# do a search on the obs file needed

if [ $cyc = 00 -o $cyc = 06 -o $cyc = 12 -o $cyc = 18 ]
then
 tmnum=06
elif [ $cyc = 01 -o $cyc = 07 -o $cyc = 13 -o $cyc = 19 ]
then
 tmnum=05
elif [ $cyc = 02 -o $cyc = 08 -o $cyc = 14 -o $cyc = 20 ]
then
 tmnum=04
elif [ $cyc = 03 -o $cyc = 09 -o $cyc = 15 -o $cyc = 21 ]
then
 tmnum=03
elif [ $cyc = 04 -o $cyc = 10 -o $cyc = 16 -o $cyc = 22 ]
then
 tmnum=02
elif [ $cyc = 05 -o $cyc = 11 -o $cyc = 17 -o $cyc = 23 ]
then
 tmnum=01
fi

obdate=`$NDATE +6 $datehr`
obday=`echo $obdate |cut -c1-8`
obhr=`echo $obdate |cut -c9-10`

if [ $cyc -lt 06 -a $cyc -ge 00 ]
then
 obcyc=06
elif [ $cyc -lt 12 -a $cyc -ge 06 ]
then
 obcyc=12
elif [ $cyc -lt 18 -a $cyc -ge 12 ]
then
 obcyc=18
elif [ $cyc -ge 18 ]
then
 obcyc=00
fi

if [ -e $COMINobsproc/nam.${obday}/nam.t${obcyc}z.prepbufr.tm${tmnum} ]
then
 obfound=1
 mkdir -p $DATA/$OBSDIR/nam.${obday}
  cp $COMINobsproc/nam.${obday}/nam.t${obcyc}z.prepbufr.tm${tmnum} $DATA/$OBSDIR/nam.${obday}/nam.t${obcyc}z.prepbufr.tm${tmnum}
else
  export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
  echo "Warning: The ${obday} prepbufr file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
  echo "Missing file is $COMINobsproc/${MODELNAME}.${obday}/${MODELNAME}.t${obcyc}z.prepbufr.tm${tmnum}" >> mailmsg
  echo "Job ID: $jobid" >> mailmsg
  cat mailmsg | mail -s "$subject" $maillist
fi

echo $obfound

if [ $obfound = 1 -a $fcstnum -gt 0 ]
then

  run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstNAM_FIREWXNEST_obsPREPBUFR.conf $PARMevs/metplus_config/machine.conf
  export err=$?; err_chk

  mkdir -p $COMOUTsmall
  cp $DATA/point_stat/$MODELNAME/* $COMOUTsmall

  if [ $cyc = 23 ]
  then
       mkdir -p $COMOUTfinal
       cd $DATA/statanalysis
       run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstNAM_FIREWXNEST_obsONLYSF_GatherByDay.conf $PARMevs/metplus_config/machine.conf
       export err=$?; err_chk

       run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstNAM_FIREWXNEST_obsADPUPA_GatherByDay.conf $PARMevs/metplus_config/machine.conf
       export err=$?; err_chk

       cat *ADPUPA >> evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat
       cp evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat  $COMOUTfinal
  fi

else

  echo "NO OBS OR MODEL DATA, METplus will not run"
  echo "NUMFCST, NUMOBS", $fcstnum, $obfound

fi

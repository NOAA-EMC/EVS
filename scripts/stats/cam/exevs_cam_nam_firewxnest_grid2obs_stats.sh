#!/bin/bash

set -x

export config=$HOMEevs/parm/evs_config/cam/config.evs.cam_nam_firewxnest.prod
source $config

mkdir -p $DATA/logs
mkdir -p $DATA/stat
mkdir -p $DATA/statanalysis

export machine=${machine:-"WCOSS2"}
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
fcstmiss=0
obfound=0
while [ $shr -le $fcstmax ]
do
     fhr=$shr
     if [ $shr -lt 10 ]
     then
       fhr=0$shr
     fi
     export fhr

     export datehr=${VDATE}${vhr}
     adate=`$NDATE -$fhr $datehr`
     aday=`echo $adate |cut -c1-8`
     acyc=`echo $adate |cut -c9-10`
     if [ $acyc = 00 -o $acyc = 06 -o $acyc = 12 -o $acyc = 18 ]; then
     if [ -e $COMINnam/nam.${aday}/nam.t${acyc}z.${regionnest}.${outtyp}${fhr}.tm00.grib2 ]
     then
       echo $fhr >> $DATA/fcstlist
       let "fcstnum=fcstnum+1"
     else
       echo $fhr >> $DATA/fcstmiss
       let "fcstmiss=fcstmiss+1"
       echo "WARNING: File $COMINnam/nam.${aday}/nam.t${acyc}z.${regionnest}.${outtyp}${fhr}.tm00.grib2 is missing."
       if [ $SENDMAIL = "YES" ]; then
        export subject="NAM Firewx File Missing for EVS ${COMPONENT}"
        echo "Warning: The NAM Firewx file is missing for valid date ${VDATE}." > mailmsg
        echo "Missing file is $COMINnam/nam.${aday}/nam.t${acyc}z.${regionnest}.${outtyp}${fhr}.tm00.grib2" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
       fi
     fi
     fi
     let "shr=shr+1"
done

if [ $fcstnum -gt 0 ]; then
 export fcsthours=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/fcstlist`
 echo $fcsthours, $fcstnum
fi

if [ $fcstmiss -gt 0 ]; then
 export fcstmissing=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/fcstmiss`
 echo "WARNING: Missing forecast hours $fcstmissing"
fi


# do a search on the obs file needed

if [ $vhr = 00 -o $vhr = 06 -o $vhr = 12 -o $vhr = 18 ]
then
 tmnum=06
elif [ $vhr = 01 -o $vhr = 07 -o $vhr = 13 -o $vhr = 19 ]
then
 tmnum=05
elif [ $vhr = 02 -o $vhr = 08 -o $vhr = 14 -o $vhr = 20 ]
then
 tmnum=04
elif [ $vhr = 03 -o $vhr = 09 -o $vhr = 15 -o $vhr = 21 ]
then
 tmnum=03
elif [ $vhr = 04 -o $vhr = 10 -o $vhr = 16 -o $vhr = 22 ]
then
 tmnum=02
elif [ $vhr = 05 -o $vhr = 11 -o $vhr = 17 -o $vhr = 23 ]
then
 tmnum=01
fi

obdate=`$NDATE +6 $datehr`
obday=`echo $obdate |cut -c1-8`
obhr=`echo $obdate |cut -c9-10`

if [ $vhr -lt 06 -a $vhr -ge 00 ]
then
 obcyc=06
elif [ $vhr -lt 12 -a $vhr -ge 06 ]
then
 obcyc=12
elif [ $vhr -lt 18 -a $vhr -ge 12 ]
then
 obcyc=18
elif [ $vhr -ge 18 ]
then
 obcyc=00
fi

if [ -e $COMINobsproc/nam.${obday}/nam.t${obcyc}z.prepbufr.tm${tmnum} ]
then
 obfound=1
 mkdir -p $DATA/$OBSDIR/nam.${obday}
  cpreq $COMINobsproc/nam.${obday}/nam.t${obcyc}z.prepbufr.tm${tmnum} $DATA/$OBSDIR/nam.${obday}/nam.t${obcyc}z.prepbufr.tm${tmnum}
else
  echo "WARNING: File $COMINobsproc/${MODELNAME}.${obday}/${MODELNAME}.t${obcyc}z.prepbufr.tm${tmnum} is missing."
  if [ $SENDMAIL = "YES" ]; then
   export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
   echo "Warning: The ${obday} prepbufr file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
   echo "Missing file is $COMINobsproc/${MODELNAME}.${obday}/${MODELNAME}.t${obcyc}z.prepbufr.tm${tmnum}" >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $MAILTO
  fi
fi

echo $obfound

if [ $obfound = 1 -a $fcstnum -gt 0 ]
then

  run_metplus.py $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/PointStat_fcstNAM_FIREWXNEST_obsPREPBUFR.conf $PARMevs/metplus_config/machine.conf
  export err=$?; err_chk

  mkdir -p $COMOUTsmall
  if [ $SENDCOM = "YES" ]; then
   stat_dir=$DATA/point_stat/$MODELNAME
   stat_files=("$stat_dir"/*)
   for stat_file in "${stat_files[@]}"; do
    if [ -s $stat_file ]; then
     cp -v $stat_file $COMOUTsmall
    fi
   done
  fi

  if [ $vhr = 23 ]
  then
       mkdir -p $COMOUTfinal
       cd $DATA/statanalysis
       run_metplus.py $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstNAM_FIREWXNEST_obsONLYSF_GatherByDay.conf $PARMevs/metplus_config/machine.conf
       export err=$?; err_chk

       run_metplus.py $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstNAM_FIREWXNEST_obsADPUPA_GatherByDay.conf $PARMevs/metplus_config/machine.conf
       export err=$?; err_chk

       cat *ADPUPA >> evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat
       if [ $SENDCOM = "YES" ]; then
        if [ -s evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ]; then
         cp -v evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat  $COMOUTfinal
	fi
       fi
  fi

else

  echo "NO OBS OR MODEL DATA, METplus will not run"
  echo "NUMFCST, NUMOBS", $fcstnum, $obfound

fi

# Cat the METplus log files
log_dirs="$DATA/logs/*"
for log_dir in $log_dirs; do
    if [ -d $log_dir ]; then
        log_file_count=$(find $log_dir -type f | wc -l)
        if [[ $log_file_count -ne 0 ]]; then
            log_files=("$log_dir"/*)
            for log_file in "${log_files[@]}"; do
                if [ -f "$log_file" ]; then
                    echo "Start: $log_file"
                    cat "$log_file"
                    echo "End: $log_file"
                fi
            done
        fi
    fi
done

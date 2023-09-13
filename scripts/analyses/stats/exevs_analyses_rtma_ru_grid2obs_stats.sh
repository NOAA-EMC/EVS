#/bin/bash

set -x

mkdir -p $DATA/logs
mkdir -p $DATA/stat
export finalstat=$DATA/final
mkdir -p $DATA/final

export regionnest=rtma
export fcstmax=$g2os_sfc_fhr_max

export maskdir=$MASKS
export fhr="00"

# search to see if obs file exists

obfound=0

datehr=${VDATE}${cyc}
obday=`echo $datehr |cut -c1-8`
obhr=`echo $datehr |cut -c9-10`

if [ -e $COMINobs/${MODELNAME}.${obday}/${MODELNAME}.t${obhr}00z.prepbufr.tm00 ]
then
 obfound=1
else
 export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
 echo "Warning: The ${obday} prepbufr file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
 echo "Missing file is $COMINobs/${MODELNAME}.${obday}/${MODELNAME}.t${obhr}z.prepbufr.tm00" >> mailmsg
 echo "Job ID: $jobid" >> mailmsg
 cat mailmsg | mail -s "$subject" $maillist
fi

echo $obfound

for type in 2dvaranl 2dvarges
do
if [ $type = "2dvaranl" ]
then
        export typtag="_anl"
elif [ $type = "2dvarges" ]
then
        export typtag="_ges"
	fhr="01"
fi
for modnam in rtma2p5_ru
do
export modnam
export outtyp=$type
export OBSDIR=OBS_$modnam

model1=`echo $MODELNAME | tr a-z A-Z`
export model1

if [ $modnam = "rtma2p5_ru" ]
then
	rtmafound=0
	export grid=CONUS
        export masks=$maskdir/Bukovsky_RTMA_CONUS.nc,$maskdir/Bukovsky_RTMA_CONUS_East.nc,$maskdir/Bukovsky_RTMA_CONUS_West.nc,$maskdir/Bukovsky_RTMA_CONUS_Central.nc,$maskdir/Bukovsky_RTMA_CONUS_South.nc

fi

       if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}00z.${outtyp}_ndfd.grb2 ]
       then
         rtmafound=1
       else
         export subject="CONUS Analysis Missing for EVS ${COMPONENT}"
         echo "Warning: The CONUS Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
         echo "Missing file is $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2_wexp" >> mailmsg
         echo "Job ID: $jobid" >> mailmsg
         cat mailmsg | mail -s "$subject" $maillist
       fi

if [ ! -e $COMOUTsmall/point_stat_${modnam}${typtag}_${fhr}0000L_${VDATE}_${cyc}0000V.stat ]
then
if [ $rtmafound -eq 1 -a $obfound -eq 1 ]
then
run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstANALYSES_RU_obsNDAS_PrepBufr.conf $PARMevs/metplus_config/machine.conf
export err=$?; err_chk

mkdir -p $COMOUTsmall

if [ $SENDCOM = YES ]; then
 cp $DATA/point_stat/${MODELNAME}${typtag}/* $COMOUTsmall
fi

else
  echo "NO RTMA-RU OR OBS DATA, METplus will not run."
  echo "RTMAFOUND, OBFOUND", $rtmafound, $obfound
fi
else
  echo "RESTART - $COMOUTsmall/point_stat_${modnam}${typtag}_${fhr}_${VDATE}_${cyc}0000V.stat exists"
fi

done

if [ $cyc = 23 -a $rtmafound -eq 1 -a $obfound -eq 1 ]
then
       mkdir -p $COMOUTfinal
       cp $COMOUTsmall/*${regionnest}*${typtag}* $finalstat
       cd $finalstat
       run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstANALYSES_obsNDAS_GatherByDay.conf $PARMevs/metplus_config/machine.conf
       export err=$?; err_chk
       if [ $SENDCOM = "YES" ]; then
           cp $finalstat/evs.stats.${regionnest}_ru${typtag}.${RUN}.${VERIF_CASE}.v${VDATE}.stat $COMOUTfinal
       fi

else
       echo "NO RTMA OR OBS DATA, or not gather time yet, METplus gather job will not run"
fi

done

exit


set -x

mkdir -p $DATA/logs
mkdir -p $DATA/stat

export modsys=rtma2p5
export regionnest=rtma
export fcstmax=$g2os_sfc_fhr_max

export maskdir=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks

# search to see if obs file exists

obfound=0

datehr=${VDATE}${cyc}
obday=`echo $datehr |cut -c1-8`
obhr=`echo $datehr |cut -c9-10`

if [ -e $COMINobs/${MODELNAME}.${obday}/${MODELNAME}.t${obhr}00z.prepbufr.tm00 ]
then
 obfound=1
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
#	export poly=/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_CONUS.nc
#        export poly=$maskdir/Bukovsky_RTMA_CONUS.nc
        export masks=$maskdir/Bukovsky_RTMA_CONUS.nc,$maskdir/Bukovsky_RTMA_CONUS_East.nc,$maskdir/Bukovsky_RTMA_CONUS_West.nc,$maskdir/Bukovsky_RTMA_CONUS_Central.nc,$maskdir/Bukovsky_RTMA_CONUS_South.nc

fi

       if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}00z.${outtyp}_ndfd.grb2 ]
       then
         rtmafound=1
       fi

if [ $rtmafound -eq 1 -a $obfound -eq 1 ]
then
run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstANALYSES_RU_obsNDAS_PrepBufr.conf $PARMevs/metplus_config/machine.conf
export err=$?; err_chk

mkdir -p $COMOUTsmall
cp $DATA/point_stat/${MODELNAME}${typtag}/* $COMOUTsmall

else
  echo "NO RTMA-RU OR OBS DATA"
  echo "RTMAFOUND, OBFOUND", $rtmafound, $obfound
fi

done

if [ $cyc = 23 -a $rtmafound -eq 1 -a $obfound -eq 1 ]
then
       mkdir -p $COMOUTfinal
       run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstANALYSES_obsNDAS_GatherByDay.conf $PARMevs/metplus_config/machine.conf
       export err=$?; err_chk
fi

done

exit


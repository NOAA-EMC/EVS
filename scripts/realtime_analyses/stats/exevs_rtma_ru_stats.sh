set -x

mkdir -p $DATA/logs
mkdir -p $DATA/stat

export modsys=rtma2p5
export regionnest=rtma
export fcstmax=$g2os_sfc_fhr_max

export maskdir=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks

# search to see if obs file exists

obfound=0
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

datehr=${VDATE}${cyc}
obdate=`/apps/ops/prod/nco/core/prod_util.v2.0.7/exec/ndate +6 $datehr`
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

if [ -e $COMINobs/nam.${obday}/nam.t${obcyc}z.prepbufr.tm${tmnum} ]
then
 obfound=1
fi

echo $obfound

for type in 2dvaranl 2dvarges
do
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
        export poly=$maskdir/Bukovsky_RTMA_CONUS.nc
fi

       if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}00z.${outtyp}_ndfd.grb2 ]
       then
         rtmafound=1
       fi

if [ $rtmafound -eq 1 -a $obfound -eq 1 ]
then
run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstREALTIME_ANALYSES_RU_obsNDAS_PrepBufr.conf $PARMevs/metplus_config/machine.conf
export err=$?; err_chk

mkdir -p $COMOUTsmall
cp $DATA/point_stat/$MODELNAME/* $COMOUTsmall

else
  echo "NO RTMA-RU OR OBS DATA"
  echo "RTMAFOUND, OBFOUND", $rtmafound, $obfound
fi

done
done

if [ $cyc = 23 -a $rtmafound -eq 1 -a $obfound -eq 1 ]
then
       mkdir -p $COMOUTfinal
       run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstREALTIME_ANALYSES_obsNDAS_GatherByDay.conf $PARMevs/metplus_config/machine.conf
       export err=$?; err_chk
fi

exit


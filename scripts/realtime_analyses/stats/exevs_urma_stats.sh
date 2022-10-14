set -x

mkdir -p $DATA/logs
mkdir -p $DATA/stat

export regionnest=urma
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
for modnam in urma2p5 akurma prurma hiurma 
do
export modnam
export outtyp=$type
export OBSDIR=OBS_$modnam

model1=`echo $MODELNAME | tr a-z A-Z`
export model1

if [ $modnam = "urma2p5" ]
then
	urmafound=0
	export grid=
#	export poly=/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_CONUS.nc
        export poly=$maskdir/Bukovsky_RTMA_CONUS.nc
	export wexptag="_wexp"

	if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2_wexp ]
        then
          urmafound=1
       fi

fi
if [ $modnam = "akurma" ] 
then
	export grid=
        export poly=$maskdir/Alaska_RTMA.nc
	export wexptag=""

# check for CONUS rtma2p5 file

        urmafound=0

        if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2 ]
        then
          urmafound=1
        fi

fi
if [ $modnam = "hiurma" ]
then
        export grid=
        export poly=$maskdir/Hawaii_RTMA.nc
	export wexptag=""

	# check for CONUS rtma2p5 file

        urmafound=0

        if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2 ]
        then    
          urmafound=1
        fi

fi
if [ $modnam = "prurma" ]
then
        export grid=
        export poly=$maskdir/Puerto_Rico_RTMA.nc
        export wexptag=""

	urmafound=0

        if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2 ]
        then
          urmafound=1
        fi

fi

if [ $urmafound -eq 1 -a $obfound -eq 1 ]
then

run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstREALTIME_ANALYSES_obsNDAS_PrepBufr.conf $PARMevs/metplus_config/machine.conf
export err=$?; err_chk

mkdir -p $COMOUTsmall
cp $DATA/point_stat/$modnam/* $COMOUTsmall
else
echo "NO URMA OR OBS DATA"
echo "URMAFOUND, OBFOUND", $urmafound, $obfound
fi


done
done

if [ $cyc = 23 -a $urmafound -eq 1 -a $obfound -eq 1 ]
then
       mkdir -p $COMOUTfinal
       run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstREALTIME_ANALYSES_obsNDAS_GatherByDay.conf $PARMevs/metplus_config/machine.conf
       export err=$?; err_chk
fi

exit


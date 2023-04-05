set -x

mkdir -p $DATA/logs
mkdir -p $DATA/stat

export regionnest=urma
export fcstmax=$g2os_sfc_fhr_max

export maskdir=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks

# search to see if obs file exists

obfound=0

datehr=${VDATE}${cyc}
obday=`echo $datehr |cut -c1-8`
obhr=`echo $datehr |cut -c9-10`

if [ -e $COMINobs/${MODELNAME}.${obday}/${MODELNAME}.t${obhr}z.prepbufr.tm00 ]
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
        export masks=$maskdir/Bukovsky_RTMA_CONUS.nc,$maskdir/Bukovsky_RTMA_CONUS_East.nc,$maskdir/Bukovsky_RTMA_CONUS_West.nc,$maskdir/Bukovsky_RTMA_CONUS_Central.nc,$maskdir/Bukovsky_RTMA_CONUS_South.nc
	export wexptag="_wexp"
	export restag=""

	if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2_wexp ]
        then
          urmafound=1
       fi

fi
if [ $modnam = "akurma" ] 
then
	export grid=
        export masks=$maskdir/Alaska_RTMA.nc
	export wexptag=""
	export restag="_3p0"

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
        export masks=$maskdir/Hawaii_RTMA.nc
	export wexptag=""
	export restag=""

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
        export masks=$maskdir/Puerto_Rico_RTMA.nc
        export wexptag=""
	export restag=""

	urmafound=0

        if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2 ]
        then
          urmafound=1
        fi

fi

if [ $urmafound -eq 1 -a $obfound -eq 1 ]
then

run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstANALYSES_obsNDAS_PrepBufr.conf $PARMevs/metplus_config/machine.conf
export err=$?; err_chk

mkdir -p $COMOUTsmall
cp $DATA/point_stat/${modnam}${typtag}/* $COMOUTsmall
else
echo "NO URMA OR OBS DATA"
echo "URMAFOUND, OBFOUND", $urmafound, $obfound
fi


done

if [ $cyc = 23 -a $urmafound -eq 1 -a $obfound -eq 1 ]
then
       mkdir -p $COMOUTfinal
       run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstANALYSES_obsNDAS_GatherByDay.conf $PARMevs/metplus_config/machine.conf
       export err=$?; err_chk
fi

done

exit


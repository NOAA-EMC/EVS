set -x

mkdir -p $DATA/logs
mkdir -p $DATA/stat
export finalstat=$DATA/final
mkdir -p $finalstat

export regionnest=urma
export fcstmax=$g2os_sfc_fhr_max

export maskdir=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks

# search to see if obs file exists

for modnam in urma
do
export modnam
export outtyp=$type
export OBSDIR=OBS_$modnam

model1=`echo $MODELNAME | tr a-z A-Z`
export model1

if [ $modnam = "urma" ]
then

# check for CONUS urma file

	urmafound=0
	obfound=0
	urmanum=0
       export masks=$maskdir/Bukovsky_RTMA_CONUS.nc
       mkdir -p $DATA/pcp${modnam}

	if [ -e $DCOMIN/${VDATE}/validation_data/CoCoRaHS/cocorahs.${VDATE}.dailyprecip.csv ]
	then
	 obfound=1
	fi

        DATE=${VDATE}${vhr}
        ENDDATE=`$NDATE -23 $DATE`
        while [ $DATE -ge $ENDDATE ]; do
        echo $DATE > curdate
        DAY=`cut -c 1-8 curdate`
        HOUR=`cut -c 9-10 curdate`
	if [ -e $COMINurma/pcp${modnam}.${DAY}/pcp${modnam}_g184.${DAY}${HOUR}.01h.grb2 ]
        then
	 let "urmanum=urmanum+1"
	 cp $COMINurma/pcp${modnam}.${DAY}/pcp${modnam}_g184.${DAY}${HOUR}.01h.grb2  $DATA/pcp${modnam}
        fi
	DATE=`$NDATE -1 $DATE`
        done
fi

echo "Number of URMA files found is $urmanum"
if [ $urmanum -eq 24 ];then
   urmafound=1
fi

if [ $urmafound -eq 1 -a $obfound -eq 1 ]
then
    run_metplus.py $PARMevs/metplus_config/stats/${COMPONENT}/${VERIF_CASE}/PointStat_fcstURMA_obsCOCORAHS_ASCIIprecip.conf $PARMevs/metplus_config/machine.conf
    export err=$?; err_chk

  mkdir -p $COMOUTsmall
  cp $DATA/PointStat/* $COMOUTsmall
else
  echo "NO URMA OR OBS DATA"
  echo "URMAFOUND, OBFOUND", $urmafound, $obfound
fi

done

# Run StatAnalysis to generate final stat file
#
 if [ $vhr = 23 -a $urmafound -eq 1 -a $obfound -eq 1 ]
 then
  mkdir -p $COMOUTfinal
  cp $COMOUTsmall/* $finalstat
  cd $finalstat
  run_metplus.py $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstANALYSES_obsCOCORAHS_ASCIIprecip.conf $PARMevs/metplus_config/machine.conf
  export err=$?; err_chk
  if [ $SENDCOM = "YES" ]; then
    if [ -s $finalstat/evs.stats.${modnam}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ]; then
       cp -v $finalstat/evs.stats.${modnam}.${RUN}.${VERIF_CASE}.v${VDATE}.stat $COMOUTfinal
    fi 
 fi   
fi

exit


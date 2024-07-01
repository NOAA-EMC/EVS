set -x

mkdir -p $DATA/logs
mkdir -p $DATA/stat
export finalstat=$DATA/final
mkdir -p $finalstat

export regionnest=ccpa
export fcstmax=$g2os_sfc_fhr_max

export maskdir=$MASKS

# search to see if obs file exists

for modnam in ccpa
do
export modnam
export outtyp=$type
export OBSDIR=OBS_$modnam

model1=`echo $MODELNAME | tr a-z A-Z`
export model1

if [ $modnam = "ccpa" ]
then

# check for CONUS ccpa file

	ccpafound=0
	obfound=0
	ccpanum=0
       export masks=$maskdir/Bukovsky_RTMA_CONUS.nc
       mkdir -p $DATA/ccpa

	if [ -e $DCOMIN/${VDATE}/validation_data/CoCoRaHS/cocorahs.${VDATE}.dailyprecip.csv ]
	then
	 obfound=1
	else
	 echo "WARNING: $DCOMIN/${VDATE}/validation_data/CoCoRaHS/cocorahs.${VDATE}.dailyprecip.csv is missing, METplus will not run"
          if [ $SENDMAIL = "YES" ]; then
	    export subject="CoCoRaHS Data Missing for EVS ${COMPONENT}"
	    echo "Warning: The CoCoRaHS file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
	    echo "Missing file is $DCOMIN/${VDATE}/validation_data/CoCoRaHS/cocorahs.${VDATE}.dailyprecip.csv" >> mailmsg
	    echo "Job ID: $jobid" >> mailmsg
	    cat mailmsg | mail -s "$subject" $MAILTO
	  fi
	fi

	DATE=${VDATE}${vhr}
	ENDDATE=`$NDATE -23 $DATE`
	while [ $DATE -ge $ENDDATE ]; do
	echo $DATE > curdate
	DAY=`cut -c 1-8 curdate`
	HOUR=`cut -c 9-10 curdate`
	if [ -e $EVSINccpa/ccpa.${DAY}/ccpa.t${HOUR}z.01h.hrap.conus.gb2 ]
        then
         let "ccpanum=ccpanum+1"
	 cp $EVSINccpa/ccpa.${DAY}/ccpa.t${HOUR}z.01h.hrap.conus.gb2  $DATA/ccpa
        else
         echo  "WARNING: $EVSINccpa/ccpa.${DAY}/ccpa.t${HOUR}z.01h.hrap.conus.gb2 is missing, METplus will not run"
         if [ $SENDMAIL = "YES" ]; then
           export subject="CONUS Precip Analysis Missing for EVS ${COMPONENT}"
           echo "Warning: The CONUS Analysis file is missing for valid date ${DAY}. METplus will not run." > mailmsg
           echo "Missing file is $EVSINccpa/ccpa.${DAY}/ccpa.t${HOUR}z.01h.hrap.conus.gb2" >> mailmsg
           echo "Job ID: $jobid" >> mailmsg
           cat mailmsg | mail -s "$subject" $MAILTO
         fi
        fi
	DATE=`$NDATE -1 $DATE`
        done
fi

echo "Number of CCPA files found is $ccpanum"
if [ $ccpanum -eq 24 ];then
 ccpafound=1
else
 echo "WARNING: Fewer than 24 files found, found only $ccpanum. METplus will not run"
fi


if [ $ccpafound -eq 1 -a $obfound -eq 1 ]
then
    run_metplus.py $PARMevs/metplus_config/stats/${COMPONENT}/${VERIF_CASE}/PointStat_fcstCCPA_obsCOCORAHS_ASCIIprecip.conf $PARMevs/metplus_config/machine.conf
    export err=$?; err_chk

  mkdir -p $COMOUTsmall
  cp $DATA/PointStat/* $COMOUTsmall
else
  echo "NO CCPA OR OBS DATA"
  echo "CCPAFOUND, OBFOUND", $ccpafound, $obfound
fi

done

# Run StatAnalysis to generate final stat file
#
 if [ $vhr = 23 -a $ccpafound -eq 1 -a $obfound -eq 1 ]
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


set -x

mkdir -p $DATA/plots
mkdir -p $DATA/logs
export STATDIR=$DATA/stats
mkdir -p $STATDIR
export PLOTDIR=$DATA/plots
export OUTDIR=$DATA/out
mkdir -p $OUTDIR
export PRUNEDIR=$DATA/prune
mkdir -p $PRUNEDIR

model1=`echo $MODELNAME | tr a-z A-Z`
export model1

STARTDATE=${VDATE}00
ENDDATE=${PDYm31}00
DATE=$STARTDATE

while [ $DATE -ge $ENDDATE ]; do

	for anl in rtma urma rtma_ru
	do	
	
	export anl
	ANL1=`echo $anl | tr a-z A-Z`
	export ANL1

	echo $DATE > curdate
	DAY=`cut -c 1-8 curdate`
	YEAR=`cut -c 1-4 curdate`
	MONTH=`cut -c 1-6 curdate`
	HOUR=`cut -c 9-10 curdate`

	if [ -e ${COMINanl}/${anl}.${DAY}/evs.stats.${anl}_anl.${RUN}.${VERIF_CASE}.v${DAY}.stat ]
	then
	cp ${COMINanl}/${anl}.${DAY}/evs.stats.${anl}_anl.${RUN}.${VERIF_CASE}.v${DAY}.stat $STATDIR
        fi

        if [ -e ${COMINanl}/${anl}.${DAY}/evs.stats.${anl}_ges.${RUN}.${VERIF_CASE}.v${DAY}.stat ]
        then
        cp ${COMINanl}/${anl}.${DAY}/evs.stats.${anl}_ges.${RUN}.${VERIF_CASE}.v${DAY}.stat $STATDIR
	fhr=0
	shr=0
	while [ $shr -lt 18 ]
	do
	 fhr=$shr
	 if [ $shr -lt 10 ]
	 then
          fhr=0$shr
	 fi

	 sed "s/ ${fhr}0000 / 000000 /g" $STATDIR/evs.stats.${anl}_ges.${RUN}.${VERIF_CASE}.v${DAY}.stat > $STATDIR/temp.stat
	 mv $STATDIR/temp.stat $STATDIR/evs.stats.${anl}_ges.${RUN}.${VERIF_CASE}.v${DAY}.stat

	 let "shr=shr+1"
	done
        fi

        done

	DATE=`$NDATE -24 $DATE`

done

for region in CONUS CONUS_East CONUS_West CONUS_Central CONUS_South Alaska Hawaii PuertoRico Guam
do
	if [ $region = CONUS_East ]
	then
         smregion=conus_e
	elif [ $region = CONUS_West ]
	then
	 smregion=conus_w
	elif [ $region = CONUS_South ]
	then
	 smregion=conus_s
	elif [ $region = CONUS_Central ]
	then
	 smregion=conus_c
	elif [ $region = CONUS ]
	then
	 smregion=conus
	elif [ $region = Alaska ]
	then
         smregion=alaska
	elif [ $region = Hawaii ]
	then
	 smregion=hawaii
	elif [ $region = PuertoRico ]
	then
	 smregion=prico
        elif [ $region = Guam ]
	then
	 smregion=guam	
	fi

for anl in rtma urma rtma_ru
do
for varb in TMP DPT
do
	export var=${varb}2m
	export region
	export lev=Z2
	export lev_obs=Z2
	export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $varb | tr A-Z a-z`
	sh $USHevs/${COMPONENT}/py_plotting.config

	if [ -e valid_hour* ]
	then
        mv ${DATA}/valid_hour* ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$varb,$region,$anl
        fi
done

for varb in WIND
do
	export var=${varb}10m
	export lev=Z10
	export lev_obs=Z10
        export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
        smvar=`echo $varb | tr A-Z a-z`
	sh $USHevs/${COMPONENT}/py_plotting.config

	if [ -e valid_hour* ]
	then
        mv ${DATA}/valid_hour* ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$varb,$region,$anl
        fi
done

for varb in GUST
do
	export var=${varb}sfc
	export lev=Z10
	export lev_obs=Z0
	export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
        smvar=`echo $varb | tr A-Z a-z`
	sh $USHevs/${COMPONENT}/py_plotting.config

	if [ -e valid_hour* ]
	then
        mv ${DATA}/valid_hour* ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$varb,$region,$anl
        fi
done

for varb in VIS CEILING
do
	if [ $varb = "VIS" ]
	then
	 export var=${varb}sfc
        elif [ $varb = "CEILING" ]
	then
	 export var=HGTcldceil
        fi	 
	export lev=L0
	export lev_obs=L0
	export linetype=CTC
        if [ $var = VISsfc ]
	then
          export thresh="<805, <1609, <4828, <8045,  <16090"
	elif [ $var = HGTcldceil ]
	then
          export thresh="<152, <305, <914, <1524, <3048"
	fi
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $varb | tr A-Z a-z`
	sh $USHevs/${COMPONENT}/py_plotting.config_perf

	if [ -e perf* ]
	then
	mv ${DATA}/perf* ${PLOTDIR}/evs.${anl}.ctc.${smvar}_${smlev}.last31days.perfdiag.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$varb,$region,$anl
        fi

	for stat in csi fbias
	do

	export stat

	sh $USHevs/${COMPONENT}/py_plotting.config_thresh
	if [ -e thresh* ]
	then
	mv ${DATA}/thresh* ${PLOTDIR}/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$varb,$region,$anl
        fi

        
        done
done

        if [ $anl = rtma -o $anl = urma ]
	then
        export var=TCDC
	export lev=L0
	export lev_obs=L0
	export linetype=CTC
	export thresh=">10,>50,>90"
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

	for stat in csi ets fbias
	do
	export stat

	sh $USHevs/${COMPONENT}/py_plotting.config_thresh
	if [ -e thresh* ]
	then
	mv ${DATA}/thresh* ${PLOTDIR}/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$var,$region,$anl
        fi
        done
        fi

	
done
done

cd ${PLOTDIR}
tar -cvf evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar *png

cp evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar $COMOUTplots

exit





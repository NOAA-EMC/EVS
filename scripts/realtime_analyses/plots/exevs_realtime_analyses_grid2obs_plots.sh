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

module load imagemagick/7.0.8-7

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

	if [ -e ${COMINanl}/${anl}.${DAY}/${anl}_${RUN}_${VERIF_CASE}_v${DAY}.stat ]
	then
	cp ${COMINanl}/${anl}.${DAY}/${anl}_${RUN}_${VERIF_CASE}_v${DAY}.stat $STATDIR
        else
        cp ${COMINanl}/${anl}.${DAY}/*stat $STATDIR/${anl}_${RUN}_${VERIF_CASE}_v${DAY}.stat 
        fi

	sed "s/$ANL1/$anl/g" $STATDIR/${anl}_${RUN}_${VERIF_CASE}_v${DAY}.stat > $STATDIR/temp.stat
	mv $STATDIR/temp.stat $STATDIR/${anl}_${RUN}_${VERIF_CASE}_v${DAY}.stat

        done

	DATE=`/apps/ops/prod/nco/core/prod_util.v2.0.7/exec/ndate -24 $DATE`

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

for var in TMP2m DPT2m
do
	export var
	export region
	export lev=Z2
	export lev_obs=Z2
	export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`
	sh $USHevs/${COMPONENT}/py_plotting.config

#        mv ${DATA}/valid_hour* ${PLOTDIR}/BCRMSE_${region}_${var}_${lev}_G221_VALID${PDYm31}to${VDATE}_VALHR.png
#        mv ${DATA}/valid_hour* ${PLOTDIR}/${COMPONENT}.bcrmse_me.${smvar}_${smlev}.buk_${smregion}.last31days.vhrmean_f000.png
         mv ${DATA}/valid_hour* ${PLOTDIR}/evs.${COMPONENT}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean_f000.buk_${smregion}.png
done

for var in WIND10m
do
	export var
	export lev=Z10
	export lev_obs=Z10
        export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
        smvar=`echo $var | tr A-Z a-z`
	sh $USHevs/${COMPONENT}/py_plotting.config

#        mv ${DATA}/valid_hour* ${PLOTDIR}/BCRMSE_${region}_${var}_${lev}_G221_VALID${PDYm31}to${VDATE}_VALHR.png
        mv ${DATA}/valid_hour* ${PLOTDIR}/evs.${COMPONENT}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean_f000.buk_${smregion}.png
done

for var in GUSTsfc
do
	export var
	export lev=Z10
	export lev_obs=Z0
	smlev=`echo $lev | tr A-Z a-z`
        smvar=`echo $var | tr A-Z a-z`
	sh $USHevs/${COMPONENT}/py_plotting.config

#        mv ${DATA}/valid_hour* ${PLOTDIR}/BCRMSE_${region}_${var}_${lev}_G221_VALID${PDYm31}to${VDATE}_VALHR.png
        mv ${DATA}/valid_hour* ${PLOTDIR}/evs.${COMPONENT}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean_f000.buk_${smregion}.png
done
done


exit





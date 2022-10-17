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

	echo $DATE > curdate
	DAY=`cut -c 1-8 curdate`
	YEAR=`cut -c 1-4 curdate`
	MONTH=`cut -c 1-6 curdate`
	HOUR=`cut -c 9-10 curdate`

	if [ -e ${COMINnam}.$DAY/${MODELNAME}_${RUN}_${VERIF_CASE}_v${DAY}.stat ]
	then
	cp ${COMINnam}.$DAY/${MODELNAME}_${RUN}_${VERIF_CASE}_v${DAY}.stat $STATDIR
        else
        cp ${COMINnam}.$DAY/*stat $STATDIR/${MODELNAME}_${RUN}_${VERIF_CASE}_v${DAY}.stat 
        fi

	sed "s/$model1/$MODELNAME/g" $STATDIR/${MODELNAME}_${RUN}_${VERIF_CASE}_v${DAY}.stat > $STATDIR/temp.stat
	mv $STATDIR/temp.stat $STATDIR/${MODELNAME}_${RUN}_${VERIF_CASE}_v${DAY}.stat

	DATE=`/apps/ops/prod/nco/core/prod_util.v2.0.7/exec/ndate -24 $DATE`

done

for var in TMP2m DPT2m RH2m
do
	export var
	export lev=Z2
	export linetype=SL1L2
	sh $USHevs/${COMPONENT}/py_plotting.config

        mv ${DATA}/lead_average* ${PLOTDIR}/BCRMSE_${var}_${lev}_G221_VALID${PDYm31}to${VDATE}_DIEOFF.png
done

for var in UGRD10m VGRD10m UGRD_VGRD10m WIND10m
do
	export var
	export lev=Z10
	if [ $var = UGRD_VGRD10m ]
        then
         export linetype=VL1L2
	else
         export linetype=SL1L2
	fi
	sh $USHevs/${COMPONENT}/py_plotting.config

        mv ${DATA}/lead_average* ${PLOTDIR}/BCRMSE_${var}_${lev}_G221_VALID${PDYm31}to${VDATE}_DIEOFF.png
done

for var in GUSTsfc
do
	export var
	export lev=Z0
	sh $USHevs/${COMPONENT}/py_plotting.config

        mv ${DATA}/lead_average* ${PLOTDIR}/BCRMSE_${var}_${lev}_G221_VALID${PDYm31}to${VDATE}_DIEOFF.png
done


exit





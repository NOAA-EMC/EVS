set -x

mkdir -p $DATA/logs
export STATDIR=$DATA/stats
export PLOTDIR=$DATA/plots
export OUTDIR=$DATA/out
export PRUNEDIR=$DATA/prune
mkdir -p $STATDIR
mkdir =p $PLOTDIR
mkdir -p $PRUNEDIR
mkdir -p $OUTDIR

model1=`echo $MODELNAME | tr a-z A-Z`
export model1

module load imagemagick/7.0.8-7

for aqmtyp in awpozcon_raw awpozcon_bc pm25_raw pm25_bc ozmax8_raw ozmax8_bc pmave_raw pmave_bc
do

STARTDATE=${VDATE}00
ENDDATE=${PDYm31}00
DATE=$STARTDATE

while [ $DATE -ge $ENDDATE ]; do

	echo $DATE > curdate
	DAY=`cut -c 1-8 curdate`
	YEAR=`cut -c 1-4 curdate`
	MONTH=`cut -c 1-6 curdate`
	HOUR=`cut -c 9-10 curdate`

	if [ -e ${COMINaqm}.$DAY/${aqmtyp}_${RUN}_${VERIF_CASE}_v${DAY}.stat ]
	then
	cp ${COMINaqm}.$DAY/${aqmtyp}_${RUN}_${VERIF_CASE}_v${DAY}.stat $STATDIR
        else
        cp ${COMINaqm}.$DAY/*stat $STATDIR/${aqmtyp}_${RUN}_${VERIF_CASE}_v${DAY}.stat 
        fi

	sed "s/$model1/$aqmtyp/g" $STATDIR/${aqmtyp}_${RUN}_${VERIF_CASE}_v${DAY}.stat > $STATDIR/temp.stat
	mv $STATDIR/temp.stat $STATDIR/${aqmtyp}_${RUN}_${VERIF_CASE}_v${DAY}.stat

	DATE=`/apps/ops/prod/nco/core/prod_util.v2.0.7/exec/ndate -24 $DATE`

done
done

        for inithr in 06 12
	do
	
	export inithr
	export var=OZCON1
	export lev=A1
	export linetype=SL1L2
	sh $USHevs/${COMPONENT}/py_plotting_awpozcon.config

        mv ${DATA}/lead_average* ${PLOTDIR}/BCRMSE_${var}_${lev}_CONUS_VALID${PDYm31}to${VDATE}_init${inithr}_DIEOFF.png

	sh $USHevs/${COMPONENT}/py_plotting_awpozcon_fbar.config
	mv ${DATA}/lead_average* ${PLOTDIR}/FBAR_${var}_${lev}_CONUS_VALID${PDYm31}to${VDATE}_init${inithr}_DIEOFF.png

	export var=PMTF
        export lev=L1
	export lev_obs=A1
        export linetype=SL1L2
        sh $USHevs/${COMPONENT}/py_plotting_pm25.config

        mv ${DATA}/lead_average* ${PLOTDIR}/BCRMSE_${var}_${lev}_CONUS_VALID${PDYm31}to${VDATE}_init${inithr}_DIEOFF.png

        sh $USHevs/${COMPONENT}/py_plotting_pm25_fbar.config
        mv ${DATA}/lead_average* ${PLOTDIR}/FBAR_${var}_${lev}_CONUS_VALID${PDYm31}to${VDATE}_init${inithr}_DIEOFF.png

        done

	for flead in 23 47 71
	do
	export flead
	export var=OZMAX8
	export lev=L1
	export lev_obs=A8
	export linetype=CTC

	sh $USHevs/${COMPONENT}/py_plotting_ozmax8.config
	mv ${DATA}/performance* ${PLOTDIR}/CTC_${var}_${lev}_CONUS_VALID${PDYm31}to${VDATE}_${flead}_PERF.png

        done

	for flead in 16 40 64
	do
	export flead
	export var=PMAVE
	export lev=A23
	export lev_obs=A1
	export linetype=CTC

	sh $USHevs/${COMPONENT}/py_plotting_pmave.config
	mv ${DATA}/performance* ${PLOTDIR}/CTC_${var}_${lev}_CONUS_VALID${PDYm31}to${VDATE}_${flead}_PERF.png

        done


exit



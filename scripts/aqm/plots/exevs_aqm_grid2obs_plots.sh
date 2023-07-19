#!/bin/ksh

set -x

mkdir -p $DATA/logs
export STATDIR=$DATA/stats
export PLOTDIR=$DATA/plots
export PLOTDIR_headline=$DATA/plots_headline
export OUTDIR=$DATA/out
export PRUNEDIR=$DATA/prune
mkdir -p $STATDIR
mkdir -p $PLOTDIR ${PLOTDIR_headline}
mkdir -p $PRUNEDIR
mkdir -p $OUTDIR

model1=`echo $MODELNAME | tr a-z A-Z`
export model1

for aqmtyp in ozmax8 pmave
do
for biasc in bc
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

	cpfile=evs.stats.${COMPONENT}_${biasc}.${RUN}.${VERIF_CASE}_${aqmtyp}.v${DAY}.stat
	if [ -e ${COMINaqm}.$DAY/${cpfile} ]; then
	    cp ${COMINaqm}.$DAY/${cpfile} $STATDIR
            sed "s/$model1/${aqmtyp}_${biasc}/g" $STATDIR/${cpfile} > $STATDIR/evs.stats.${aqmtyp}_${biasc}.${RUN}.${VERIF_CASE}.v${DAY}.stat
        else
            echo "WARNING ${COMPONENT} ${STEP} :: Can not find ${COMINaqm}.$DAY/${cpfile}"
        fi

	DATE=`$NDATE -24 $DATE`

done
done
done

##
## Headline Plots
##
for region in CONUS CONUS_East CONUS_West CONUS_South CONUS_Central
do
	export region
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
	fi

	for flead in 47
	do
	export flead
	export var=OZMAX8
	export lev=L1
	export lev_obs=A8
	export linetype=CTC
	export inithr=12
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

	sh $USHevs/${COMPONENT}/py_plotting_ozmax8_headline.config
	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR_headline}/headline_$COMPONENT.csi_gt70.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$var,$region
        fi

        done

	for flead in 40
	do
	export flead
	export var=PMAVE
	export lev=A23
	export lev_obs=A1
	export linetype=CTC
        export inithr=12
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

	sh $USHevs/${COMPONENT}/py_plotting_pmave_headline.config
	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR_headline}/headline_$COMPONENT.csi_gt35.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$var,$region
        fi

        done
done

cd ${PLOTDIR_headline}
tarfile=evs.plots.${COMPONENT}.${RUN}.headline.v${VDATE}.tar
tar -cvf ${tarfile} *png

mkdir -m 775 -p ${COMOUTheadline}
cp ${tarfile} ${COMOUTheadline}

exit



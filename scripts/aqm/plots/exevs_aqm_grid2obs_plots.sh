#!/bin/ksh

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
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/headline_$COMPONENT.csi_gt70.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png
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
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/headline_$COMPONENT.csi_gt35.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$var,$region
        fi

        done
done

cd ${PLOTDIR}
tar -cvf evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar *png

mkdir -m 775 -p $COMOUTplots
cp evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar $COMOUTplots

exit



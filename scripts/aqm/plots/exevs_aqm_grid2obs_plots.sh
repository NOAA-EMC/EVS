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

for aqmtyp in ozone pm25 ozmax8 pmave
do
for biasc in raw bc
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

	if [ -e ${COMINaqm}.$DAY/evs.stats.${COMPONENT}_${biasc}.${RUN}.${VERIF_CASE}_${aqmtyp}.v${DAY}.stat ]
	then
	cp ${COMINaqm}.$DAY/evs.stats.${COMPONENT}_${biasc}.${RUN}.${VERIF_CASE}_${aqmtyp}.v${DAY}.stat $STATDIR
        fi

	sed "s/$model1/${aqmtyp}_${biasc}/g" $STATDIR/evs.stats.${COMPONENT}_${biasc}.${RUN}.${VERIF_CASE}_${aqmtyp}.v${DAY}.stat > $STATDIR/evs.stats.${aqmtyp}_${biasc}.${RUN}.${VERIF_CASE}.v${DAY}.stat

	DATE=`$NDATE -24 $DATE`

done
done
done

for region in CONUS CONUS_East CONUS_West CONUS_South CONUS_Central Appalachia CPlains DeepSouth GreatBasin GreatLakes Mezquital MidAtlantic NorthAtlantic NPlains NRockies PacificNW PacificSW Prairie Southeast Southwest SPlains SRockies
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
	elif [ $region = Appalachia ]
	then
	 smregion=apl
	elif [ $region = CPlains ]
	then
	 smregion=cpl
	elif [ $region = DeepSouth ]
	then
	 smregion=ds
	elif [ $region = GreatBasin ]
	then
	 smregion=grb
	elif [ $region = GreatLakes ]
	then
	 smregion=grlk
	elif [ $region = Mezquital ]
	then
	 smregion=mez
	elif [ $region = MidAtlantic ]
	then
	 smregion=matl
	elif [ $region = NorthAtlantic ]
	then
         smregion=ne
	elif [ $region = NPlains ]
	then
	 smregion=npl
	elif [ $region = NRockies ]
	then
         smregion=nrk
	elif [ $region = PacificNW ]
	then
	 smregion=npw
	elif [ $region = PacificSW ]
	then
	 smregion=psw
	elif [ $region = Prairie ]
	then
	 smregion=pra
	elif [ $region = Southeast ]
	then
	 smregion=se
	elif [ $region = Southwest ]
	then
	 smregion=sw
        elif [ $region = SPlains ]
	then
	 smregion=spl
	elif [ $region = SRockies ]
	then
	 smregion=srk
	elif [ $region = CONUS ]
	then
	 smregion=conus
	fi

        for inithr in 06 12
	do
	
	export inithr
	export var=OZCON1
	export lev=A1
	export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
	smvar=ozone
	sh $USHevs/${COMPONENT}/py_plotting_awpozcon.config

	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$var,$region
        fi

	sh $USHevs/${COMPONENT}/py_plotting_awpozcon_fbar.config
	
	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$var,$region
        fi

	export var=PMTF
        export lev=L1
	export lev_obs=A1
        export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
        smvar=pm25
        sh $USHevs/${COMPONENT}/py_plotting_pm25.config

	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
        mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$var,$region
        fi

        sh $USHevs/${COMPONENT}/py_plotting_pm25_fbar.config
	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
        mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$var,$region
        fi

        done

	for flead in 29 53 77
	do
	export flead
	export var=OZMAX8
	export lev=L1
	export lev_obs=A8
	export linetype=CTC
	export inithr=06
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

	sh $USHevs/${COMPONENT}/py_plotting_ozmax8.config
	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$var,$region
        fi

        done

	for flead in 23 47 71
	do
	export flead
	export var=OZMAX8
	export lev=L1
	export lev_obs=A8
	export linetype=CTC
	export inithr=12
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

	sh $USHevs/${COMPONENT}/py_plotting_ozmax8.config
	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$var,$region
        fi

        done

	for flead in 22 46 70
	do
	export flead
	export var=PMAVE
	export lev=A23
	export lev_obs=A1
	export linetype=CTC
	export inithr=06
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

	sh $USHevs/${COMPONENT}/py_plotting_pmave.config
	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png
        else
	echo "NO PLOT FOR",$var,$region
        fi

        done

	for flead in 16 40 64
	do
	export flead
	export var=PMAVE
	export lev=A23
	export lev_obs=A1
	export linetype=CTC
        export inithr=12
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

	sh $USHevs/${COMPONENT}/py_plotting_pmave.config
	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png
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



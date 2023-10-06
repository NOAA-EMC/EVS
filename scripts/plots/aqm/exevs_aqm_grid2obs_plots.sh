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
	mkdir -p $COMOUTplots/$var
	export lev=A1
	export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
	smvar=ozone
	if [ ! -e $COMOUTplots/$var/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png ]
	then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_awpozcon.config
        else
	echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$var/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png
	cp ${PLOTDIR}/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png $COMOUTplots/$var
        elif [ ! -e ${PLOTDIR}/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png ]
	then
	echo "NO PLOT FOR",$var,$region
        fi

	if [ ! -e $COMOUTplots/$var/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png ]
	then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_awpozcon_fbar.config
        else
        echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$var/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png $PLOTDIR
	fi
	
	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png
	cp ${PLOTDIR}/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png $COMOUTplots/$var
        elif [ ! -e ${PLOTDIR}/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png ]
        then
	echo "NO PLOT FOR",$var,$region
        fi

	export var=PMTF
	mkdir -p $COMOUTplots/$var
        export lev=L1
	export lev_obs=A1
        export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
        smvar=pm25
	if [ ! -e $COMOUTplots/$var/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png ]
	then
        sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_pm25.config
        else
	echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$var/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
        mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png
	cp ${PLOTDIR}/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png $COMOUTplots/$var
        elif [ ! -e ${PLOTDIR}/evs.$COMPONENT.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png ]
	then
	echo "NO PLOT FOR",$var,$region
        fi

	if [ ! -e $COMOUTplots/$var/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png ]
	then
        sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_pm25_fbar.config
        else
	echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$var/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
        mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png
	cp ${PLOTDIR}/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png $COMOUTplots/$var
        elif [ ! -e ${PLOTDIR}/evs.$COMPONENT.fbar_obar.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png ]
	then
	echo "NO PLOT FOR",$var,$region
        fi

        done

	for flead in 29 53 77
	do
	export flead
	export var=OZMAX8
	mkdir -p $COMOUTplots/$var
	export lev=L1
	export lev_obs=A8
	export linetype=CTC
	export inithr=06
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

        if [ ! -e $COMOUTplots/$var/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_ozmax8.config
        else
        echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$var/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png
	cp ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png $COMOUTplots/$var
        elif [ ! -e ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	echo "NO PLOT FOR",$var,$region
        fi

        done

	for flead in 23 47 71
	do
	export flead
	export var=OZMAX8
	mkdir $COMOUTplots/$var
	export lev=L1
	export lev_obs=A8
	export linetype=CTC
	export inithr=12
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

	if [ ! -e $COMOUTplots/$var/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_ozmax8.config
	else
        echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$var/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png
	cp ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png $COMOUTplots/$var
        elif [ ! -e ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	echo "NO PLOT FOR",$var,$region
        fi

        done

	for flead in 22 46 70
	do
	export flead
	export var=PMAVE
	mkdir $COMOUTplots/$var
	export lev=A23
	export lev_obs=A1
	export linetype=CTC
	export inithr=06
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

	if [ ! -e $COMOUTplots/$var/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_pmave.config
        else
	echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$var/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png
	cp ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png $COMOUTplots/$var
        elif [ ! -e ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	echo "NO PLOT FOR",$var,$region
        fi

        done

	for flead in 16 40 64
	do
	export flead
	export var=PMAVE
	mkdir $COMOUTplots/$var
	export lev=A23
	export lev_obs=A1
	export linetype=CTC
        export inithr=12
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

	if [ ! -e $COMOUTplots/$var/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_pmave.config
        else
	echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$var/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e $PLOTDIR/aq/*/evs*png ]
	then
	mv $PLOTDIR/aq/*/evs*png ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png
	cp ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png $COMOUTplots/$var
        elif [ ! -e ${PLOTDIR}/evs.$COMPONENT.ctc.${smvar}.${smlev}.last31days.perfdiag_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	echo "NO PLOT FOR",$var,$region
        fi

        done
done

cd ${PLOTDIR}
tar -cvf evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar *png

if [ $SENDCOM = "YES" ]; then
 mkdir -m 775 -p $COMOUTplots
 cp evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar $COMOUTplots
fi

if [ $SENDDBN = YES ] ; then     
 $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar
fi

##
## Headline Plots
##

mkdir $COMOUTplots/headline
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

        # Forecast lead option for init::06z are day1::F29, day2::F53, and day3::F77
        # Forecast lead option for init::12z are day1::F23, day2::F47, and day3::F71
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

        ## selected csi values need to be defined in settings.py ('grid2obs_aq'::'CTC'::'var_dict'::'OZMAX8'::'obs_var_thresholds' and 'fcst_var_thresholds')
	export select_headline_csi="70"
	export select_headline_threshold=">${select_headline_csi}"

	if [ ! -e $COMOUTplots/headline/headline_${COMPONENT}.csi_gt${select_headline_csi}.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_ozmax8_headline.config
        else
	echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/headline/headline_${COMPONENT}.csi_gt${select_headline_csi}.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png ${PLOTDIR_headline}
	fi

	if [ -e ${PLOTDIR_headline}/aq/*/evs*png ]
	then
	mv ${PLOTDIR_headline}/aq/*/evs*png ${PLOTDIR_headline}/headline_${COMPONENT}.csi_gt${select_headline_csi}.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png
	cp ${PLOTDIR_headline}/headline_${COMPONENT}.csi_gt${select_headline_csi}.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png $COMOUTplots/headline
        elif [ ! -e ${PLOTDIR_headline}/headline_${COMPONENT}.csi_gt${select_headline_csi}.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	echo "NO PLOT FOR",$var,$region
        fi

        done
	 
        # Forecast lead option for init::06z are day1::F22, day2::F46, and day3::F70
        # Forecast lead option for init::12z are day1::F16, day2::F40, and day3::F64
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

        ## selected csi values need to be defined in settings.py ('grid2obs_aq'::'CTC'::'var_dict'::'PMAVE'::'obs_var_thresholds' and 'fcst_var_thresholds')
	export select_headline_csi="35"
	export select_headline_threshold=">${select_headline_csi}"

	if [ ! -e $COMOUTplots/headline/headline_${COMPONENT}.csi_gt${select_headline_csi}.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_pmave_headline.config
        else
        echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/headline/headline_${COMPONENT}.csi_gt${select_headline_csi}.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png ${PLOTDIR_headline}
	fi

	if [ -e ${PLOTDIR_headline}/aq/*/evs*png ]
	then
	mv ${PLOTDIR_headline}/aq/*/evs*png ${PLOTDIR_headline}/headline_${COMPONENT}.csi_gt${select_headline_csi}.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png
	cp ${PLOTDIR_headline}/headline_${COMPONENT}.csi_gt${select_headline_csi}.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png $COMOUTplots/headline
        elif [ ! -e ${PLOTDIR_headline}/headline_${COMPONENT}.csi_gt${select_headline_csi}.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png ]
	then
	echo "NO PLOT FOR",$var,$region
        fi

        done
done

cd ${PLOTDIR_headline}
tarfile=evs.plots.${COMPONENT}.${RUN}.headline.last31days.v${VDATE}.tar
tar -cvf ${tarfile} *png

if [ $SENDCOM = "YES" ]; then
 mkdir -m 775 -p ${COMOUTheadline}
 cp ${tarfile} ${COMOUTheadline}
fi

if [ $SENDDBN = YES ] ; then     
  $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.${COMPONENT}.${RUN}.headline.last31days.v${VDATE}.tar
fi

exit



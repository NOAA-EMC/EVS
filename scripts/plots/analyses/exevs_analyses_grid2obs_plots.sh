#!/bin/bash

#################################################################################
# Name of Script: exevs_analyses__grid2obs_plots.sh
# Contact(s):     Perry C. Shafran (perry.shafran@noaa.gov)
# Purpose of Script: This script runs plotting codes to generate plots
#                   of analysis vs first guess for all three analyses 
##################################################################################
 
set -x

# Set up initial directories and initialize variables

mkdir -p $DATA/plots
mkdir -p $DATA/plots/logs
export LOGDIR=$DATA/plots/logs
export LOGFIN=$DATA/logs
mkdir -p $LOGFIN
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

# Bring in past 31 days of stats files

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

	if [ -e ${EVSINanl}/${anl}.${DAY}/evs.stats.${anl}_anl.${RUN}.${VERIF_CASE}.v${DAY}.stat ]
	then
	cp ${EVSINanl}/${anl}.${DAY}/evs.stats.${anl}_anl.${RUN}.${VERIF_CASE}.v${DAY}.stat $STATDIR
	else 
	echo "WARNING: ${EVSINanl}/${anl}.${DAY}/evs.stats.${anl}_anl.${RUN}.${VERIF_CASE}.v${DAY}.stat does not exist"
        fi

        if [ -e ${EVSINanl}/${anl}.${DAY}/evs.stats.${anl}_ges.${RUN}.${VERIF_CASE}.v${DAY}.stat ]
        then
        cp ${EVSINanl}/${anl}.${DAY}/evs.stats.${anl}_ges.${RUN}.${VERIF_CASE}.v${DAY}.stat $STATDIR
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
        else
	echo "WARNING: ${EVSINanl}/${anl}.${DAY}/evs.stats.${anl}_ges.${RUN}.${VERIF_CASE}.v${DAY}.stat does not exist"
        fi

        done

	DATE=`$NDATE -24 $DATE`

done

# Create plot for each region

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

# Plots for temperature and dew point

do
for varb in TMP DPT
do
        mkdir -p $COMOUTplots/$varb	
	export var=${varb}2m
	export region
	export lev=Z2
	export lev_obs=Z2
	export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $varb | tr A-Z a-z`
	if [ ! -e $COMOUTplots/$varb/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png ]
	then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting.config
	cat $LOGDIR/*out
	mv $LOGDIR/*out $LOGFIN
        else
	echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$varb/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e ${PLOTDIR}/sfc_upper/*/evs*png ]
	then
        mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png
	cp ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png $COMOUTplots/$varb
        elif [ ! -e  ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png ]
	then
	echo "WARNING: NO PLOT FOR",$varb,$region,$anl
        fi
done

for varb in WIND

# Plots for wind

do
	mkdir -p $COMOUTplots/$varb
	export var=${varb}10m
	export lev=Z10
	export lev_obs=Z10
        export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
        smvar=`echo $varb | tr A-Z a-z`
	if [ ! -e $COMOUTplots/$varb/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png ]
	then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting.config
        cat $LOGDIR/*out
        mv $LOGDIR/*out $LOGFIN
        else
	echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$varb/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e ${PLOTDIR}/sfc_upper/*/evs*png ]
	then
        mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png
	cp ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png $COMOUTplots/$varb
        elif [ ! -e ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png ]
        then
	echo "WARNING: NO PLOT FOR",$varb,$region,$anl
        fi
done

for varb in GUST

# Plots for wind gust

do
	mkdir -p $COMOUTplots/$varb
	export var=${varb}sfc
	export lev=Z10
	export lev_obs=Z0
	export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
        smvar=`echo $varb | tr A-Z a-z`
	if [ ! -e $COMOUTplots/$varb/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png ]
	then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting.config
        cat $LOGDIR/*out
        mv $LOGDIR/*out $LOGFIN
        else
	echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$varb/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e ${PLOTDIR}/sfc_upper/*/evs*png ]
	then
        mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png
	cp ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png $COMOUTplots/$varb
        elif [ ! -e ${PLOTDIR}/evs.${anl}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.buk_${smregion}.png ]
        then
	echo "WARNING: NO PLOT FOR",$varb,$region,$anl
        fi
done

for varb in VIS CEILING

# Plots for visibility and ceiling

do
	mkdir -p $COMOUTplots/$varb
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
	if [ ! -e $COMOUTplots/$varb/evs.${anl}.ctc.${smvar}_${smlev}.last31days.perfdiag.buk_${smregion}.png ]; then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting.config_perf
        cat $LOGDIR/*out
        mv $LOGDIR/*out $LOGFIN
        else
	echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$varb/evs.${anl}.ctc.${smvar}_${smlev}.last31days.perfdiag.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e ${PLOTDIR}/ceil_vis/*/evs*png ]
	then
	mv ${PLOTDIR}/ceil_vis/*/evs*png ${PLOTDIR}/evs.${anl}.ctc.${smvar}_${smlev}.last31days.perfdiag.buk_${smregion}.png
	cp ${PLOTDIR}/evs.${anl}.ctc.${smvar}_${smlev}.last31days.perfdiag.buk_${smregion}.png $COMOUTplots/$varb
        elif [ ! -e ${PLOTDIR}/evs.${anl}.ctc.${smvar}_${smlev}.last31days.perfdiag.buk_${smregion}.png ]
	then
	echo "WARNING: NO PLOT FOR",$varb,$region,$anl
        fi

	for stat in csi fbias
	do

	export stat

	if [ ! -e $COMOUTplots/$varb/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png ]; then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting.config_thresh
        cat $LOGDIR/*out
        mv $LOGDIR/*out $LOGFIN
        else
	echo "RESTART - plot exists; copying over to plot directory"
	cp $COMOUTplots/$varb/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png $PLOTDIR
	fi

	if [ -e ${PLOTDIR}/ceil_vis/*/evs*png ]
	then
	mv ${PLOTDIR}/ceil_vis/*/evs*png ${PLOTDIR}/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png
	cp ${PLOTDIR}/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png $COMOUTplots/$varb
        elif [ ! -e ${PLOTDIR}/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png ]
	then
	echo "WARNING: NO PLOT FOR",$varb,$region,$anl
        fi

        
        done
done

# Plots for total cloud

        if [ $anl = rtma -o $anl = urma ]
	then
        export var=TCDC
	mkdir -p $COMOUTplots/$var
	export lev=L0
	export lev_obs=L0
	export linetype=CTC
	export thresh=">10,>50,>90"
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $var | tr A-Z a-z`

	for stat in csi ets fbias
	do
	export stat

	if [ ! -e $COMOUTplots/$var/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png ]; then
	sh $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting.config_thresh
        cat $LOGDIR/*out
        mv $LOGDIR/*out $LOGFIN
        else
        echo "RESTART - plot exists; copying over to plot directory"
        cp $COMOUTplots/$var/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png $PLOTDIR
        fi

	if [ -e ${PLOTDIR}/sfc_upper/*/evs*png ]
	then
	mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png
	cp ${PLOTDIR}/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png $COMOUTplots/$var
        elif [ ! -e ${PLOTDIR}/evs.${anl}.${stat}.${smvar}_${smlev}.last31days.threshmean.buk_${smregion}.png ]
	then
	echo "WARNING: NO PLOT FOR",$var,$region,$anl
        fi
        done
        fi

	
done
done

# Tar up plot files and send to com directory

cd ${PLOTDIR}
tar -cvf evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar *png

if [ $SENDCOM = "YES" ]; then
 cpreq -v  evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar $COMOUTplots
fi

if [ $SENDDBN = YES ] ; then     
 $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar
fi


exit





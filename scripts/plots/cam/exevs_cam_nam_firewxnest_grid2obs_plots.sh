#!/bin/bash

set -x

export config=$HOMEevs/parm/evs_config/cam/config.evs.cam_nam_firewxnest.prod
source $config

export machine=${machine:-"WCOSS2"}
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

	echo $DATE > curdate
	DAY=`cut -c 1-8 curdate`
	YEAR=`cut -c 1-4 curdate`
	MONTH=`cut -c 1-6 curdate`
	HOUR=`cut -c 9-10 curdate`

	if [ -e ${EVSINnam}.$DAY/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${DAY}.stat ]
	then
	 cpreq ${EVSINnam}.$DAY/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${DAY}.stat $STATDIR

	 sed "s/$model1/$MODELNAME/g" $STATDIR/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${DAY}.stat > $STATDIR/temp.stat
	 sed "s/FULL/FireWx/g" $STATDIR/temp.stat > $STATDIR/temp2.stat
	 sed "s/TDO/DPT/g" $STATDIR/temp2.stat > $STATDIR/temp3.stat
	 sed "s/MXGS/GUST/g" $STATDIR/temp3.stat > $STATDIR/temp4.stat
	 mv $STATDIR/temp4.stat $STATDIR/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${DAY}.stat
	 rm -f $STATDIR/temp*stat
	fi

	if [ -e $COMIN/stats/$COMPONENT/namnest.$DAY/evs.stats.namnest.${RUN}.${VERIF_CASE}.v${DAY}.stat ]; then
	 cpreq $COMIN/stats/$COMPONENT/namnest.$DAY/evs.stats.namnest.${RUN}.${VERIF_CASE}.v${DAY}.stat $STATDIR
	fi

	if [ -e $COMIN/stats/$COMPONENT/hrrr.$DAY/evs.stats.hrrr.${RUN}.${VERIF_CASE}.v${DAY}.stat ]; then
	 cpreq $COMIN/stats/$COMPONENT/hrrr.$DAY/evs.stats.hrrr.${RUN}.${VERIF_CASE}.v${DAY}.stat $STATDIR
	fi

	DATE=`$NDATE -24 $DATE`

done

for varb in TMP DPT RH
do
	export var=${varb}2m
	export lev=Z2
	export lev_obs=Z2
	export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $varb | tr A-Z a-z`
	export plottyp=lead
	export datetyp=VALID
	$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/cam_nam_firewxnest_plots_py_plotting.config
    export err=$?; err_chk

        mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${MODELNAME}.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean.firewx.png

	export plottyp=valid_hour
	export datetyp=INIT
	$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/cam_nam_firewxnest_plots_py_plotting.config
    export err=$?; err_chk

        mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${MODELNAME}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.firewx.png

	if [ $varb = DPT ]
	then 
		export plottyp=threshold_average
		export datetyp=INIT
		export linetype=CTC
		export stat=fbias
                export thresh=">=277.594, >=283.15, >=288.706, >=294.261"
		$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/cam_nam_firewxnest_plots_py_plotting.config_thresh
        export err=$?; err_chk

		mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${MODELNAME}.fbias.${smvar}_${smlev}.last31days.threshmean.firewx.png
	elif [ $varb = RH ]
	then
		export plottyp=threshold_average
		export datetyp=INIT
		export linetype=CTC
		export stat=fbias
		export thresh="<=15, <=20, <=25, <=30"
		$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/cam_nam_firewxnest_plots_py_plotting.config_thresh
        export err=$?; err_chk

		mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${MODELNAME}.fbias.${smvar}_${smlev}.last31days.threshmean.firewx.png
	fi
done


for varb in UGRD VGRD UGRD_VGRD WIND
do
	export var=${varb}10m
	export lev=Z10
	export lev_obs=Z10
	if [ $var = UGRD_VGRD10m ]
        then
         export linetype=VL1L2
	else
         export linetype=SL1L2
	fi
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $varb | tr A-Z a-z`
	export plottyp=lead
	export datetyp=VALID
	$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/cam_nam_firewxnest_plots_py_plotting.config
    export err=$?; err_chk

        mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${MODELNAME}.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean.firewx.png

	export plottyp=valid_hour
	export datetyp=INIT
	$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/cam_nam_firewxnest_plots_py_plotting.config
    export err=$?; err_chk

	mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${MODELNAME}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.firewx.png

done

for varb in GUST
do
	export var=${varb}sfc
	export lev=Z0
	export lev_obs=Z0
	export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $varb | tr A-Z a-z`
	export plottyp=lead
	export datetyp=VALID
	$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/cam_nam_firewxnest_plots_py_plotting.config
    export err=$?; err_chk

        mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${MODELNAME}.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean.firewx.png

	export plottyp=valid_hour
	export datetyp=INIT
	$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/cam_nam_firewxnest_plots_py_plotting.config
    export err=$?; err_chk

	mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${MODELNAME}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.firewx.png
done

for varb in PBL
do
	export var=${varb}
	export lev=L0
	export lev_obs=L0
	export linetype=SL1L2
	smlev=`echo $lev | tr A-Z a-z`
	smvar=`echo $varb | tr A-Z a-z`
	export plottyp=lead
	export datetyp=VALID
	$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/cam_nam_firewxnest_plots_py_plotting.config_pbl
    export err=$?; err_chk

	mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${MODELNAME}.bcrmse_me.${smvar}_${smlev}.last31days.fhrmean.firewx.png

	export plottyp=valid_hour
	export datetyp=INIT
	$PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/cam_nam_firewxnest_plots_py_plotting.config_pbl
    export err=$?; err_chk

	mv ${PLOTDIR}/sfc_upper/*/evs*png ${PLOTDIR}/evs.${MODELNAME}.bcrmse_me.${smvar}_${smlev}.last31days.vhrmean.firewx.png

done

cd ${PLOTDIR}
tar -cvf evs.plots.${MODELNAME}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar *png

# Cat the plotting log files
log_dir="$DATA/plots/logs"
if [ -d $log_dir ]; then
    log_file_count=$(find $log_dir -type f | wc -l)
    if [[ $log_file_count -ne 0 ]]; then
        log_files=("$log_dir"/*)
        for log_file in "${log_files[@]}"; do
            if [ -f "$log_file" ]; then
                echo "Start: $log_file"
                cat "$log_file"
                echo "End: $log_file"
            fi
        done
    fi
fi
        
if [ $SENDCOM = "YES" ]; then
 if [ -s evs.plots.${MODELNAME}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar ]; then
  cp -v evs.plots.${MODELNAME}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar $COMOUTplots
 fi
fi

if [ $SENDDBN = YES ] ; then
  $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.${MODELNAME}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar
fi


exit



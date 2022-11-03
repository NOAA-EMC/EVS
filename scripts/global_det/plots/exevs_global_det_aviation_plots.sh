#!/bin/sh
########################################################################################
# Name of Script: exevs_global_det_aviation_plots.sh
# Purpose of Script: To plot the verification products for WAFS verification
# Arguments: exevs_global_det_aviation_plots.sh
#   
########################################################################################

set -x 

msg="WAFS g2g verification job HAS BEGUN"
echo $msg

export VALID_END=$VDATE
export VALID_BEG=`date -d "$VDATE - $NDAYS days" +%Y%m%d`

export DATAplot=$DATA/plot
mkdir -p $DATAplot

export EVAL_PERIOD="LAST${NDAYS}DAYS"
eval_period=`echo $EVAL_PERIOD | tr [:upper:] [:lower:]`

################################################
# Part 1: Icing Verification
################################################
export OBSERVATION=GCIP
export LINE_TYPE="ctc"
export CENTERS="blend us uk"

PLOT_TYPES="roc_curve fbias"

resolutions="0P25"
for RESOLUTION in $resolutions ; do
    export RESOLUTION
    source $HOMEevs/parm/evs_config/global_det/config.evs.stats.global_det.aviation.standalone

    export OUTPUT_BASE_DIR=$DATA/datainput/${OBSERVATION}_${RESOLUTION}
    mkdir -p $OUTPUT_BASE_DIR
    rm $OUTPUT_BASE_DIR/*

    for CENTER in $CENTERS ; do
#	# Re-organize data for plotting
	n=0
	while [[ $n -le $NDAYS ]] ; do
	    day=`date -d "$VDATE - $n days" +%Y%m%d`
	    sourefile=$COMINstat/${MODELNAME}.$day/$NET.stats.$MODELNAME.$RUN.$VERIF_CASE.v$day.stat
	    if [[ -f "$sourefile" ]] ; then
		ln -s $sourefile $OUTPUT_BASE_DIR/.
	    fi
	    n=$((n+1))
	done
    done

    cd $DATA    

    for PLOT_TYPE in $PLOT_TYPES ; do
	export PLOT_TYPE
	if [[ $PLOT_TYPE = "roc_curve" ]] ; then
	    export STATS="farate,pod"
	elif [[ $PLOT_TYPE = "fbias" ]] ; then
	    export STATS="fbias"
	fi
	# Set the config and run python scripts to generate plots
	sh $HOMEevs/parm/evs_config/global_det/config.evs.plots.global_det.aviation
    done
done

cd $DATAplot
tar -cvf $COMOUT/$NET.$STEP.${COMPONENT}.${RUN}.${VERIF_CASE}.$eval_period.v${VDATE}.tar *png

################################################
# Part 2: U/V/T Verification
################################################
export OBSERVATION=GFS
export CENTERS="gfs"

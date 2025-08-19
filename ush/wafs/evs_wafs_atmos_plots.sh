#!/bin/bash
########################################################################################
# Name of Script: exevs_wafs_atmos_plots.sh
# Purpose of Script: To plot the verification products for WAFS verification
# Arguments: exevs_wafs_atmos_plots.sh
#   
########################################################################################
# OBSERVATION  CENTERS        RESOLUTION  PLOT_TYPE    ||  LINE_TYPE  STAT
# GCIP         "blend us uk"  1.25        roc_curve    ||  ctc        "farate,pod"
#                                         fbias        ||  ctc        "fbias"
#                             0.25        roc_curve    ||  ctc        "farate,pod"
#                                         fbias        ||  ctc        "fbias"
# GFS          "gfs"          1.25        time_series  ||  SL1L2      "rmse"
#                                         time_series  ||  VCNT       "dir_rmse"

set -x 

msg="WAFS g2g verification job HAS BEGUN"
echo $msg

export OBSERVATION=$1
export NDAYS=$2
export RESOLUTION=$3
export VAR=$4
export PLOT_TYPE=$5
export VX_MASK_LIST=$6
if [ $7 != 'all' ] ; then
    export FHOURS=$7
fi

export VALID_END=$VDATE
export VALID_BEG=`date -d "$VDATE - $NDAYS days" +%Y%m%d`

export EVAL_PERIOD="LAST${NDAYS}DAYS"

################################################
# Part 1: Icing Verification
################################################
if [ $OBSERVATION = "GCIP" ] ; then
    # export CENTERS="blend us uk"
    export CENTERS="blend"
################################################
# Part 2: U/V/T Verification
################################################
else
    export CENTERS="gfs"
fi

resolution=`echo $RESOLUTION | tr '[:upper:]' '[:lower:]'`
    
if [ $VX_MASK_LIST = 'GLB' ] ; then
    if [ $RESOLUTION = "0P25" ] ; then
	export VX_MASK_LIST="G193"
    elif [ $RESOLUTION = "1P25" ] ; then
	export VX_MASK_LIST="G045"
    fi
fi
    
export OUTPUT_BASE_DIR=$DATA/datainput/${OBSERVATION}_${RESOLUTION}_$VAR
mkdir -p $OUTPUT_BASE_DIR

source $HOMEevs/parm/evs_config/wafs/config.evs.wafs.standalone
export FHOURS_EVSlist=${FHOURS_EVSlist:-${FHOURS// /, }}
    
if [ $OBSERVATION = "GCIP" ] ; then
    stat_file_suffix="$VAR"
    export LINE_TYPE="CTC"
elif [ $OBSERVATION = "GFS" ] ; then
    stat_file_suffix="$VAR$resolution"
    if [ $VAR = 'uvt' ] ; then
	export LINE_TYPE="SL1L2"
    elif [ $VAR = 'wdir' ] ; then
	export LINE_TYPE="VCNT"
    fi
fi

cd $DATA    

# Re-organize data for plotting
n=0
while [[ $n -le $NDAYS ]] ; do
    day=`date -d "$VDATE - $n days" +%Y%m%d`
    if [ $VDATE -ne $PDYm1 ] ; then
	yyyy=`echo $day | cut -c 1-4`
	sourcefile=$COMIN/$yyyy/$NET.stats.$MODELNAME.$RUN.${VERIF_CASE}_${stat_file_suffix}.v$day.stat
    else
	sourcefile=$COMIN/stats/$COMPONENT/$COMPONENT.$day/$NET.stats.$MODELNAME.$RUN.${VERIF_CASE}_${stat_file_suffix}.v$day.stat
    fi
    targetfile=$OUTPUT_BASE_DIR/$NET.stats.$MODELNAME.$RUN.${VERIF_CASE}_${stat_file_suffix}.v$day.stat
    if [[ ! -f "$targetfile" ]] ; then
	if [[ -f "$sourcefile" ]] ; then
	    ln -sf $sourcefile $OUTPUT_BASE_DIR/.
	fi
    fi
    n=$((n+1))
done

if [[ $PLOT_TYPE = "roc_curve" ]] ; then
    export STATS="farate,pod"
elif [[ $PLOT_TYPE = "fbias" ]] ; then
    export STATS="fbias"
elif [[ $PLOT_TYPE = "time_series" ]] ; then
    export STATS="rmse"
    if [ $VAR = "wdir" ] ; then
	export STATS="dir_rmse"
    fi
fi
# Set the config and run python scripts to generate plots
$HOMEevs/parm/evs_config/wafs/config.evs.plots.wafs.atmos
export err=$?; err_chk


#####################################################################
# GOOD RUN
echo "********USH SCRIPT evs_wafs_atmos_plots.sh $1 $2 $3 COMPLETED NORMALLY"

#####################################################################

############## END OF SCRIPT #######################

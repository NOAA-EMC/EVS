#! /bin/sh
########################################################################################
# Name of Script: exevs_global_det_aviation_stats.sh
# Purpose of Script: To generate the verification products for WAFS verification
# Arguments: exevs_global_det_aviation_stats.sh
#   
########################################################################################
set -x

cd $DATA

msg="WAFS g2g verification job HAS BEGUN"
echo $msg

################################################
# Part 1: Icing Verification
################################################
export OBSERVATION=GCIP
resolutions="0P25 1P25"
export CENTERS="blend us uk"

for RESOLUTION in $resolutions ; do
    export RESOLUTION

    export STAT_ANALYSIS_OUTPUT_DIR=$DATA/${MODELNAME}_${RESOLUTION}_stat
    export INPUT_BASE=$DATA/${MODELNAME}_${RESOLUTION}
    rm -rf $INPUT_BASE
    mkdir -p $INPUT_BASE
    
    source $HOMEevs/parm/evs_config/global_det/config.evs.stats.global_det.aviation.standalone

    if [ $RESOLUTION = "0P25" ] ; then
	sed "s|.*_VAR2_.*|#|" $PARMevs/$STEP/GridStat_fcstWAFS_obs${OBSERVATION}.conf > GridStat_fcstWAFS_obs${OBSERVATION}.conf
    else
	cp $PARMevs/$STEP/GridStat_fcstWAFS_obs${OBSERVATION}.conf .
    fi
    for CENTER in $CENTERS ; do
	export CENTER
	# Prepare data
	sh $USHevs/evs_global_det_aviation_stats.sh

	${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $DATA/GridStat_fcstWAFS_obs${OBSERVATION}.conf

	${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $PARMevs/$STEP/StatAnalysis_fcstWAFS_obs${OBSERVATION}_GatherbyDay.conf
    done

    stat_file_suffix=`echo $VAR1_NAME | sed -e "s|mean||" -e "s|max||" | tr '[:upper:]' '[:lower:]'`
    cat $STAT_ANALYSIS_OUTPUT_DIR/* > ${MODELNAME}_${RESOLUTION}.stat
    awk '!seen[$0]++' ${MODELNAME}_${RESOLUTION}.stat > $COMOUTfinal/$NET.$STEP.$MODELNAME.$RUN.${VERIF_CASE}_${stat_file_suffix}.v$VDATE.stat
done


################################################
# Part 2: U/V/T Verification
################################################
export OBSERVATION=GFS
resolutions="1P25"
export CENTERS="gfs"

for RESOLUTION in $resolutions ; do
    export RESOLUTION

    export STAT_ANALYSIS_OUTPUT_DIR=$DATA/${MODELNAME}_${RESOLUTION}_stat
    export INPUT_BASE=$DATA/${MODELNAME}_${RESOLUTION}
    rm -rf $INPUT_BASE
    mkdir -p $INPUT_BASE

    source $HOMEevs/parm/evs_config/global_det/config.evs.stats.global_det.${RUN}.standalone
done

#####################################################################
# GOOD RUN
echo "********SCRIPT exevs_global_det_aviation_stats.sh COMPLETED NORMALLY on `date`"
exit 0
#####################################################################

############## END OF SCRIPT #######################


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

export OBSERVATION=$1

################################################
# Part 1: Icing Verification
################################################
if [ $OBSERVATION = "GCIP" ] ; then
    export CENTERS="blend us uk"
    resolutions="0P25 1P25"
################################################
# Part 2: U/V/T Verification
################################################
elif [ $OBSERVATION = "GFS" ] ; then
    export CENTERS="gfs"
    resolutions="1P25"
fi

for RESOLUTION in $resolutions ; do
    export RESOLUTION
    resolution=`echo $RESOLUTION | tr '[:upper:]' '[:lower:]'`

    export GRID_STAT_INPUT_BASE=$DATA/${OBSERVATION}_${RESOLUTION}_data
    mkdir -p $GRID_STAT_INPUT_BASE
    
    export STAT_ANALYSIS_OUTPUT_DIR=$DATA/${OBSERVATION}_${RESOLUTION}_stat

    source $HOMEevs/parm/evs_config/global_det/config.evs.stats.global_det.aviation.standalone

    if [[ $RESOLUTION = "0P25" ]] && [[ $OBSERVATION = "GCIP" ]] ; then
	sed "s|.*_VAR2_.*|#|" $PARMevs/$STEP/GridStat_fcstWAFS_obs${OBSERVATION}.conf > GridStat_fcstWAFS_obs${OBSERVATION}_${RESOLUTION}.conf
    else
	cp $PARMevs/$STEP/GridStat_fcstWAFS_obs${OBSERVATION}.conf GridStat_fcstWAFS_obs${OBSERVATION}_${RESOLUTION}.conf
    fi
    for CENTER in $CENTERS ; do
	export CENTER
	# Prepare data
	sh $USHevs/evs_global_det_aviation_stats.sh
	
	${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $DATA/GridStat_fcstWAFS_obs${OBSERVATION}_${RESOLUTION}.conf

	${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $PARMevs/$STEP/StatAnalysis_fcstWAFS_obs${OBSERVATION}_GatherbyDay.conf

	#===================================================================================================#
	#========== Turn off Wind Direction verification until its RMSE gets supported by METplus ==========#
	#if [ $OBSERVATION = "GFS" ] ; then
	#    # Do wind direction verification separately
	#    ${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $PARMevs/$STEP/GridStat_fcstWAFS_obs${OBSERVATION}wdir.conf
	#    ${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $PARMevs/$STEP/StatAnalysis_fcstWAFS_obs${OBSERVATION}wdir_GatherbyDay.conf
	#    cat $STAT_ANALYSIS_OUTPUT_DIR/wdir_${RESOLUTION}.* > $COMOUTfinal/$NET.$STEP.$MODELNAME.$RUN.${VERIF_CASE}_wdir$resolution.v$VDATE.stat
	#fi
	#===================================================================================================#
    done

    if [ $OBSERVATION = "GCIP" ] ; then
	stat_file_suffix=`echo $VAR1_NAME | sed -e "s|mean||" -e "s|max||" | tr '[:upper:]' '[:lower:]'`
    elif [ $OBSERVATION = "GFS" ] ; then
	stat_file_suffix='uvt'$resolution
    fi
    # Non wind direction variables:
    tmpfile=${OBSERVATION}_${RESOLUTION}.stat
    cat $STAT_ANALYSIS_OUTPUT_DIR/${RESOLUTION}.* > $tmpfile
    sed '/>=/s/WIND/WIND80/g' -i $tmpfile
    awk '!seen[$0]++' $tmpfile > $COMOUTfinal/$NET.$STEP.$MODELNAME.$RUN.${VERIF_CASE}_${stat_file_suffix}.v$VDATE.stat
done

#####################################################################
# GOOD RUN
echo "********SCRIPT exevs_global_det_aviation_stats.sh COMPLETED NORMALLY on `date`"
exit 0
#####################################################################

############## END OF SCRIPT #######################


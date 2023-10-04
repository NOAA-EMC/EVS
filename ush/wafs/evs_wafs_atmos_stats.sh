#! /bin/bash
########################################################################################
# Name of Script: exevs_wafs_atmos_stats.sh
# Purpose of Script: To generate the verification products for WAFS verification
# Arguments: exevs_wafs_atmos_stats.sh
#   
########################################################################################
set -x

cd $DATA

msg="WAFS g2g verification job HAS BEGUN"
echo $msg

export OBSERVATION=$1
export RESOLUTION=$2
export CENTER=$3

resolution=`echo $RESOLUTION | tr '[:upper:]' '[:lower:]'`

export GRID_STAT_INPUT_BASE=$DATA/${OBSERVATION}_${RESOLUTION}_data
mkdir -p $GRID_STAT_INPUT_BASE
    
export STAT_ANALYSIS_OUTPUT_DIR=$DATA/${OBSERVATION}_${RESOLUTION}_${CENTER}_stat

source $HOMEevs/parm/evs_config/wafs/config.evs.wafs.standalone

cp $PARMevs/GridStat_fcstWAFS_obs${OBSERVATION}.conf GridStat_fcstWAFS_obs${OBSERVATION}_${RESOLUTION}.conf

# Prepare data
$USHevs/evs_wafs_atmos_stats_preparedata.sh

# run stat files
${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $DATA/GridStat_fcstWAFS_obs${OBSERVATION}_${RESOLUTION}.conf
${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $PARMevs/StatAnalysis_fcstWAFS_obs${OBSERVATION}_GatherbyDay.conf

	#===================================================================================================#
	#========== Turn off Wind Direction verification until its RMSE gets supported by METplus ==========#
	#if [ $OBSERVATION = "GFS" ] ; then
	#    # Do wind direction verification separately
	#    ${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $PARMevs/GridStat_fcstWAFS_obs${OBSERVATION}wdir.conf
	#    ${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $PARMevs/StatAnalysis_fcstWAFS_obs${OBSERVATION}wdir_GatherbyDay.conf
	#    cat $STAT_ANALYSIS_OUTPUT_DIR/wdir_${RESOLUTION}.* > $COMOUTfinal/$NET.$STEP.$MODELNAME.$RUN.${VERIF_CASE}_wdir$resolution.v$VDATE.stat
	#fi
	#===================================================================================================#


if [ $OBSERVATION = "GCIP" ] ; then
    stat_file_suffix=`echo $VAR1_NAME | tr '[:upper:]' '[:lower:]'`
elif [ $OBSERVATION = "GFS" ] ; then
    stat_file_suffix='uvt'$resolution
fi
# Non wind direction variables:
# remove duplicate lines and keep the first one
if [ $OBSERVATION = "GFS" ] ; then
    sed '/>=/s/WIND/WIND80/g' $STAT_ANALYSIS_OUTPUT_DIR/* > $STATSOUTfinal/$NET.$STEP.$MODELNAME.$RUN.${VERIF_CASE}_${stat_file_suffix}.v$VDATE.stat
else
    cat $STAT_ANALYSIS_OUTPUT_DIR/* > $DATAsemifinal/${CENTER}_${RESOLUTION}.$NET.$STEP.$MODELNAME.$RUN.${VERIF_CASE}_${stat_file_suffix}.v$VDATE.stat
fi

#####################################################################
# GOOD RUN
echo "********SCRIPT exevs_wafs_atmos_stats.sh COMPLETED NORMALLY on `date`"
exit 0
#####################################################################

############## END OF SCRIPT #######################


#! /bin/bash
########################################################################################
# Name of Script: exevs_wafs_atmos_stats.sh
# Purpose of Script: To generate the verification products for WAFS verification
# Arguments: exevs_wafs_atmos_stats.sh
#   
########################################################################################
set -x

msg="WAFS g2g verification job HAS BEGUN"
echo $msg

export OBSERVATION=$1
export RESOLUTION=$2
export CENTER=$3

export DATAmpmd=$DATA/$OBSERVATION.$RESOLUTION.$CENTER
mkdir -p $DATAmpmd
cd $DATAmpmd

resolution=`echo $RESOLUTION | tr '[:upper:]' '[:lower:]'`

export GRID_STAT_INPUT_BASE=$DATAmpmd/${OBSERVATION}_${RESOLUTION}_data
mkdir -p $GRID_STAT_INPUT_BASE

# STAT_ANALYSIS_OUTPUT_DIR is defined in config.evs.wafs.standalone, and created & used by StatAnalysis_fcstWAFS*
source $HOMEevs/parm/evs_config/wafs/config.evs.wafs.standalone

cp $PARMevs/GridStat_fcstWAFS_obs${OBSERVATION}.conf GridStat_fcstWAFS_obs${OBSERVATION}_${RESOLUTION}.conf

inithours=${FCST_VALID_HOUR//,/ }

# run stat files
for cc in $inithours ; do
    export cc
    # Prepare data and re-define FHOURS_EVSlist  based on the availability for each verification hour
    sh $USHevs/evs_wafs_atmos_stats_preparedata.sh
done

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
if [ -d $STAT_ANALYSIS_OUTPUT_DIR ] ; then
    if [ $OBSERVATION = "GFS" ] ; then
	sed '/>=/s/WIND/WIND80/g' $STAT_ANALYSIS_OUTPUT_DIR/* > $STATSOUTfinal/$NET.$STEP.$MODELNAME.$RUN.${VERIF_CASE}_${stat_file_suffix}.v$VDATE.stat
    else
	cat $STAT_ANALYSIS_OUTPUT_DIR/* > $DATAsemifinal/${CENTER}_${RESOLUTION}.$NET.$STEP.$MODELNAME.$RUN.${VERIF_CASE}_${stat_file_suffix}.v$VDATE.stat
    fi
fi

#####################################################################
# GOOD RUN
echo "********SCRIPT exevs_wafs_atmos_stats.sh COMPLETED NORMALLY on `date`"
#####################################################################

############## END OF SCRIPT #######################


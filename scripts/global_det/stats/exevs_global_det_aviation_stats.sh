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
resolutions="0P25"
export CENTERS="blend us uk"

for RESOLUTION in $resolutions ; do
    export RESOLUTION

    export INPUT_BASE=$DATA/${MODELNAME}_${RESOLUTION}
    rm -rf $INPUT_BASE
    mkdir -p $INPUT_BASE
    
    source $HOMEevs/parm/evs_config/global_det/config.evs.stats.global_det.aviation.standalone

    for CENTER in $CENTERS ; do
	export CENTER
	# Prepare data
	sh $USHevs/evs_global_det_aviation_stats.sh

	${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $PARMevs/$STEP/GridStat_fcstWAFS_obs${OBSERVATION}.conf
    done
    
done

for RESOLUTION in $resolutions ; do
    export RESOLUTION
    for CENTER in $CENTERS ; do
	export CENTER
	${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $PARMevs/$STEP/StatAnalysis_fcstWAFS_obs${OBSERVATION}_GatherbyDay.conf
    done
done

cat $DATA/${MODELNAME}_stat/* > ${MODELNAME}.stat
awk '!seen[$0]++' ${MODELNAME}.stat > $COMOUTfinal/$NET.$STEP.$MODELNAME.$RUN.$VERIF_CASE.v$VDATE.stat

################################################
# Part 2: U/V/T Verification
################################################
export OBSERVATION=GFS
export CENTERS="gfs"

source $HOMEevs/parm/evs_config/global_det/config.evs.stats.global_det.${RUN}.standalone

#####################################################################
# GOOD RUN
echo "********SCRIPT exevs_global_det_aviation_stats.sh COMPLETED NORMALLY on `date`"
exit 0
#####################################################################

############## END OF SCRIPT #######################


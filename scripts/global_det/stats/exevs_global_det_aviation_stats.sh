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

export MODEL=$MODELNAME

################################################
# Part 1: Icing Verification
################################################
export OBSERVATION=GCIP
resolutions="0P25"
for RESOLUTION in $resolutions ; do
    export RESOLUTION
    source $HOMEevs/parm/evs_config/global_det/config.evs.stats.global_det.${RUN}.standalone
    
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


################################################
# Part 2: U/V/T Verification
################################################
export OBSERVATION=GFS
source $HOMEevs/parm/evs_config/global_det/config.evs.stats.global_det.${RUN}.standalone

#####################################################################
# GOOD RUN
echo "********SCRIPT exevs_global_det_aviation_stats.sh COMPLETED NORMALLY on `date`"
exit 0
#####################################################################

############## END OF SCRIPT #######################


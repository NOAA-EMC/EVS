#!/bin/ksh
set -x

export WORK=$DATA

cd $WORK

export MET_bin_exec='bin'
export log_met_output_to_metplus=''
export metplus_verbosity=2
export met_verbosity=2


export get_anl=${get_anl:-'yes'}
export get_prepbufr=${get_prepbufr:-'yes'}
export get_ccpa=${get_ccpa:-'yes'}
export get_gefs=${get_gefs:-'yes'}
export get_ecme=${get_ecme:-'yes'}
export get_cmce=${get_cmce:-'yes'}
export get_gefs_apcp06h=${get_gefs_apcp06h:-'yes'}
export get_cmce_apcp06h=${get_cmce_apcp06h:-'yes'}
export get_ecme_apcp06h=${get_ecme_apcp06h:-'yes'}
export get_gefs_apcp24h=${get_gefs_apcp24h:-'yes'}
export get_cmce_apcp24h=${get_cmce_apcp24h:-'yes'}
export get_ecme_apcp24h=${get_ecme_apcp24h:-'yes'}
export get_nohrsc24h=${get_nohrsc24h:-'yes'}

export vday=$INITDATE

export run_mpi=${run_mpi:-'yes'}


export CLIMO=$FIXevs/climos/atmos
export MASKS=$FIXevs/mask

export COMOUT_gefs=${COMOUT}.${INITDATE}/gefs
export COMOUT_cmce=${COMOUT}.${INITDATE}/cmce
export COMOUT_ecme=${COMOUT}.${INITDATE}/ecme
mkdir -p $COMOUT_gefs
mkdir -p $COMOUT_cmce
mkdir -p $COMOUT_ecme


export GRID2GRID_CONF=$PARMevs/metplus_config/${COMPONENT}/${RUN}_grid2grid/stats
export GRID2OBS_CONF=$PARMevs/metplus_config/${COMPONENT}/${RUN}_grid2obs/stats
export ENS_LIST=$PARMevs/metplus_config/${COMPONENT}/${RUN}_${grid2grid}/prep


#$USHevs/global_ens/evs_get_gens_atmos_data.sh nohrsc24h
$USHevs/global_ens/evs_get_gens_atmos_data.sh ecme_snow24h

exit

if [ $get_anl = yes ] ; then
 $USHevs/global_ens/evs_get_gens_atmos_data.sh gfsanl
 $USHevs/global_ens/evs_get_gens_atmos_data.sh cmcanl
fi

if [ $get_prepbufr = yes ] ; then
 $USHevs/global_ens/evs_get_gens_atmos_data.sh prepbufr
fi


if [ $get_ccpa = yes ] ; then
 $USHevs/global_ens/evs_get_gens_atmos_data.sh ccpa
fi

if [ $get_nohrsc24h = yes ] ; then
 $USHevs/global_ens/evs_get_gens_atmos_data.sh nohrsc24h 
fi



#get ensemble member data by sequentail(non-mpi) or mpi run
$USHevs/global_ens/evs_global_ens_atmos_prep.sh




msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0

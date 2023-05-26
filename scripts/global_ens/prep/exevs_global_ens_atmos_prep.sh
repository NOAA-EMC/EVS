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
export get_naefs=${get_naefs:-'no'}
export get_gefs_apcp06h=${get_gefs_apcp06h:-'no'}
export get_cmce_apcp06h=${get_cmce_apcp06h:-'yes'}
export get_ecme_apcp06h=${get_ecme_apcp06h:-'no'}
export get_gefs_apcp24h=${get_gefs_apcp24h:-'yes'}
export get_cmce_apcp24h=${get_cmce_apcp24h:-'yes'}
export get_ecme_apcp24h=${get_ecme_apcp24h:-'yes'}
export get_gefs_snow24h=${get_gefs_snow24h:-'yes'}
export get_cmce_snow24h=${get_cmce_snow24h:-'yes'}
export get_ecme_snow24h=${get_ecme_snow24h:-'yes'}
export get_nohrsc24h=${get_nohrsc24h:-'yes'}
export get_gefs_icec=${get_gefs_icec:-'yes'}
export get_gefs_icec24h=${get_gefs_icec24h:-'yes'}
export get_gfs=${get_gfs:-'yes'}
export get_osi_saf=${get_osi_saf:-'yes'}
export get_forecast=${get_forecast:-'yes'}
export get_ghrsst=${get_ghrsst:-'yes'}
export get_gefs_sst24h=${get_gefs_sst24h:-'yes'}

export vday=$INITDATE

export run_mpi=${run_mpi:-'yes'}


export CLIMO=$FIXevs/climos/atmos
export MASKS=$FIXevs/mask

export COMOUT_gefs=${COMOUT}.${INITDATE}/gefs
export COMOUT_cmce=${COMOUT}.${INITDATE}/cmce
export COMOUT_ecme=${COMOUT}.${INITDATE}/ecme
export COMOUT_naefs=${COMOUT}
export COMOUT_osi_saf=${COMOUT}.${INITDATE}/osi_saf
mkdir -p $COMOUT_gefs
mkdir -p $COMOUT_cmce
mkdir -p $COMOUT_ecme
mkdir -p $COMOUT_osi_saf


export GRID2GRID_CONF=$PARMevs/metplus_config/${COMPONENT}/${RUN}_grid2grid/stats
export GRID2OBS_CONF=$PARMevs/metplus_config/${COMPONENT}/${RUN}_grid2obs/stats
export ENS_LIST=$PARMevs/metplus_config/${COMPONENT}/atmos_grid2grid/prep
export CONF_PREP=$PARMevs/metplus_config/${COMPONENT}/atmos_grid2grid/prep

if [ $get_gfs = yes ] ; then
 $USHevs/global_ens/evs_get_gens_atmos_data.sh gfs
fi

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

if [ $get_ghrsst = yes ] ; then
  #cp $COMINsst/$vday/validation_data/marine/ghrsst/${vday}120000-UKMO-L4_GHRSST-SSTfnd-GMPE-GLOB-v03.0-fv03.0.nc $COMOUT_gefs/ghrsst.t00z.nc
  if [ -s $COMINsst/$vday/validation_data/marine/ghrsst/${vday}_OSPO_L4_GHRSST.nc ] ; then
    cp $COMINsst/$vday/validation_data/marine/ghrsst/${vday}_OSPO_L4_GHRSST.nc $COMOUT_gefs/ghrsst.t00z.nc
  else
     export subject="GHRSST OSPO Data Missing for EVS ${COMPONENT}"
     export maillist=${maillist:-'geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'}
     echo "Warning: No GHRSST OSPO data was available for valid date ${vday}" > mailmsg
     echo Missing file is  $COMINsst/$vday/validation_data/marine/ghrsst/${vday}_OSPO_L4_GHRSST.nc >> mailmsg
     echo "Job ID: $jobid" >> mailmsg
     cat mailmsg | mail -s "$subject" $maillist 
  fi
fi

#get_gefs_icec24h
#if [ $get_gefs_icec = yes ] || [ $test_icec = yes ] ; then
#  $USHevs/global_ens/evs_get_gens_atmos_data.sh gefs_icec24h 
#  $USHevs/global_ens/evs_get_gens_atmos_data.sh gefs_icec7day
#exit 
#fi


#if [ $get_gefs_snow24h = yes ] ; then
#just for testing  
#  $USHevs/global_ens/evs_get_gens_atmos_data.sh gefs_snow24h 
#  exit
#fi


#if [ $get_gefs_sst24h = yes ] ; then
#  $USHevs/global_ens/evs_get_gens_atmos_data.sh gefs_sst24h
#  exit
#fi

if [ $get_osi_saf = yes ] ; then 
 export MODELNAME=""
 export OBSNAME="osi_saf"
 export COMINcfs=
 export COMINcmc=
 export COMINcmc_precip=
 export COMINcmc_regional_precip=
 export COMINdwd_precip=
 export COMINecmwf=
 export COMINecmwf_precip=
 export COMINfnmoc=
 export COMINimd=
 export COMINjma=
 export COMINjma_precip=
 export COMINmetfra_precip=
 export COMINukmet=
 export COMINukmet_precip=
 export COMINosi_saf=${COMINosi_saf:-/lfs/h1/ops/dev/dcom}

 $USHevs/global_ens/evs_get_gens_atmos_data.sh osi_saf
 export MODELNAME=gefs

fi

#get ensemble member data by sequentail(non-mpi) or mpi run
if [ $get_forecast = yes ] ; then
 $USHevs/global_ens/evs_global_ens_atmos_prep.sh
fi


if [ $get_naefs = yes ] ; then
 $USHevs/global_ens/evs_gens_atmos_g2g_prep_naefs.sh
fi



msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0

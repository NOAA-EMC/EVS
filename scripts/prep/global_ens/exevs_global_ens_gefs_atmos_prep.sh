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



export GRID2GRID_CONF=$PARMevs/metplus_config/stats/${COMPONENT}/${RUN}_grid2grid
export GRID2OBS_CONF=$PARMevs/metplus_config/stats/${COMPONENT}/${RUN}_grid2obs
export ENS_LIST=$PARMevs/metplus_config/prep/${COMPONENT}/atmos_grid2grid
export CONF_PREP=$PARMevs/metplus_config/prep/${COMPONENT}/atmos_grid2grid

if [ $get_gfs = yes ] ; then
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh gfs
fi

if [ $get_anl = yes ] ; then
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh gfsanl
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh cmcanl
fi

if [ $get_prepbufr = yes ] ; then
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh prepbufr
fi


if [ $get_ccpa = yes ] ; then
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh ccpa
fi

if [ $get_nohrsc24h = yes ] ; then
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh nohrsc24h 
fi

if [ $get_ghrsst = yes ] ; then
  #[[ $SENDCOM="YES" ]] && cp $COMINsst/$vday/validation_data/marine/ghrsst/${vday}120000-UKMO-L4_GHRSST-SSTfnd-GMPE-GLOB-v03.0-fv03.0.nc $COMOUT_gefs/ghrsst.t00z.nc
  if [ -s $COMINsst/$vday/validation_data/marine/ghrsst/${vday}_OSPO_L4_GHRSST.nc ] ; then
    [[ $SENDCOM="YES" ]] && cp $COMINsst/$vday/validation_data/marine/ghrsst/${vday}_OSPO_L4_GHRSST.nc $COMOUT_gefs/ghrsst.t00z.nc
  else
    if [ $SENDMAIL = YES ]; then
     export subject="GHRSST OSPO Data Missing for EVS ${COMPONENT}"
     export maillist=${maillist:-'alicia.bentley@noaa.gov,steven.simon@noaa.gov'}
     echo "Warning: No GHRSST OSPO data was available for valid date ${vday}" > mailmsg
     echo Missing file is  $COMINsst/$vday/validation_data/marine/ghrsst/${vday}_OSPO_L4_GHRSST.nc >> mailmsg
     echo "Job ID: $jobid" >> mailmsg
     cat mailmsg | mail -s "$subject" $maillist
    fi 
  fi
fi

#get_gefs_icec24h
#if [ $get_gefs_icec = yes ] || [ $test_icec = yes ] ; then
#  $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh gefs_icec24h 
#  $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh gefs_icec7day
#exit 
#fi


#if [ $get_gefs_snow24h = yes ] ; then
#just for testing  
#  $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh gefs_snow24h 
#  exit
#fi


#if [ $get_gefs_sst24h = yes ] ; then
#  $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh gefs_sst24h
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
 export COMINosi_saf=${COMINosi_saf:-$DCOMROOT}

 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh osi_saf
 export MODELNAME=gefs

fi

#get ensemble member data by sequentail(non-mpi) or mpi run
if [ $get_forecast = yes ] ; then
 $USHevs/${COMPONENT}/evs_global_ens_${RUN}_prep.sh
fi


if [ $get_naefs = yes ] ; then
 $USHevs/${COMPONENT}/evs_gens_${RUN}_g2g_prep_naefs.sh
fi



msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"




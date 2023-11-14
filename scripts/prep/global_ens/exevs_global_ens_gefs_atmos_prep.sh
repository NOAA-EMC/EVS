#!/bin/ksh
set -x

export WORK=$DATA

cd $WORK

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
 export err=$?; err_chk
fi

if [ $get_anl = yes ] ; then
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh gfsanl
 export err=$?; err_chk
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh cmcanl
 export err=$?; err_chk
fi

if [ $get_prepbufr = yes ] ; then
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh prepbufr
 export err=$?; err_chk
fi

if [ $get_ccpa = yes ] ; then
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh ccpa
 export err=$?; err_chk
fi

if [ $get_nohrsc24h = yes ] ; then
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh nohrsc24h
 export err=$?; err_chk
fi

if [ $get_ghrsst = yes ] ; then
  if [ -s $DCOMINghrsst/$vday/validation_data/marine/ghrsst/${vday}_OSPO_L4_GHRSST.nc ] ; then
     cpreq -v $DCOMINghrsst/$vday/validation_data/marine/ghrsst/${vday}_OSPO_L4_GHRSST.nc $WORK/ghrsst.t00z.nc
     [[ $SENDCOM=YES ]] && cpreq -v $WORK/ghrsst.t00z.nc $COMOUTgefs/ghrsst.t00z.nc
  else
    if [ $SENDMAIL = YES ]; then
     export subject="GHRSST OSPO Data Missing for EVS ${COMPONENT}"
     export MAILTO=${MAILTO:-'alicia.bentley@noaa.gov,steven.simon@noaa.gov'}
     echo "Warning: No GHRSST OSPO data was available for valid date ${vday}" > mailmsg
     echo Missing file is  $DCOMINghrsst/$vday/validation_data/marine/ghrsst/${vday}_OSPO_L4_GHRSST.nc >> mailmsg
     echo "Job ID: $jobid" >> mailmsg
     cat mailmsg | mail -s "$subject" $MAILTO
    fi 
  fi
fi

if [ $get_osi_saf = yes ] ; then 
 export OBSNAME="osi_saf"
 $USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh osi_saf
 export err=$?; err_chk
fi

#get ensemble member data sequentially (non-mpi) or mpi run
if [ $get_forecast = yes ] ; then
 $USHevs/${COMPONENT}/evs_global_ens_${RUN}_prep.sh
 export err=$?; err_chk
fi

if [ $get_naefs = yes ] ; then
 $USHevs/${COMPONENT}/evs_gens_${RUN}_g2g_prep_naefs.sh
 export err=$?; err_chk
fi

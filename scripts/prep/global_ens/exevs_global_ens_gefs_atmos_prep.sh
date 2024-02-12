#!/bin/ksh
#******************************************************************************************
# Purpose:   1. Setup required environment parameters 
#            2. Run global_ens_gefs_atmos_prep  
#
# Note: prep job will:
#            1. Retrive/regrid analysis/observational data (1 degree and 1.5 degree for WMO) 
#            2. Retrive required fields from large opreational global ensemble forecast 
#               member files (grib2 GEFS, CMCE, and grib1 ECME ) to form smaller member files
#            3. Regrid the smaller files to required grid (1x1 degree) for GEFS and CMCE
#               But retrived grib1 ECME files are still kept in original grid since wgrib
#               has limited regrid capability for grib1 files. The regrid will be done
#               by METplus
#            4. For CMCE grib2 files, reverse North-South direction (by wgrib2) 
#            5. Store the well-formed analysis/observational, and  smaller ensemble member
#               files in the evs prep sub-directory /prep/global_ens/atmos.YYYYMMDD  
#                             
# Last updated 11/15/2023: by  Binbin Zhou, Lynker@EMC/NCEP
#
#******************************************************************************************

set -x

export WORK=$DATA

cd $WORK

#**********************************************************************
# Following parameters are for setting which get-data sub-tasks 
#          should be run
#  Note 1: The big global_ens_gefs_atmos_prep job can be split to 
#          more smaller jobs by re-setting these get_data parameters
#          Current setting is for running one big prep job 
#       2: Specific get_data task(s) can be tested by setting all other
#          get_data parameters to "no"
#**********************************************************************
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

#*************************************
# run_mpi=yes is for MPI parallel run
# otherwise is for sequence run
#************************************
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
 export vdaym1=$($NDATE -24 ${INITDATE}00 | cut -c1-8)
  if [ -s $DCOMINghrsst/$vdaym1/validation_data/marine/ghrsst/${vdaym1}_OSPO_L4_GHRSST.nc ] ; then
      python $USHevs/${COMPONENT}/global_ens_prep_ghrsst_obs.py
      export err=$?; err_chk
  else
    echo "WARNING: $DCOMINghrsst/$vdaym1/validation_data/marine/ghrsst/${vdaym1}_OSPO_L4_GHRSST.nc is not available"
    if [ $SENDMAIL = YES ]; then
     export subject="GHRSST OSPO Data Missing for EVS ${COMPONENT}"
     export MAILTO=${MAILTO:-'alicia.bentley@noaa.gov,steven.simon@noaa.gov'}
     echo "Warning: No GHRSST OSPO data was available for valid date ${vday}" > mailmsg
     echo Missing file is  $DCOMINghrsst/$vdaym1/validation_data/marine/ghrsst/${vdaym1}_OSPO_L4_GHRSST.nc >> mailmsg
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

#***********************************************************
# Prep ensemble member data sequentially (non-mpi) or mpi run
#   This job will take most of running time
#**********************************************************
if [ $get_forecast = yes ] ; then
 $USHevs/${COMPONENT}/evs_global_ens_${RUN}_prep.sh
 export err=$?; err_chk
fi

#**********************************************************
# The default get_naefs=no. This task is run in another job
#   exevs_global_ens_naefs_atmos_prep.sh 
#**********************************************************
if [ $get_naefs = yes ] ; then
 $USHevs/${COMPONENT}/evs_gens_${RUN}_g2g_prep_naefs.sh
 export err=$?; err_chk
fi

#!/bin/ksh
#################################################################
# Purpose:   To run grid-to-grid verification on all global ensembles
#
# Log History:  12/01/2021 Binbin Zhou  
################################################################
set -x

export WORK=$DATA
cd $WORK

#Just for testing ver MET/METplus version
#if [ $met_ver = 11.0.0 ] ; then
#  export MET_BASE=/apps/ops/para/libs/intel/$intel_ver/met/$met_ver/share/met
#  export MET_ROOT=/apps/ops/para/libs/intel/$intel_ver/met/$met_ver
#  #export PATH=/apps/ops/para/libs/intel/$intel_ver/met/$met_ver/bin:${PATH}
#fi 


export MET_bin_exec='bin'
export log_met_output_to_metplus=''
export metplus_verbosity=2
export met_verbosity=2

export CLIMO=$FIXevs/climos/atmos
export MASKS=$FIXevs/masks

export ENS_LIST=$PARMevs/metplus_config/${COMPONENT}/${RUN}_grid2grid/prep
export GRID2GRID_CONF=$PARMevs/metplus_config/${COMPONENT}/${RUN}_grid2grid/${STEP}
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS

msg="$job HAS BEGUN"
postmsg "$jlogfile" "$msg"
export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}

export vday=$1
ens=$2 
verif_case=$3

#############################################################
# Step 0: Run copygb to convert URMA data to 4km WRF grid
#############################################################

if [ $ens = all ] || [ $ens = gefs ] || [ $ens = cmce ] || [ $ens = naefs ] || [ $ens = ecme ] ; then
 if [ $verif_case = all ] || [ $verif_case = upper ] || [ $verif_case = precip ] ; then 

   if [ $ens = gefs ] && [ $verif_case = upper ] ; then

     if [ ! -s ${COMIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
       export subject="GFS analysis data missing "
       echo "Warning: No GFS analysis available for ${VDATE}" > mailmsg 
       echo Missing file is ${COMIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit
     fi 

    elif [ $ens = cmce ] && [ $verif_case = upper ] ; then

     if [ ! -s ${COMIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2 ] ; then
       export subject="CMC analysis data missing "
       echo "Warning: No CMC analysis available for ${VDATE}" > mailmsg 
       echo Missing file is ${COMIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit
      fi

     elif [ $ens = ecme ] && [ $verif_case = upper ] ; then

      if [ ! -s ${COMIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2 ] ; then
       export subject="EC analysis data missing "
       echo "Warning: No EC analysis available for ${VDATE}" > mailmsg 
       echo Missing file is ${COMIN}.${VDATE}/ecme/ecmanl.t00z.grid3.f000.grib2  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit
      fi

     elif [ $ens = naefs ] && [ $verif_case = upper ] ; then

      if [ ! -s ${COMIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2 ] || [ ! -s ${COMIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
       export subject="GFS or CMC analysis data missing for NAEFS "
       echo "Warning: No GFS or CMC analysis available for ${VDATE}" > mailmsg 
       echo Missing file is ${COMIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 or ${COMIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit
      fi

     elif [ $verif_case = precip ] ; then

      if [ ! -s ${COMIN}.${VDATE}/gefs/ccpa.t12z.grid3.24h.f00.nc ] ; then
       export subject="24h CCAP data missing "
       echo "Warning: No 24hCCAP data available for ${VDATE}" > mailmsg 
       echo Missing file is ${COMIN}.${VDATE}/gefs/ccpa.t12z.grid3.24h.f00.nc  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit
      fi

     fi 

      echo "All validation data are available, continuing ..."

      $USHevs/global_ens/evs_global_ens_atmos_grid2grid.sh $ens $verif_case

 fi
fi

if [ $verif_case = snowfall ] || [ $verif_case = sea_ice ] ; then
  day1=`$NDATE -24 ${VDATE}12`
  VDATE_1=${day1:0:8}

  if [ $verif_case = snowfall ] && [ ! -s ${COMIN}.${VDATE}/gefs/nohrsc.t00z.grid184.grb2 ] ; then
       export subject="NOHRSC Snowfall analysis data missing "
       echo "Warning: No NOHRSC snowfall analysis available for ${VDATE}" > mailmsg 
       echo Missing file is ${COMIN}.${VDATE}/gefs/nohrsc.t00z.grid184.grb2  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit
   elif [ $verif_case = sea_ice ] && [ ! -s ${COMIN}.${VDATE}/osi_saf/osi_saf.multi.${VDATE_1}00to${VDATE}00_G004.nc ] ; then
       export subject="OSI_SAF analysis data missing "
       echo "Warning: No OSI_SAF analysis available for ${VDATE}" > mailmsg 
       echo Missing file is ${COMIN}.${VDATE}/osi_saf/osi_saf.multi.${VDATE_1}00to${VDATE}00_G004.nc  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit
    fi

    echo "All validation data are available, continuing ..."
  
    $USHevs/global_ens/evs_global_ens_atmos_${verif_case}.sh $ens ${verif_case}
fi

if [ $verif_case = sst ] ; then
  if [ ! -s ${COMIN}.${VDATE}/gefs/ghrsst.t00z.nc ] ; then

       export subject="GHRSST analysis data missing "
       echo "Warning: No GHRSST analysis available for ${VDATE}" > mailmsg 
       echo Missing file is ${COMIN}.${VDATE}/gefs/ghrsst.t00z.nc >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit
  fi
  echo "All validation data are available, continuing ..."
  
  $USHevs/global_ens/evs_global_ens_atmos_${verif_case}.sh $ens sst24h
fi


msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0

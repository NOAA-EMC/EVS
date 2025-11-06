#!/bin/ksh
#**********************************************************************************************
# Purpose:  1. Setup some running envirnment paramters for WMO job that are not
#              defined in stat J-job
#           2. Run WMO verifications of surface fields for gefs and cmce
#
# Last  updated 11/15/2023: by  Binbin Zhou, Lynker@EMC/NCEP
#
#**********************************************************************************************
set -x

export WORK=$DATA
cd $WORK

export CLIMO=$FIXevs/climos/atmos
export MASKS=$FIXevs/masks

export ENS_LIST=$PARMevs/metplus_config/prep/${COMPONENT}/atmos_grid2grid
export GRID2GRID_CONF=$PARMevs/metplus_config/${STEP}/${COMPONENT}/${RUN}_grid2grid
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS

export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}


export vday=$1
ens=$2 
verify_type=$3

if  [ $ens = gefs ] ||  [ $ens = cmce ] ; then
  if [ $verify_type = upper ] ; then 

   if [ $ens = gefs ] && [ ! -s ${EVSINwmo}.${VDATE}/gefs/gfsanl.t00z.deg1.5.f000.grib2 ] ; then
     if [ $SENDMAIL = YES ]; then
       export subject="GFS analysis data missing for WMO gefs verif"
       echo "Warning: No GFS analysis available for ${VDATE}" > mailmsg
       echo Missing file is ${EVSINwmo}.${VDATE}/gefs/gfsanl.t00z.deg1.5.f000.grib2  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $MAILTO
     fi
    exit
   fi

    if [ $ens = cmce ] && [ ! -s ${EVSINwmo}.${VDATE}/cmce/cmcanl.t00z.deg1.5.f000.grib2 ] ; then
      if [ $SENDMAIL = YES ]; then
        export subject="CMC analysis data missing for WMO cmce verif"
        echo "Warning: No CMC analysis available for ${VDATE}" > mailmsg
        echo Missing file is ${EVSINwmo}.${VDATE}/cmce/cmcanl.t00z.deg1.5.f000.grib2  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
      fi
     exit
    fi

   echo "All data are available, continuing ..."

   $USHevs/global_ens/evs_global_ens_wmo_grid2grid.sh $ens $verify_type 

 fi
fi

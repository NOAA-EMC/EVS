#!/bin/ksh
#################################################################
# Purpose:   To run grid-to-grid verification on all global ensembles
#
# Log History:  12/01/2021 Binbin Zhou  
################################################################
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

if [ $verify_type != upper ] ; then
    err_exit "$verify_type is not valid verification type"
fi

if  [ $ens = gefs ] || [ $ens = naefs ] || [ $ens = gfs ] ; then
   if [ $ens = gfs ] || [ $ens = gefs ] ; then
    if [ ! -s ${EVSIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
      if [ $SENDMAIL = YES ]; then
        export subject="GFS analysis data missing for $ens headline stat job"
        echo "Warning: No GFS analysis available for ${VDATE}" > mailmsg 
        echo "Missing file is ${EVSIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2"  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
      fi
    else
      echo "All $verif_case data are available, continuing"
      $USHevs/global_ens/evs_global_ens_headline_grid2grid.sh $ens $verify_type
      export err=$?; err_chk
    fi
   elif [ $ens = naefs ] ; then
      if [ ! -s ${EVSIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2 ] || [ ! -s ${EVSIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
        if [ $SENDMAIL = YES ]; then
          export subject="GFS or CMC analysis data missing for $ens headline stat job"
          echo "Warning: No GFS or CMC analysis available for ${VDATE}" > mailmsg
          echo "Missing file is ${EVSIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 or ${EVSIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2"  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist
        fi
       else
        echo "All $verif_case data are available, continuing"
        $USHevs/global_ens/evs_global_ens_headline_grid2grid.sh $ens $verify_type
        export err=$?; err_chk
       fi
     fi
else
    err_exit "$ens not valid ensemble"
fi

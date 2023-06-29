#!/bin/ksh
set -x

#check input data are available:
$USHevs/cam/evs_check_href_files.sh

export WORK=$DATA
cd $WORK

export MET_bin_exec='bin'
export log_met_output_to_metplus=''
export metplus_verbosity=2
export met_verbosity=2

export run_mpi=${run_mpi:-'yes'}
export prepare=${prepare:-'yes'}
export verif_precip=${verif_precip:-'yes'}
export verif_snowfall=${verif_snowfall:-'yes'}
export gather=${gather:-'yes'}
export verify='precip'

export COMHREF=$COMINhref
export COMCCPA=$COMINccpa
export COMSNOW=$COMINsnow
export COMMRMS=$COMINmrms

export PRECIP_CONF=$PARMevs/metplus_config/$COMPONENT/precip/$STEP
export SNOWFALL_CONF=$PARMevs/metplus_config/$COMPONENT/snowfall/$STEP
export GATHER_CONF_PRECIP=$PRECIP_CONF
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS
export vday=$VDATE


msg="$job HAS BEGUN"
postmsg "$jlogfile" "$msg"


if [ $prepare = yes ] ; then
 for precip in ccpa01h03h ccpa24h apcp24h_conus  apcp24h_alaska mrms ; do
  $USHevs/cam/evs_href_preppare.sh  $precip
 done
fi


> run_all_precip_poe.sh
if [ $verif_precip = yes ] ; then
 $USHevs/cam/evs_href_precip.sh
 cat ${DATA}/run_all_href_precip_poe.sh >> run_all_precip_poe.sh
fi

if [ $verif_snowfall = yes ] ; then
 $USHevs/cam/evs_href_snowfall.sh
 cat ${DATA}/run_all_href_snowfall_poe.sh >> run_all_precip_poe.sh
fi


if [ -s ${DATA}/run_all_precip_poe.sh ]  ; then
  chmod 775 run_all_precip_poe.sh

  if [ $run_mpi = yes ] ; then
    export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
    mpiexec  -n 44 -ppn 44 --cpu-bind core --depth=2 cfp ${DATA}/run_all_precip_poe.sh
  else
   ${DATA}/run_all_precip_poe.sh
  fi

fi

if [ $gather = yes ] ; then
  $USHevs/cam/evs_href_gather.sh precip
fi

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0

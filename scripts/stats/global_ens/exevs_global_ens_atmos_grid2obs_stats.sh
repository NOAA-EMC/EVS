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

export ENS_LIST=$PARMevs/metplus_config/prep/${COMPONENT}/${RUN}_grid2grid
export GRID2OBS_CONF=$PARMevs/metplus_config/${STEP}/${COMPONENT}/${RUN}_grid2obs
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS

export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}

export vday=$1
export ens=$2 
export verif_case=$3

if [ $ens = gefs ] ; then
  vhours="00 06 12 18"
elif [ $ens = cmce ] || [ $ens = naefs ] || [ $ens = ecme ] ; then
  vhours="00 12"
else
  err_exit "$ens not valid"
fi

all_prepbufr_av=YES
for vhour in $vhours; do
    if [ ! -s ${EVSIN}.${VDATE}/gefs/gfs.t${vhour}z.prepbufr.f00.nc ] ; then
      if [ $SENDMAIL = YES ]; then
        all_prepbufr_av=NO
        export subject="PREPBUFR data file missing "
        echo "Warning: No PREPBUFR data available for ${VDATE}${vhour}" > mailmsg 
        echo "Missing file is ${EVSIN}.${VDATE}/gefs/gfs.t${vhour}z.prepbufr.f00.nc"  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
      fi
    fi
done

if [ $all_prepbufr_av = YES ]; then
  echo "All data are available, continuing ...."
  $USHevs/global_ens/evs_global_ens_atmos_${verif_case}.sh $ens
  export err=$?; err_chk
fi

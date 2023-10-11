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
#  export PATH=/apps/ops/para/libs/intel/$intel_ver/met/$met_ver/bin:${PATH}
#fi


export CLIMO=$FIXevs/climos/atmos
export MASKS=$FIXevs/masks

export ENS_LIST=$PARMevs/metplus_config/prep/${COMPONENT}/${RUN}_grid2grid
export GRID2OBS_CONF=$PARMevs/metplus_config/${STEP}/${COMPONENT}/${RUN}_grid2obs
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS

msg="$job HAS BEGUN"
postmsg "$jlogfile" "$msg"

export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}

export vday=$1
export ens=$2 
export verif_case=$3

#############################################################
# Step 0: Run copygb to convert URMA data to 4km WRF grid
#############################################################


if [ $ens = all ] || [ $ens = gefs ] || [ $ens = cmce ] || [ $ens = naefs ] || [ $ens = ecme ] ; then 	
    if [ ! -s ${COMIN}.${VDATE}/gefs/gfs.t00z.prepbufr.f00.nc ] ; then
      if [ $SENDMAIL = YES ]; then
        export subject="PREPBUFR data file missing "
        echo "Warning: No PREPBUFR data available for ${VDATE}" > mailmsg 
        echo Missing file is ${COMIN}.${VDATE}/gefs/gfs.t00z.prepbufr.f00.nc  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
      fi
     exit
    fi
   echo "All data are available, continuing ...."
   $USHevs/global_ens/evs_global_ens_atmos_${verif_case}.sh $ens  
fi

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"




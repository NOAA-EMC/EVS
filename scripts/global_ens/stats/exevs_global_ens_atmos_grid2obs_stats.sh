#!/bin/ksh
#################################################################
# Purpose:   To run grid-to-grid verification on all global ensembles
#
# Log History:  12/01/2021 Binbin Zhou  
################################################################
set -x

export WORK=$DATA
cd $WORK

export MET_bin_exec='bin'
export log_met_output_to_metplus=''
export metplus_verbosity=2
export met_verbosity=2

export CLIMO=$FIXevs/climos/atmos
export MASKS=$FIXevs/masks

export ENS_LIST=$PARMevs/metplus_config/${COMPONENT}/${RUN}_grid2grid/prep
export GRID2OBS_CONF=$PARMevs/metplus_config/${COMPONENT}/${RUN}_grid2obs/${STEP}
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
 $USHevs/global_ens/evs_global_ens_atmos_${verif_case}.sh $ens  
fi

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0

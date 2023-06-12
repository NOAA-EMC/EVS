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
#export MET_BASE=/apps/ops/para/libs/intel/$intel_ver/met/$met_ver/share/met
#export MET_ROOT=/apps/ops/para/libs/intel/$intel_ver/met/$met_ver
#export PATH=/apps/ops/para/libs/intel/$intel_ver/met/$met_ver/bin:${PATH}

export MET_bin_exec='bin'
export log_met_output_to_metplus=''
export metplus_verbosity=2
export met_verbosity=2

export run_mpi=${run_mpi:-'yes'}
export stats=${stats:-'yes'}
export gather=${gather:-'yes'}


msg="$job HAS BEGUN"
postmsg "$jlogfile" "$msg"

export GRID2OBS_CONF=$PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS


#############################################################
# Step 0: Run copygb to convert URMA data to 4km WRF grid
#############################################################

if [ $stats = yes ] ; then
 $USHevs/narre/evs_narre_stats.sh  
fi


msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0

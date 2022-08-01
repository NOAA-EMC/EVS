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


msg="$job HAS BEGUN"
postmsg "$jlogfile" "$msg"


#############################################################
# Step 0: Run copygb to convert URMA data to 4km WRF grid
#############################################################

if [ $stats = yes ] ; then
 $USHevs/narre/evs_narre_stats.sh  
fi


#if [ $gather = yes ] ; then
# $USHevs/narre/stats/evs_narre_gather.sh
#fi

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0

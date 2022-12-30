#!/bin/ksh
#################################################################
# Purpose:   To run grid-to-grid verification on all global ensembles
#
# Log History:  12/01/2021 Binbin Zhou  
################################################################
set -x

export MET_bin_exec='bin'
export log_met_output_to_metplus=''
export metplus_verbosity=2
export met_verbosity=2

msg="$job HAS BEGUN"
postmsg "$jlogfile" "$msg"
export run_mpi=${run_mpi:-'yes'}


#############################################################
# Step 0: Run copygb to convert URMA data to 4km WRF grid
#############################################################

export PLOT_CONF=$PARMevs/metplus_config/global_ens/headline_grid2grid/plots
$USHevs/global_ens/evs_global_ens_headline_plot.sh 

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0

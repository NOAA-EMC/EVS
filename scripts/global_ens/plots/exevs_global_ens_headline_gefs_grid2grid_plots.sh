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

this_year=${VDATE:0:4}
past=`$NDATE -8760 ${VDATE}01`
last_year=${past:0:4} 

mm=${VDATE:4:2}
dd=${VDATE:6:2}

if [ $mm = 01 ] && [ $dd = 17 ] ; then
  run_entire_year=yes
else
  run_entire_year=no
  last_year=$this_year
fi 

export PLOT_CONF=$PARMevs/metplus_config/global_ens/headline_grid2grid/plots
$USHevs/global_ens/evs_global_ens_headline_plot.sh $last_year $this_year 

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.v${VDATE}.tar evs.global_ens*.png

if [ $SENDCOM = YES ]; then
    cp evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.v${VDATE}.tar $COMOUT/.
fi

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"

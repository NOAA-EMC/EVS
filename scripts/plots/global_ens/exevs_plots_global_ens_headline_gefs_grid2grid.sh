#!/bin/ksh
#****************************************************************************************
# Purpose:  1. Setup the environment parameter for running GEFS headline plotting script
#           2. Run plotting script $USHevs/global_ens/evs_global_ens_headline_plot.sh
#  
#  Note: 1. The headline score needs the stat files over one year + 16 days 
#           (last year + next 16 days of Jan of this year) 
#        2. This job is run on Jan 16 of each year                 
#  
# Log History:  
#             01/17/2024, Add calculation of day for ACC<=0.6, Binbin Zhou, Lynker@EMC
#             11/17/2021, created by Binbin Zhou, Lynker@EMC  
#**********************************************************************
set -x
export run_mpi=${run_mpi:-'yes'}

this_year=${VDATE:0:4}
past=`$NDATE -8760 ${VDATE}01`

mm=${VDATE:4:2}

if [ $mm = 01 ] ; then
  run_entire_year=yes
  last_year=${past:0:4}
else
  run_entire_year=no
  last_year=$this_year
fi 

export PLOT_CONF=$PARMevs/metplus_config/$STEP/$COMPONENT/headline_grid2grid
$USHevs/global_ens/evs_global_ens_headline_plot.sh $last_year $this_year 
export err=$?; err_chk

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.v${VDATE}.tar evs.global_ens*.png

if [ $SENDCOM = YES ]; then
    if [ -s evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.v${VDATE}.tar ]; then
        cp -v evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.v${VDATE}.tar $COMOUT/.
    fi
fi

if [ $SENDDBN = YES ]; then 
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.v${VDATE}.tar
fi

#**********************************************************************************************
# Calculate the day when ACC drops below 0.6 
# Step 1: use $USHevs/global_ens/evs_global_ens_headline_acc0.6_day.sh for GEFS, GFS 
#         and NAEFS, respectively based on $DATA/model_500HGT_NH_PAC_${last_year}.txt as input
#         All output results will be saved in day.txt in $DATA
# Step 2: Rename the day.txt and send it to $COMOUT 
#*********************************************************************************************
if [ $calculate_acc0p6_days = yes ] ; then
  export output=day.txt
  >$output
  export model=GEFS
  $USHevs/global_ens/evs_global_ens_headline_acc0.6_day.sh < $DATA/GEFS_500HGT_NH_PAC_${last_year}.txt
  export err=$?; err_chk
  export model=GFS
  $USHevs/global_ens/evs_global_ens_headline_acc0.6_day.sh < $DATA/GFS_500HGT_NH_PAC_${last_year}.txt
  export err=$?; err_chk
  export model=NAEFS
  $USHevs/global_ens/evs_global_ens_headline_acc0.6_day.sh < $DATA/NAEFS_500HGT_NH_PAC_${last_year}.txt
  export err=$?; err_chk
  if [ $SENDCOM = YES ]; then
    if [ -s $output ] ; then	  
      cp -v $output $COMOUT/day_acc_below_0.6.txt
    fi 
  fi
fi



#!/bin/bash
###############################################################################
# Name of Script: exevs_glwu_headline_plots.sh
# Purpose of Script: To create headline score plots for RTOFS forecast
#    verifications using MET/METplus.
# Author: Samira Ardani (samira.ardani@noaa.gov)
###############################################################################

set -x

# set up plot variables
export PERIOD=last90days

# plot time series
export PTYPE=time_series

for lead in 000 024 048 072 096 120 144 168 192; do
  export FLEAD=$lead

# make plots for htsgw
  export MASKS="glb" # that should be changed.

  for obs in NDBC_STANDARD; do  # keep it just in case we have more validation sources.
    export OBTYPE=$obs
    export LTYPE=SL1L2
    export THRESH=""

    if [ $obs = 'NDBC_STANDARD' ] ; then
      export VERIF_CASE=grid2obs
      export VAR=htsgw
      export FLVL=Z0
      export OLVL=Z0
    fi


    for stats in me rmse; do
      export METRIC=$stats
      $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
    done

    export METRIC=fbias
    export LTYPE=CTC
    export THRESH=">=26.5"
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
  done


# plot mean vs. lead time
export PTYPE=lead_average
export FLEAD="000,024,048,072,096,120,144,168,192"

# make plots for perpw
export MASKS="GLB"

for obs in NDBC_STANDARD; do
  export OBTYPE=$obs
  export LTYPE=SL1L2
  export THRESH=""


  if [ $obs = 'NDBC_STANDARD' ] ; then
    export VERIF_CASE=grid2obs
    export VAR=perpw
    export FLVL=Z0
    export OLVL=Z0
  fi


  for stats in me rmse; do
    export METRIC=$stats
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
  done

  export METRIC=fbias
  export LTYPE=CTC
  export THRESH=">=26.5"
  $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
done


# tar all plots together
tar -cvf $COMOUTplots/evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar $DATA/plots/$COMPONENT/glwu.$VDATE/$RUN/*.png

exit

################################ END OF SCRIPT ################################

#!/bin/bash
###############################################################################
# Name of Script: exevs_glwu_seasfc_plots.sh
# Purpose of Script: To create forecast verification plots for glwu sea
#    surface variables using MET/METplus.
# Author: Samira Ardani (samira.ardani@noaa.gov)
###############################################################################

set -x

# set up plot variables
export PERIOD=last60days
export THRESH=""
export MASKS="GLB, NATL, SATL, EQATL, NPAC, SPAC, EQPAC, IND, SOC, Arctic, MEDIT" #need to be changed
if [ $RUN = 'ndbc' ] ; then
  export MASKS="GLB"
fi

# plot time series
export PTYPE=time_series

for lead in 000 024 048 072 096 120 144 168 192; do
  export FLEAD=$lead

  for stats in me rmse acc; do
    export METRIC=$stats

    if [ $stats = 'me' ] ; then 
      export LTYPE=SL1L2
    fi

    if [ $stats = 'rmse' ] ; then  
      export LTYPE=SL1L2
    fi

    if [ $stats = 'acc' ] ; then  
      export LTYPE=SAL1L2
    fi

# make plots
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.glwu.conf

  done
done

# plot mean vs. lead time
export PTYPE=lead_average
export FLEAD="000,024,048,072,096,120,144,168,192"

for stats in me rmse acc; do
  export METRIC=$stats

  if [ $stats = 'me' ] ; then
    export LTYPE=SL1L2
  fi

  if [ $stats = 'rmse' ] ; then
    export LTYPE=SL1L2
  fi

  if [ $stats = 'acc' ] ; then
    export LTYPE=SAL1L2
  fi

# make plots
  $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.glwu.conf
done

# tar all plots together
tar -cvf $COMOUTplots/evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar $DATA/plots/$COMPONENT/glwu.$VDATE/$RUN/*.png

exit

################################ END OF SCRIPT ################################

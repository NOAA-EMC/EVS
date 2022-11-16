#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_plots_timeseries.sh
# Purpose of Script: To create time series plots for RTOFS forecast
#    verification using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# set up plot variables
export PTYPE=time_series
export PERIOD=last60days
export MASKS="GLB, NATL, SATL, EQATL, NPAC, SPAC, EQPAC, IND, SOC, Arctic, MEDIT"

for lead in 000 024 048 072 096 120 144 168 192; do
  export FLEAD=$lead

  for stats in me rmse acc; do
    if [ $stats = 'me' ] ; then 
      export METRIC=$stats
      export LTYPE=SL1L2
      export THRESH=""
    fi

    if [ $stats = 'rmse' ] ; then  
      export METRIC=$stats
      export LTYPE=SL1L2
      export THRESH=""
    fi

    if [ $stats = 'acc' ] ; then  
      export METRIC=$stats
      export LTYPE=SAL1L2
      export THRESH=""
    fi

# make plots
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf

  done
done

# tar all plots together
tar -cvf $COMOUTplots/evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar $COMOUTplots/$RUN/*.png

exit

################################ END OF SCRIPT ################################

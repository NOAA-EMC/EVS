#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_plots_seaice_timeseries.sh
# Purpose of Script: To create time series plots for RTOFS sea ice forecast
#    verification using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# set up plot variables
export PERIOD=last60days
export MASKS="Arctic, Antarctic"

# plot time series
export PTYPE=time_series
for lead in 000 024 048 072 096 120 144 168 192; do
  export FLEAD=$lead

  for stats in me rmse; do
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

# make plots
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
  done

  for stats in csi; do
    export METRIC=$stats
    export LTYPE=CTC

    for thre in ">=15" ">=40" ">=80"; do
      export THRESH=$thre

# make plots
      $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
    done
  done

done

# plot performance diagram
export PTYPE=performance_diagram
export METRIC="sratio,pod,csi"
export LTYPE=CTC
export THRESH=">=15,>=40,>=80"

for lead in 000 024 048 072 096 120 144 168 192; do
  export FLEAD=$lead

# make plots
  $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
done

# tar all plots together
tar -cvf $COMOUTplots/evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar $COMOUTplots/$RUN/*.png

exit

################################ END OF SCRIPT ################################

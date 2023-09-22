#!/bin/bash
###############################################################################
# Name of Script: exevs_glwu_seaice_plots.sh
# Purpose of Script: To create plots for glwu sea ice forecast verification
#    using MET/METplus.
# Author: Samira Ardani (samira.ardani@noaa.gov)
###############################################################################

set -x

# set up plot variables
export PERIOD=last60days
export MASKS="Arctic, Antarctic" # should be changed

# plot time series
export PTYPE=time_series
for lead in 000 024 048 072 096 120 144 168 192; do
  export FLEAD=$lead

  for stats in me rmse; do
    export METRIC=$stats
    export LTYPE=SL1L2
    export THRESH=""

# make plots
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.glwu.conf
  done

  for stats in csi; do
    export METRIC=$stats
    export LTYPE=CTC

    for thre in ">=15" ">=40" ">=80"; do
      export THRESH=$thre

# make plots
      $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.glwu.conf
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
  $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.glwu.conf
done

# plot mean vs. lead time
export PTYPE=lead_average
export FLEAD="000,024,048,072,096,120,144,168,192"

for stats in me rmse; do
  export METRIC=$stats
  export LTYPE=SL1L2
  export THRESH=""

# make plots
  $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.glwu.conf
done

for stats in csi; do
  export METRIC=$stats
  export LTYPE=CTC

  for thre in ">=15" ">=40" ">=80"; do
    export THRESH=$thre

# make plots
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.glwu.conf
  done
done

# tar all plots together
tar -cvf $COMOUTplots/evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar $DATA/plots/$COMPONENT/glwu.$VDATE/$RUN/*.png

exit

################################ END OF SCRIPT ################################

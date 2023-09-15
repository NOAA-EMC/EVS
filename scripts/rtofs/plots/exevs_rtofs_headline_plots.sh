#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_headline_plots.sh
# Purpose of Script: To create headline score plots for RTOFS forecast
#    verifications using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# set up plot variables
export PERIOD=last90days

# plot time series
export PTYPE=time_series

for lead in 000 024 048 072 096 120 144 168 192; do
  export FLEAD=$lead

# make plots for SST
  export MASKS="GLB"

  for obs in GHRSST NDBC_STANDARD ARGO; do
    export OBTYPE=$obs
    export LTYPE=SL1L2
    export THRESH=""

    if [ $obs = 'GHRSST' ] ; then
      export VERIF_CASE=grid2grid
      export VAR=SST
    fi

    if [ $obs = 'NDBC_STANDARD' ] ; then
      export VERIF_CASE=grid2obs
      export VAR=SST
      export FLVL=Z0
      export OLVL=Z0
    fi

    if [ $obs = 'ARGO' ] ; then
      export VERIF_CASE=grid2obs
      export VAR=TEMP
      export FLVL=Z0
      export OLVL=Z4-0
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

# make plots for SIC
  export VAR=SIC
  export MASKS="Arctic"
  export VERIF_CASE=grid2grid
  export OBTYPE=OSISAF
  export METRIC=csi
  export LTYPE=CTC

  for thre in ">=15" ">=40" ">=80"; do
    export THRESH=$thre
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
  done
done

# plot mean vs. lead time
export PTYPE=lead_average
export FLEAD="000,024,048,072,096,120,144,168,192"

# make plots for SST
export MASKS="GLB"

for obs in GHRSST NDBC_STANDARD ARGO; do
  export OBTYPE=$obs
  export LTYPE=SL1L2
  export THRESH=""

  if [ $obs = 'GHRSST' ] ; then
    export VERIF_CASE=grid2grid
    export VAR=SST
  fi

  if [ $obs = 'NDBC_STANDARD' ] ; then
    export VERIF_CASE=grid2obs
    export VAR=SST
    export FLVL=Z0
    export OLVL=Z0
  fi

  if [ $obs = 'ARGO' ] ; then
    export VERIF_CASE=grid2obs
    export VAR=TEMP
    export FLVL=Z0
    export OLVL=Z4-0
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

# make plots for SIC
export VAR=SIC
export MASKS="Arctic"
export VERIF_CASE=grid2grid
export OBTYPE=OSISAF
export METRIC=csi
export LTYPE=CTC

for thre in ">=15" ">=40" ">=80"; do
  export THRESH=$thre
  $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
done

# tar all plots together
cd $DATA/plots/$COMPONENT/rtofs.$VDATE/$RUN
tar -cvf evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar *.png

if [ $SENDCOM = "YES" ]; then
 cp evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar $COMOUTplotsheadline
fi

exit

################################ END OF SCRIPT ################################

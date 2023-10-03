#!/bin/bash
###############################################################################
# Name of Script: rtofs_plots_seasfc.sh
# Purpose of Script: To create forecast verification plots for RTOFS sea
#    surface variables using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# set major & minor MET version
export MET_VERSION_major_minor=`echo $MET_VERSION | sed "s/\([^.]*\.[^.]*\)\..*/\1/g"`

# set up plot variables
export PERIOD=last60days
export THRESH=""
export MASKS="GLB, NATL, SATL, EQATL, NPAC, SPAC, EQPAC, IND, SOC, Arctic, MEDIT"
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
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf

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
  $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
done

# tar all plots together
cd $DATA/plots/$COMPONENT/rtofs.$VDATE/$RUN
tar -cvf evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar *.png

if [ $SENDCOM = "YES" ]; then
 cp -v evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar $COMOUTplots
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar
fi


exit

################################ END OF SCRIPT ################################

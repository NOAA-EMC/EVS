#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_profile_plots.sh
# Purpose of Script: To create forecast verification plots for RTOFS
#    temperature and salinity profiles using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# set up plot variables
export PERIOD=last60days
export THRESH=""
export MASKS="GLB"
#export MASKS="GLB, NATL, SATL, EQATL, NPAC, SPAC, EQPAC, IND, SOC, Arctic, MEDIT"

# plot time series
export PTYPE=time_series

for lead in 000 024 048 072 096 120 144 168 192; do
  export FLEAD=$lead

  for levl in 0 50 125 200 400 700 1000 1400; do
    if [ $levl = 0 ] ; then
      export FLVL=Z0
      export OLVL=Z4-0
    fi

    if [ $levl = 50 ] ; then
      export FLVL=Z50
      export OLVL=Z52-48
    fi

    if [ $levl = 125 ] ; then
      export FLVL=Z125
      export OLVL=Z127-123
    fi

    if [ $levl = 200 ] ; then
      export FLVL=Z200
      export OLVL=Z202-198
    fi

    if [ $levl = 400 ] ; then
      export FLVL=Z400
      export OLVL=Z402-398
    fi

    if [ $levl = 700 ] ; then
      export FLVL=Z700
      export OLVL=Z702-698
    fi

    if [ $levl = 1000 ] ; then
      export FLVL=Z1000
      export OLVL=Z1003-997
    fi

    if [ $levl = 1400 ] ; then
      export FLVL=Z1400
      export OLVL=Z1403-1397
    fi

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
done

# plot mean vs. lead time
export PTYPE=lead_average
export FLEAD="000,024,048,072,096,120,144,168,192"

for levl in 0 50 125 200 400 700 1000 1400; do
  if [ $levl = 0 ] ; then
    export FLVL=Z0
    export OLVL=Z4-0
  fi

  if [ $levl = 50 ] ; then
    export FLVL=Z50
    export OLVL=Z52-48
  fi

  if [ $levl = 125 ] ; then
    export FLVL=Z125
    export OLVL=Z127-123
  fi

  if [ $levl = 200 ] ; then
    export FLVL=Z200
    export OLVL=Z202-198
  fi

  if [ $levl = 400 ] ; then
    export FLVL=Z400
    export OLVL=Z402-398
  fi

  if [ $levl = 700 ] ; then
    export FLVL=Z700
    export OLVL=Z702-698
  fi

  if [ $levl = 1000 ] ; then
    export FLVL=Z1000
    export OLVL=Z1003-997
  fi

  if [ $levl = 1400 ] ; then
    export FLVL=Z1400
    export OLVL=Z1403-1397
  fi

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

# tar all plots together
cd $DATA/plots/$COMPONENT/rtofs.$VDATE/$RUN
tar -cvf evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar *.png

if [ $SENDCOM = "YES" ]; then
 cp evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar $COMOUTplots
fi

exit

################################ END OF SCRIPT ################################

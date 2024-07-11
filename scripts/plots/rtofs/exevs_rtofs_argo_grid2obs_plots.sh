#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_argo_grid2obs_plots
# Purpose of Script: Create RTOFS ARGO plots for last 60 days
# Author: Mallory Row (mallory.row@noaa.gov)
###############################################################################

set -x

export OBTYPE=ARGO

mkdir -p $DATA/$STEP/$COMPONENT/$COMPONENT.$VDATE
mkdir -p $DATA/tmp/rtofs
# set major & minor MET version
export MET_VERSION_major_minor=$(echo $MET_VERSION | sed "s/\([^.]*\.[^.]*\)\..*/\1/g")

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

      for vari in TEMP PSAL; do
        export VAR=$vari
        # make plots
        $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
        export err=$?; err_chk
      done
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

    for vari in TEMP PSAL; do
      export VAR=$vari
      # make plots
      $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
      export err=$?; err_chk
    done
  done
done

# Cat the plotting log files
log_dir=$DATA/logs/rtofs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
	for log_file in $log_dir/*; do
		echo "Start: $log_file"
		cat $log_file
		echo "End: $log_file"
	done
fi

# tar all plots together
cd $DATA/plots/$COMPONENT/rtofs.$VDATE/$RUN
tar -cvf evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar *.png

if [ $SENDCOM = "YES" ]; then
 if [ -s evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar ]; then
	cp -v evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar $COMOUTplots
 fi
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar
fi

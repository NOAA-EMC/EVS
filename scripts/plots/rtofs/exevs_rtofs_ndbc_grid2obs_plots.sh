#!/bin/bash
######################################################################################################
# Name of Script: exevs_rtofs_ndnc_grid2obs_plots
# Purpose of Script: Create RTOFS NDBC plots for last 60 days
# Author: Mallory Row (mallory.row@noaa.gov)
# Edited by:  Samira Ardani (samira.ardani@noaa.gov) 
# 09/2024: Variable names changed:
# 1- $RUN=ocean for each step of EVSv2-RTOFS was defined to be consistent with other EVS components. 
# 2- $RUN was defined in all j-jobs. 
# 3- $RUNsmall was renamed to $RUN in stats j-job and all stats scripts; and 
# 4- For all observation types, variable $OBTYPE was used instead of $RUN throughout all scripts.
#####################################################################################################

set -x

export OBTYPE=NDBC_STANDARD

export VAR=SST
export FLVL=Z0
export OLVL=Z0

mkdir -p $DATA/$STEP/$COMPONENT/$COMPONENT.$VDATE
mkdir -p $DATA/tmp/rtofs
# set major & minor MET version
export MET_VERSION_major_minor=$(echo $MET_VERSION | sed "s/\([^.]*\.[^.]*\)\..*/\1/g")

# set up plot variables
export PERIOD=last60days
export THRESH=""
export MASKS="GLB"

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
    $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
    export err=$?; err_chk

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
  $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
  export err=$?; err_chk
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

if [ $OBTYPE = 'NDBC_STANDARD' ]; then
	export obtype_lower=ndbc_standard
	export obtype=ndbc

fi

# tar all plots together
cd $DATA/plots/$COMPONENT/rtofs.$VDATE/$obtype_lower
tar -cvf evs.plots.$COMPONENT.$obtype.${VERIF_CASE}.$PERIOD.v$VDATE.tar *.png

if [ $SENDCOM = "YES" ]; then
	if [ -s evs.plots.$COMPONENT.$obtype.${VERIF_CASE}.$PERIOD.v$VDATE.tar ]; then
		cp -v evs.plots.$COMPONENT.$obtype.${VERIF_CASE}.$PERIOD.v$VDATE.tar $COMOUTplots
	fi
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.$COMPONENT.$obtype.${VERIF_CASE}.$PERIOD.v$VDATE.tar
fi

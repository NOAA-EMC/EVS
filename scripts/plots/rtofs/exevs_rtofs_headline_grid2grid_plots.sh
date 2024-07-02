#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_headline_grid2grid_plots
# Purpose of Script: Create RTOFS headline plots
# Author: Mallory Row (mallory.row@noaa.gov)
###############################################################################

set -x

mkdir -p $DATA/$STEP/$COMPONENT/$COMPONENT.$VDATE
mkdir -p $DATA/tmp/rtofs
# set major & minor MET version
export MET_VERSION_major_minor=$(echo $MET_VERSION | sed "s/\([^.]*\.[^.]*\)\..*/\1/g")

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
      $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
      export err=$?; err_chk
    done

    export METRIC=fbias
    export LTYPE=CTC
    export THRESH=">=26.5"
    $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
    export err=$?; err_chk
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
    $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
    export err=$?; err_chk
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
    $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
    export err=$?; err_chk
  done

  export METRIC=fbias
  export LTYPE=CTC
  export THRESH=">=26.5"
  $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
  export err=$?; err_chk
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

# tar all plots together
cd $DATA/plots/$COMPONENT/rtofs.$VDATE/$RUN
tar -cvf evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar *.png

if [ $SENDCOM = "YES" ]; then
	if [ -s evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar ]; then	 
       		cp -v evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar $COMOUTplotsheadline
	fi
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplotsheadline/evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar
fi

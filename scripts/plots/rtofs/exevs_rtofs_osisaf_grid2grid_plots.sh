#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_osisaf_grid2grid_plots
# Purpose of Script: Create RTOFS OSI-SAF plots for last 60 days
# Author: Mallory Row (mallory.row@noaa.gov)
###############################################################################

set -x

export OBTYPE=OSISAF

export VAR=SIC

mkdir -p $DATA/$STEP/$COMPONENT/$COMPONENT.$VDATE
mkdir -p $DATA/tmp/rtofs
# set major & minor MET version
export MET_VERSION_major_minor=$(echo $MET_VERSION | sed "s/\([^.]*\.[^.]*\)\..*/\1/g")

# set up plot variables
export PERIOD=last60days
export MASKS="Arctic, Antarctic"

# plot time series
export PTYPE=time_series
for lead in 000 024 048 072 096 120 144 168 192; do
  export FLEAD=$lead

  for stats in me rmse; do
    export METRIC=$stats
    export LTYPE=SL1L2
    export THRESH=""

# make plots
    $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
    export err=$?; err_chk
  done

  for stats in csi; do
    export METRIC=$stats
    export LTYPE=CTC

    for thre in ">=15" ">=40" ">=80"; do
      export THRESH=$thre

# make plots
      $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
      export err=$?; err_chk
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
  $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
  export err=$?; err_chk
done

# plot mean vs. lead time
export PTYPE=lead_average
export FLEAD="000,024,048,072,096,120,144,168,192"

for stats in me rmse; do
  export METRIC=$stats
  export LTYPE=SL1L2
  export THRESH=""

# make plots
  $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
  export err=$?; err_chk
done

for stats in csi; do
  export METRIC=$stats
  export LTYPE=CTC

  for thre in ">=15" ">=40" ">=80"; do
    export THRESH=$thre

# make plots
    $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/verif_plotting.rtofs.conf
    export err=$?; err_chk
  done
done


# tar all plots together
cd $DATA/plots/$COMPONENT/rtofs.$VDATE/$RUN
tar -cvf evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar *.png

if [ $SENDCOM = "YES" ]; then
	if [ -s evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar ] ; then
		cp -v evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar $COMOUTplots
	fi
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.$COMPONENT.$RUN.${VERIF_CASE}.$PERIOD.v$VDATE.tar
fi

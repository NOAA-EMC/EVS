#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_plots.sh
# Purpose of Script: Create RTOFS plots for last 60 days
# Author: Mallory Row (mallory.row@noaa.gov)
###############################################################################

set -x

mkdir -p $DATA/$STEP/$COMPONENT/$COMPONENT.$VDATE

# make plots; run scripts for each RUN;
# RUN is the validation source: ghrsst, smos, smap etc.

##########################
# seasfc
##########################
for rcase in ghrsst smos smap aviso ndbc; do
  export RUN=$rcase
  if [ $RUN = 'ghrsst' ] ; then
    export OBTYPE=GHRSST
    export VAR=SST
    export VERIF_CASE=grid2grid
  fi
  if [ $RUN = 'smos' ] ; then
    export OBTYPE=SMOS
    export VAR=SSS
    export VERIF_CASE=grid2grid
  fi
  if [ $RUN = 'smap' ] ; then
    export OBTYPE=SMAP
    export VAR=SSS
    export VERIF_CASE=grid2grid
  fi
  if [ $RUN = 'aviso' ] ; then
    export OBTYPE=AVISO
    export VAR=SSH
    export VERIF_CASE=grid2grid
  fi
  if [ $RUN = 'ndbc' ] ; then
    export OBTYPE=NDBC_STANDARD
    export VAR=SST
    export VERIF_CASE=grid2obs
    export FLVL=Z0
    export OLVL=Z0
  fi
  $USHevs/$COMPONENT/${COMPONENT}_${STEP}_seasfc.sh
done

##########################
# seaice
##########################
for rcase in osisaf; do
  export RUN=$rcase
  export OBTYPE=OSISAF
  export VAR=SIC
  export VERIF_CASE=grid2grid
  $USHevs/$COMPONENT/${COMPONENT}_${STEP}_seaice.sh
done

##########################
# profile
##########################
export RUN=argo
export OBTYPE=ARGO
export VERIF_CASE=grid2obs
for vari in TEMP PSAL; do
  export VAR=$vari
  $USHevs/$COMPONENT/${COMPONENT}_${STEP}_profile.sh
done

##########################
# headline
##########################
export RUN=headline
$USHevs/$COMPONENT/${COMPONENT}_${STEP}_headline.sh

#!/bin/ksh
#************************************************************************************
# Purpose: To build virtual links for last 31/90 days of stat files required
#          by aigefs plots jobs
# Updated: 10/22/2025 by L. Gwen Chen (lichuan.chen@noaa.gov)
#************************************************************************************
set -x 

day=$1
MODEL_LIST=$2

if [ ${VERIF_CASE} = profile1 ] || [ ${VERIF_CASE} = profile2 ] ; then
  VRF_CASE=grid2obs
else
  VRF_CASE=${VERIF_CASE}
fi

for MODEL in $MODEL_LIST ; do
 
  model=`echo $MODEL | tr '[A-Z]' '[a-z]'`

  #**************************
  # Get sub-string of $EVSIN
  #**************************
  archive=$output_base_dir

  COM_IN=$COMIN/stats/$COMPONENT
  echo $COM_IN

  model_stat_dir=${COM_IN}/${model}.${day}

  gens_archive_yyyymmdd=${archive}/${model}
  mkdir -p $gens_archive_yyyymmdd

  cd ${gens_archive_yyyymmdd}

  stat=${model_stat_dir}/evs.stats.${model}.atmos.${VRF_CASE}.v${day}.stat

  if [ -s ${stat} ] ; then
    ln -sf ${stat} ${MODEL}_${day}.stat
  fi

done


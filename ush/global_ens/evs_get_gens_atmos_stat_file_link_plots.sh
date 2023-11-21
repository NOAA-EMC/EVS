#!/bin/ksh
#**********************************************************************************************
# Purpose: To build virtually link for past 31/90 days of global_ens  stat data files required
#          by global_ens plot jobs
# Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#**********************************************************************************************
set -x 

day=$1
MODEL_LIST=$2
if [ ${VERIF_CASE} = sst ] ; then
  VRF_CASE=${VERIF_CASE}24h
elif [ ${VERIF_CASE} = profile1 ] || [ ${VERIF_CASE} = profile2 ] || [ ${VERIF_CASE} = profile3 ] || [ ${VERIF_CASE} = profile4 ]; then
  VRF_CASE=grid2obs
else
  VRF_CASE=${VERIF_CASE}
fi

for MODEL in $MODEL_LIST ; do
 
  model=`echo $MODEL | tr '[A-Z]' '[a-z]'`

  #********************************
  # Get sub-string of $EVSIN
  #*******************************
  archive=$output_base_dir
  prefix=${EVSIN%%${MODELNAME}*}
  index=${#prefix}
  echo $index
  COM_IN=${EVSIN:0:$index}
  echo $COM_IN

  model_stat_dir=${COM_IN}${model}.${day}

  gens_archive_yyyymmdd=${archive}/${model}
  mkdir -p $gens_archive_yyyymmdd

  cd ${gens_archive_yyyymmdd}

  stat=${model_stat_dir}/evs.stats.${model}.atmos.${VRF_CASE}.v${day}.stat

  if [ -s ${stat} ] ; then
    ln -sf ${stat} ${MODEL}_${day}.stat
  fi

  if [ $MODEL = ECME ] ; then
    if [ -s ${MODEL}_${day}.stat ]; then
      #**********************************************************
      # Change string L0 to Z10 in ECME stat files to make it as
      # same as in the GEFS and CMCE stat files
      #*********************************************************
      sed -e 's!-1   L0!-1   Z10!g'  ${MODEL}_${day}.stat > a
      mv a ${MODEL}_${day}.stat
    fi
  fi 

done
  


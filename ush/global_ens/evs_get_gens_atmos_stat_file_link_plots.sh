#!/bin/ksh

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

  archive=$output_base_dir
  prefix=${COMIN%%${MODELNAME}*}
  index=${#prefix}
  echo $index
  COM_IN=${COMIN:0:$index}
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
    sed -e 's!-1   L0!-1   Z10!g'  ${MODEL}_${day}.stat > a
    mv a ${MODEL}_${day}.stat 
  fi 

done
  


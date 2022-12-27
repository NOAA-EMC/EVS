#!/bin/ksh

set -x 

day=$1
MODEL_LIST=$2

for MODEL in $MODEL_LIST ; do
 
  model=`echo $MODEL | tr '[A-Z]' '[a-z]'`

  archive=$output_base_dir
  prefix=${COMIN%%gefs*}
  index=${#prefix}
  echo $index
  COM_IN=${COMIN:0:$index}
  echo $COM_IN

  model_stat_dir=${COM_IN}${model}.${day}

  gens_archive_yyyymmdd=${archive}/${model}
  mkdir -p $gens_archive_yyyymmdd

  cd ${gens_archive_yyyymmdd}

  if [ -s ${model_stat_dir}/evs.stats.${model}_atmos_${VERIF_CASE}_v${day}.stat ] ; then
    ln -sf ${model_stat_dir}/evs.stats.${model}_atmos_${VERIF_CASE}_v${day}.stat ${MODEL}_${day}.stat
  fi

  if [ $MODEL = ECME ] ; then
    sed -e 's!-1   L0!-1   Z10!g'  ${MODEL}_${day}.stat > a
    mv a ${MODEL}_${day}.stat 
  fi 

done
  


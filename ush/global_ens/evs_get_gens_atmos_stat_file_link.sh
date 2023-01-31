#!/bin/ksh

set -x 

day=$1
MODEL=GEFS

for MODEL in GEFS ; do
 
  model=`echo $MODEL | tr '[A-Z]' '[a-z]'`

  archive=$output_base_dir
# COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/com/$NET/$evs_ver/stats/$COMPONENT/$MODELNAME.$day
# COMIN=/lfs/h2/emc/vpppg/noscrub/binbin.zhou/com/evs/v1.0/stats/global_ens/gefs.$day
  prefix=${COMIN%%gefs*}
  index=${#prefix}
  echo $index
  COM_IN=${COMIN:0:$index}
  echo $COM_IN

  model_stat_dir=${COM_IN}${model}.${day}

  gens_archive_yyyymmdd=${archive}/${model}
  mkdir -p $gens_archive_yyyymmdd

  cd ${gens_archive_yyyymmdd}

  if [ -s ${model_stat_dir}/evs.stats.${model}_atmos_grid2grid_v${day}.stat ] ; then
    ln -sf ${model_stat_dir}/evs.stats.${model}_atmos_grid2grid_v${day}.stat ${MODEL}_${day}.stat
  fi

done
  


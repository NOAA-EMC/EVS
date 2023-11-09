#!/bin/ksh
#**************************************************************************************
# Purpose: To build virtually link for past 90 days of sref stat data files required
#          by sref plot jobs
# Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#**************************************************************************************
set -x 

day=$1
MODEL_LIST=$2
VRF_CASE=${VERIF_CASE}

archive=$output_base_dir

COM_IN=${EVSIN}/stats/


for MODEL in $MODEL_LIST ; do
 
  model=`echo $MODEL | tr '[A-Z]' '[a-z]'`

  model_archive=${archive}/${model}
  mkdir -p $model_archive

  cd $model_archive

  if [ $model = gefs ] ; then
    model_stat_dir=${COM_IN}/global_ens/${model}.${day}
    if [ $VRF_CASE = grid2obs ] ||  [ $VRF_CASE = cape ] || [ $VRF_CASE = cloud ] || [ $VRF_CASE = td2m ] ; then
       if [ -s  ${model_stat_dir}/evs.stats.${model}.atmos.grid2obs.v${day}.stat ] ; then
         ln -sf ${model_stat_dir}/evs.stats.${model}.atmos.grid2obs.v${day}.stat ${MODEL}_${day}.stat
       fi
    else 
       if [ -s ${model_stat_dir}/evs.stats.${model}.atmos.${VRF_CASE}.v${day}.stat ] ; then
        ln -sf ${model_stat_dir}/evs.stats.${model}.atmos.${VRF_CASE}.v${day}.stat ${MODEL}_${day}.stat
       fi
    fi 
  elif [ $model = sref ] ; then
    model_stat_dir=${COM_IN}/mesoscale/${model}.${day}
    if [ $VRF_CASE = cnv ] || [ $VRF_CASE = cape ] || [ $VRF_CASE = cloud ] || [ $VRF_CASE = td2m ] ; then
	if [ -s ${model_stat_dir}/evs.stats.${model}.grid2obs.v${day}.stat ] ;then 
         ln -sf ${model_stat_dir}/evs.stats.${model}.grid2obs.v${day}.stat ${MODEL}_${day}.stat
	fi 
    else
        if [ -s ${model_stat_dir}/evs.stats.${model}.${VRF_CASE}.v${day}.stat ] ; then	    
         ln -sf ${model_stat_dir}/evs.stats.${model}.${VRF_CASE}.v${day}.stat ${MODEL}_${day}.stat
	fi
    fi
  else
     err_exit "Wrong model"
  fi 

done
  


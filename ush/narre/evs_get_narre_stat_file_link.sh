#!/bin/ksh
# **************************************************************************************
# Purpose: To build virtually link past 31/90 days of narre stat data files required 
#          by narre plot jobs
# Last update: 10/27/2023, by Binbin Zhou Lynker@EMC/NCEP
#**************************************************************************************
set -x 

day=$1
MODEL=NARRE_MEAN
model=narre_mean

archive=$output_base_dir

prefix=${COMIN%%$VDATE*}
index=${#prefix}
echo $index
COM_IN=${COMIN:0:$index}
echo $COM_IN

narre_stat=${COM_IN}${day}

yyyymm=${day:0:6} 

narre_archive_yyyymmdd=${archive}/${model}
#narre_archive_yyyymmdd=${archive}/${model}/${MODEL}_${day}
#narre_archive_yyyymm=${archive}/${VERIF_CASE}/$MODEL/$yyyymm
mkdir -p $narre_archive_yyyymmdd

cd ${narre_archive_yyyymmdd}

if [ -s ${narre_stat}/evs.stats.narremean.mean.${VERIF_CASE}.v${day}.stat ] ; then
  ln -sf ${narre_stat}/evs.stats.narremean.mean.${VERIF_CASE}.v${day}.stat ${MODEL}_${day}.stat
fi

  


#!/bin/ksh

set -x 

day=$1
verify=grid2obs
MODEL=NARRE_MEAN
archive=$output_base_dir
narre_stat=${COM_OUT}/stats/narre

yyyymm=${day:0:6} 

narre_archive_yyyymm=${archive}/grid2obs/$MODEL/$yyyymm
mkdir -p $narre_archive_yyyymm

cd ${narre_archive_yyyymm}

ln -sf $GATHER_STAT/narre.${day}/${MODEL}_${verify}_${day}.stat ${MODEL}_${day}.stat

  


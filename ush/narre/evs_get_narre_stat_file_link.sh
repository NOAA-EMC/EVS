#!/bin/ksh

set -x 

day=$1
MODEL=NARRE_MEAN
archive=$output_base_dir

prefix=${COMIN%%$VDATE*}
index=${#prefix}
echo $index
COM_IN=${COMIN:0:$index}
echo $COM_IN

narre_stat=${COM_IN}${day}

yyyymm=${day:0:6} 

narre_archive_yyyymm=${archive}/${VERIF_CASE}/$MODEL/$yyyymm
mkdir -p $narre_archive_yyyymm

cd ${narre_archive_yyyymm}

ln -sf ${narre_stat}/${MODEL}_${VERIF_CASE}_${day}.stat ${MODEL}_${day}.stat

  


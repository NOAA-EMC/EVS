#!/bin/sh
set -x

source ../versions/build.ver
module reset

module load PrgEnv-intel/${PrgEnvintel_ver}
module load intel/${intel_ver}
module load bacio/${bacio_ver}
module load w3nco/${w3nco_ver}
module load w3emc/${w3emc_ver}
module load ip/${ip_ver}
module load sp/${sp_ver}
module load g2/${g2_ver}
module load jasper/${jasper_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module list

w3nco_lib4_name=$(echo ${W3NCO_LIB4##*/})
export W3NCOLIB=$(echo $w3nco_lib4_name | sed -e "s/lib//g" | sed -e "s/\.a//g")
export LIBDIRW3NCO=$(echo $W3NCO_LIB4 | sed -e "s/\/${w3nco_lib4_name}//g")
w3emc_lib4_name=$(echo ${W3EMC_LIB4##*/})
export W3EMCLIB=$(echo $w3emc_lib4_name | sed -e "s/lib//g" | sed -e "s/\.a//g")
export LIBDIRW3EMC=$(echo $W3EMC_LIB4 | sed -e "s/\/${w3emc_lib4_name}//g")
bacio_lib4_name=$(echo ${BACIO_LIB4##*/})
export BACIOLIB=$(echo $bacio_lib4_name | sed -e "s/lib//g" | sed -e "s/\.a//g")
export LIBDIRBACIO=$(echo $BACIO_LIB4 | sed -e "s/\/${bacio_lib4_name}//g")

BASE=`pwd`

if [ -d $BASE/../exec ]; then
    ls $BASE/../exec/*
    #rm -f $BASE/../exec/*
else
    mkdir $BASE/../exec
fi

#-------------------
cd $BASE/ecm_gfs_look_alike_new.fd 
make
make install
#-------------------

#-------------------
cd $BASE/jma_merge.fd
make
make install
#-------------------

#-------------------
cd $BASE/ukm_hires_merge.fd
make
make install
#-------------------

#-------------------
cd $BASE/pcpconform.fd
make
make install
#-------------------

exit

#!/bin/sh
set -x

# Location of PWD and package source directory.
readonly pkg_root=$(cd "$(dirname "$(readlink -f -n "${BASH_SOURCE[0]}" )" )/.." && pwd -P)

# User options
export BUILD_CLEAN=${BUILD_CLEAN-:YES}

source $pkg_root/versions/build.ver
module reset
module load PrgEnv-intel/${PrgEnvintel_ver}
module load intel/${intel_ver}
module load craype/${craype_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
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

if [ ! -d $pkg_root/exec ]; then
    echo "Creating $pkg_root/exec"
    mkdir $pkg_root/exec
else
    if [ $BUILD_CLEAN = YES ]; then
        echo "Doing clean build...Creating $pkg_root/exec"
        mkdir $pkg_root/exec
    fi
fi

cd $pkg_root/sorc/ecm_gfs_look_alike_new.fd 
make
make install

cd $pkg_root/sorc/jma_merge.fd
make
make install

cd $pkg_root/sorc/ukm_hires_merge.fd
make
make install

cd $pkg_root/sorc/pcpconform.fd
make
make install

cd $pkg_root/sorc/evs_sref_adjust_precip24_time.fd
make precip

cd $pkg_root/sorc/evs_global_ens_adjust_CMCE_NAEFS.fd
make cmce

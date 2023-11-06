#!/bin/bash
set -eux

# Location of PWD and package source directory.
readonly pkg_root=$(cd "$(dirname "$(readlink -f -n "${BASH_SOURCE[0]}" )" )/.." && pwd -P)

# User options
BUILD_DEBUG=${BUILD_DEBUG:-NO}
BUILD_CLEAN=${BUILD_CLEAN:-YES}
BUILD_VERBOSE=${BUILD_VERBOSE:-YES}
export EXECevs=${EXECevs:-${pkg_root}/exec}

# Load modules
source ${pkg_root}/versions/build.ver
set +x
module reset
module load PrgEnv-intel/${PrgEnvintel_ver}
module load intel/${intel_ver}
module load craype/${craype_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load bacio/${bacio_ver}
module load w3emc/${w3emc_ver}
module load ip/${ip_ver}
module load sp/${sp_ver}
module load g2/${g2_ver}
module load jasper/${jasper_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module list
set -x
w3emc_lib4_name=$(echo ${W3EMC_LIB4##*/})
export W3EMCLIB=$(echo $w3emc_lib4_name | sed -e "s/lib//g" | sed -e "s/\.a//g")
export LIBDIRW3EMC=$(echo $W3EMC_LIB4 | sed -e "s/\/${w3emc_lib4_name}//g")
bacio_lib4_name=$(echo ${BACIO_LIB4##*/})
export BACIOLIB=$(echo $bacio_lib4_name | sed -e "s/lib//g" | sed -e "s/\.a//g")
export LIBDIRBACIO=$(echo $BACIO_LIB4 | sed -e "s/\/${bacio_lib4_name}//g")

# Define compiler and default compiler flags
export FC=ftn
export FFLAGS="-g -traceback"

# Make EXECevs
if [ ! -d ${EXECevs} ]; then
    echo "Creating ${EXECevs}"
    mkdir -p ${EXECevs}
else
    if [ ${BUILD_CLEAN} = "YES" ]; then
        echo "Doing clean build for $EXECevs"
        rm -rf ${pkg_root}/exec
        mkdir -p ${pkg_root}/exec
    else
        echo "Not doing clean build...${EXECevs} exists"
        exit
    fi
fi

# Build
for code in ecm_gfs_look_alike_new jma_merge ukm_hires_merge pcpconform sref_precip evs_g2g_adjustCMC; do

  cd "${pkg_root}/sorc/${code}.fd"
  if [ ${BUILD_CLEAN} = "YES" ]; then
      make VERBOSE=${BUILD_VERBOSE} clean
  fi
  if [ ${BUILD_DEBUG} = "YES" ]; then
      make VERBOSE=${BUILD_VERBOSE} debug
  else
      make VERBOSE=${BUILD_VERBOSE}
  fi
  make VERBOSE=${BUILD_VERBOSE} install

done

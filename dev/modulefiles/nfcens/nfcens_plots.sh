#!/bin/bash
# modulefile for EVS nfcens component, plots step

set -x

module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
export HPC_OPT=/apps/ops/para/libs
module use /apps/dev/modulefiles
module load PrgEnv-intel/${PrgEnvintel_ver}
module load intel/${intel_ver}
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load prod_util/${prod_util_ver}
module load libjpeg/${libjpeg_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load cray-pals/${craypals_ver}
module load cfp/${cfp_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}

export SIPHONROOT=${UTILROOT}/fakedbn
export DBNROOT=$SIPHONROOT

module list
set -x

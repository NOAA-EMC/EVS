#!/bin/bash

set +x

module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}/
export HPC_OPT=/apps/ops/para/libs
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load netcdf/${netcdf_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}

module load libjpeg/$libjpeg_ver
module load grib_util/$grib_util_ver
module load prod_util/${produtil_ver}
module load prod_envir/${prodenvir_ver}
module load libfabric/${libfabric_ver}
module load imagemagick/${imagemagick_ver}

module list

set -x

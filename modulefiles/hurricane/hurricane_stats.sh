#!/bin/bash

export HPC_OPT=/apps/ops/prod/libs
module use /apps/ops/prod/libs/modulefiles/compiler/intel/19.1.3.304/
module load intel/${intel_ver}
module load gsl/${gsl_ver}
module load python/${python_ver}
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

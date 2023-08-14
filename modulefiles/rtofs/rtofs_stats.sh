#!/bin/bash
# modulefile for EVS rtofs component

set +x

module use /apps/prod/lmodules/intel/${intel_ver}
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load netcdf/${netcdf_ver}
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}
module load rsync/${rsync_ver}
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}

module list
set -x

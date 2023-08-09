#!/bin/bash
# modulefile for EVS subseasonal component

set +x

module use /apps/prod/lmodules/intel/${intel_ver}
module load ve/evs/${ve_evs_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load wgrib2/${wgrib2_ver}
module load gsl/${gsl_ver}
module load prod_util/${produtil_ver}
module load prod_envir/${prodenvir_ver}
module load imagemagick/${imagemagick_ver}
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}

module list
set -x

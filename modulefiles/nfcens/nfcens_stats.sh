#!/bin/bash
# modulefile for EVS nfcens component, stats step

set +x

export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load prod_envir/${prod_envir_ver}
module load prod_util/${prod_util_ver}
module load libjpeg/${libjpeg_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load cray-pals/${craypals_ver}
module load cfp/${cfp_ver}

module list
set -x

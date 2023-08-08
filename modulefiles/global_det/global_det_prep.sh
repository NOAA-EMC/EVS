#!/bin/bash
# modulefile for EVS global_det component, prep step

set +x

module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
export HPC_OPT=/apps/ops/para/libs
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load prod_util/${prod_util_ver}
module load libjpeg/${libjpeg_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load cdo/${cdo_ver}
module load udunits/${udunits_ver}
module load nco/${nco_ver}

module list

set -x

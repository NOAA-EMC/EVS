#!/bin/bash
# modulefile for EVS global_det component, prep step

set -x

#module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
#export HPC_OPT=/apps/ops/para/libs
#module use /apps/dev/modulefiles
module use /ncrc/proj/epic/spack-stack/c6/spack-stack-1.6.0/envs/fms-2024.01/install/modulefiles/Core
module load Core/24.11
module load PrgEnv-intel/${PrgEnvintel_ver}
module load stack-intel/${intel_ver}
module load stack-cray-mpich/8.1.29
#module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load netcdf-c/${netcdf_ver}
#module load cray-pals/${craypals_ver}
module load prod_util/${prod_util_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module load jasper/${jasper_ver}
module load udunits/${udunits_ver}
module load grib-util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load cdo/${cdo_ver}
module load udunits/${udunits_ver}
module load nco/${nco_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load bufr/${bufr_ver}

module list

set -x

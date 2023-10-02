#!/bin/bash
# modulefile for EVS wafs stat
set -x

module load PrgEnv-intel/${PrgEnvintel_ver}
module load intel/${intel_ver}

module load ve/evs/$ve_evs_ver
module load craype/$craype_ver
module load cray-pals/$craypals_ver
module load libjpeg/$libjpeg_ver
module load prod_util/$prod_util_ver
module load wgrib2/$wgrib2_ver
module load libpng/$libpng_ver
module load zlib/$zlib_ver
module load jasper/$jasper_ver
module load cfp/$cfp_ver
module load gsl/$gsl_ver
module load met/$met_ver
module load metplus/$metplus_ver

module list

#!/bin/bash

set +x

module use /apps/prod/lmodules/intel/${intel_ver}
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load netcdf/${netcdf_ver}
module load libjpeg/$libjpeg_ver
module load grib_util/$grib_util_ver
module load prod_util/${produtil_ver}
module load libfabric/${libfabric_ver}
module load imagemagick/${imagemagick_ver}
module load geos/${geos_ver}
module load proj/${proj_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}

module list

set -x


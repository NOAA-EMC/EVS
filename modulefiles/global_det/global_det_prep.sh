#!/bin/bash
# modulefile for EVS global_det component, prep step

set -x

module load PrgEnv-intel/${PrgEnvintel_ver}
module load intel/${intel_ver}
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

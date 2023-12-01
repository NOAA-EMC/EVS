#!/bin/bash
# modulefile for EVS rtofs component

set -x

module load PrgEnv-intel/${PrgEnvintel_ver}
module load intel/${intel_ver}
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load netcdf/${netcdf_ver}
module load prod_util/${prod_util_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}

export SIPHONROOT=${UTILROOT}/fakedbn
export DBNROOT=$SIPHONROOT

module list
set -x

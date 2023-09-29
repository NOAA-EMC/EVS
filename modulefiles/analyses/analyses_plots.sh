#!/bin/bash
# modulefile for EVS analyses plot component

set -x

module load PrgEnv-intel/${PrgEnvintel_ver}
module load intel/${intel_ver)
module load ve/evs/${ve_evs_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load wgrib2/${wgrib2_ver}
module load gsl/${gsl_ver}
module load prod_util/${produtil_ver}
module load imagemagick/${imagemagick_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}

module list
set -x

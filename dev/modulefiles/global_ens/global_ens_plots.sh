set -x
module load PrgEnv-intel/${PrgEnvintel_ver}
module load intel/${intel_ver}
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load prod_util/${prod_util_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module load jasper/${jasper_ver}
module load udunits/${udunits_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load cray-pals/${craypals_ver}
module load cfp/${cfp_ver}
module load imagemagick/${imagemagick_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}

export SIPHONROOT=${UTILROOT}/fakedbn
export DBNROOT=$SIPHONROOT

module list

set -x


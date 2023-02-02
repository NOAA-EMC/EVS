source $HOMEevs/versions/run.ver

source /usr/share/lmod/lmod/init/sh
module reset
export HPC_OPT=/apps/ops/para/libs
export MET_bin_exec="bin"
module load cray-pals/${craypals_ver}
module load PrgEnv-intel/${PrgEnv_intel_ver}
module load craype/${craype_ver}
module load intel/${intel_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load cfp/${cfp_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module load jasper/${jasper_ver}
module load udunits/${udunits_ver}
module load gsl/${gsl_ver}
module load hdf5/${hdf5_ver}
module load python/${python_ver}
module load netcdf/${netcdf_ver}
module load nco/${nco_ver}
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}
module load cdo/${cdo_ver}
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
export MET_PLUS_PATH="/apps/ops/para/libs/intel/19.1.3.304/metplus/${metplus_ver}"
export MET_PATH="/apps/ops/para/libs/intel/19.1.3.304/met/${met_ver}"
export MET_CONFIG="${MET_PLUS_PATH}/parm/met_config"
export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH

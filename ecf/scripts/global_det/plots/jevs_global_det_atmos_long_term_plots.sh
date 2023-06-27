#PBS -N jevs_global_det_atmos_long_term_plots_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l select=1:ncpus=1
#PBS -l debug=true
#PBS -V

set -x

export model=evs

############################################################
# For dev testing
############################################################
cd $PBS_O_WORKDIR
module reset
export HOMEevs=$(eval "cd ../../../;pwd")
versionfile=$HOMEevs/versions/run.ver
. $versionfile
export evs_ver=$evs_ver
export envir=dev
export RUN_ENVIR=nco
export SENDCOM=YES
export KEEPDATA=NO
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_global_det_atmos_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_global_det_atmos_long_term_plots}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

############################################################
# Load modules
############################################################
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
export HPC_OPT=/apps/ops/para/libs
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load netcdf/${netcdf_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load cray-pals/${craypals_ver}
module load prod_envir/${prod_envir_ver}
module load prod_util/${prod_util_ver}
module load cfp/${cfp_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module load jasper/${jasper_ver}
module load udunits/${udunits_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
export MET_bin_exec=bin
module list

# Set machine
export machine=WCOSS2

# Set cycle
export cyc=00

# Set verification information
export NET=evs
export STEP=plots
export COMPONENT=global_det
export RUN=long_term

# Set archive
export PDY=$(date '+%Y%m%d')
export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER/evs_global_det_atmos_test/$envir/com
export COMIN=$COMROOT/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/evs_global_det_atmos_test/$envir/com/$NET/$evs_ver/$STEP/$COMPONENT/$RUN
export COMINdailystats=$COMIN/stats/$COMPONENT
export COMINmonthlystats=$COMIN/stats/$COMPONENT/$RUN/monthly_means
export COMINyearlystats=$COMIN/stats/$COMPONENT/$RUN/annual_means

# Set year and month
export VDATEYYYY=$(date -d "1 month ago" '+%Y')
export VDATEmm=$(date -d "1 month ago" '+%m')

# CALL executable job script here
$HOMEevs/jobs/global_det/plots/JEVS_GLOBAL_DET_ATMOS_LONG_TERM_PLOTS

######################################################################
# Purpose: This does the plotting work for the global deterministic
#          atmospheric long term stats
######################################################################

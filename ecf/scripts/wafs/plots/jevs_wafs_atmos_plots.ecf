#PBS -N jevs_wafs_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=40:mem=200GB
#PBS -l debug=true
#PBS -V

export OMP_NUM_THREADS=1

export HOMEevs=${HOMEevs:-/lfs/h2/emc/vpppg/noscrub/$USER/EVS}
source $HOMEevs/versions/run.ver

############################################################
# Load modules
############################################################
module reset

module use /apps/ops/para/libs/modulefiles/compiler/intel/19.1.3.304
export HPC_OPT=/apps/ops/para/libs
module use /apps/dev/modulefiles
module load ve/evs/$ve_evs_ver
module load craype/$craype_ver
module load cray-pals/$craypals_ver
module load libjpeg/$libjpeg_ver
module load prod_util/$prod_util_ver
module load prod_envir/$prod_envir_ver
module load wgrib2/$wgrib2_ver
module load libpng/$libpng_ver
module load zlib/$zlib_ver
module load jasper/$jasper_ver
module load cfp/$cfp_ver

module load gsl/$gsl_ver
module load met/$met_ver
module load metplus/$metplus_ver

set -xa
module list

############################################################
# environment variables set
############################################################
export envir=dev

export NET=evs
export STEP=plots
export COMPONENT=wafs
export RUN=atmos
export VERIF_CASE=grid2grid

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/evs/$evs_ver

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export USH_DIR=$HOMEevs/ush/$COMPONENT
export DAYS_LIST="90 31"

############################################################
# CALL executable job script here
############################################################
export KEEPDATA=YES

export pid=${pid:-$$}
export DATA=/lfs/h2/emc/ptmp/$USER/evs/working/${STEP}.$pid

$HOMEevs/jobs/wafs/plots/JEVS_WAFS_ATMOS_PLOTS

############################################################
## Purpose: This job generates the grid2grid statistics stat
##          files for GFS WAFS
############################################################
#

exit


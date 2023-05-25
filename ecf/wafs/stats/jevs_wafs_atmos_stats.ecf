#PBS -N jevs_wafs_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=7:mem=10GB
#PBS -l debug=true
#PBS -V

##PBS -q debug
##PBS -A GFS-DEV
##PBS -q dev
##PBS -A VERF-DEV

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
export MET_bin_exec=bin

set -xa
module list

############################################################
# environment variables set
############################################################
export envir=prod

export NET=evs
export STEP=stats
export COMPONENT=wafs
export RUN=atmos
export VERIF_CASE=grid2grid

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/evs/$evs_ver

############################################################
# set up for email alerts of missing data
############################################################
export pid=${PBS_JOBID:-$$}
export job=${PBS_JOBNAME:-jevs_aviation_stats}
export jobid=$job.$pid
export maillist=${maillist:-'geoffrey.manikin@noaa.gov,yali.mao@noaa.gov'}

############################################################
# CALL executable job script here
############################################################
export DATA=/lfs/h2/emc/ptmp/$USER/evs/working/${STEP}.$pid

export KEEPDATA=YES

$HOMEevs/jobs/wafs/stats/JEVS_WAFS_ATMOS_STATS

############################################################
## Purpose: This job generates the grid2grid statistics stat
##          files for GFS WAFS
############################################################
#
exit

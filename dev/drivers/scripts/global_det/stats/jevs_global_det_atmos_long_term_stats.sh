#PBS -N jevs_global_det_atmos_long_term_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=05:00:00
#PBS -l select=1:ncpus=1
#PBS -l debug=true
#PBS -V

set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export SENDCOM=YES
export KEEPDATA=YES
export job=${PBS_JOBNAME:-jevs_global_det_atmos_long_term_stats}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export cyc=00

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/global_det/global_det_stats.sh

export machine=WCOSS2

export evs_run_mode=production
export envir=dev
export NET=evs
export STEP=stats
export COMPONENT=global_det
export RUN=long_term

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver
export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER

export VDATEYYYY=$(date -d "1 month ago" '+%Y')
export VDATEmm=$(date -d "1 month ago" '+%m')

# CALL executable job script here
$HOMEevs/jobs/JEVS_GLOBAL_DET_ATMOS_LONG_TERM_STATS

######################################################################
# Purpose: This does the statistics work for the global deterministic
#          atmospheric long term stats
######################################################################

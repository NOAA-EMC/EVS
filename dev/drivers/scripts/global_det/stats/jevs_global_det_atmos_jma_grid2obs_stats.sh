#PBS -N jevs_global_det_atmos_jma_grid2obs_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter,select=1:ncpus=14:ompthreads=1:mem=25GB
#PBS -l debug=true
#PBS -V

set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export SENDCOM=YES
export SENDMAIL=YES
export KEEPDATA=NO
export job=${PBS_JOBNAME:-jevs_global_det_atmos_jma_grid2obs_stats}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export cyc=00

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/global_det/global_det_stats.sh

export machine=WCOSS2
export USE_CFP=YES
export nproc=14

export maillist='alicia.bentley@noaa.gov,mallory.row@noaa.gov'

export envir=prod
export NET=evs
export STEP=stats
export COMPONENT=global_det
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=jma

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=$COMROOT/$NET/$evs_ver
export COMOUT=$COMROOT/$NET/$evs_ver/$STEP/$COMPONENT

export config=$HOMEevs/parm/evs_config/global_det/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${MODELNAME}

# CALL executable job script here
$HOMEevs/jobs/JEVS_GLOBAL_DET_STATS

######################################################################
# Purpose: This does the statistics work for the global deterministic
#          atmospheric grid-to-observations component for JMA
######################################################################

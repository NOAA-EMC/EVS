#PBS -N jevs_global_ens_gefs_headline_grid2grid_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter,select=1:ncpus=2:mem=100GB
#PBS -l debug=true


export OMP_NUM_THREADS=1
#Total 18 cpu cores: assigned to 1 nodes, 18 cores for each node 
#Total 9 processes 4(gefs/upper) + 1 (gefs/apcp24h) + 4 (gefs/apcp06h)
#
set -x

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver

export NET=evs
export RUN=headline
export STEP=stats
export COMPONENT=global_ens
export VERIF_CASE=grid2grid
export MODELNAME=gefs


module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh




export KEEPDATA=NO

export cyc=00
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_headline_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export run_mpi=no

export maillist='alicia.bentley@noaa.gov,steven.simon@noaa.gov'

${HOMEevs}/jobs/global_ens/stats/JEVS_GLOBAL_ENS_STATS

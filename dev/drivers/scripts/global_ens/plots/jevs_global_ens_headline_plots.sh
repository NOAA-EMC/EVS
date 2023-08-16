#PBS -N jevs_global_ens_headline_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter,select=1:ncpus=2:mem=500GB
#PBS -l debug=true


set -x
export OMP_NUM_THREADS=1
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver

export NET=evs
export RUN=headline
export STEP=plots
export COMPONENT=global_ens
export VERIF_CASE=grid2grid
export MODELNAME=gefs


source $HOMEevs/modulefiles/${evs_ver}

module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh





export KEEPDATA=YES

#This var is only for testing, if not set, then run operational 


export cyc=00
export run_mpi=no
export run_entire_year=no

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATA=/lfs/h2/emc/stmp/${USER}/evs/tmpnwprd
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

${HOMEevs}/jobs/global_ens/plots/JEVS_GLOBAL_ENS_PLOTS



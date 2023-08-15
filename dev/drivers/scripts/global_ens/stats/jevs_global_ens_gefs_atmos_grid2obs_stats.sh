#PBS -N jevs_global_ens_gefs_atmos_grid2obs_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A EVS-DEV
#PBS -l walltime=01:30:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=88:mem=500GB
#PBS -l debug=true


#Total 44  processes = 4x4 profile, 4x4 sfc, 3x4 cloud

set -x

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export NET=evs
export RUN=atmos
export STEP=stats
export COMPONENT=global_ens
export VERIF_CASE=grid2obs
export MODELNAME=gefs


module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh




export KEEPDATA=YES


export cyc=00
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATA=/lfs/h2/emc/stmp/${USER}/evs/tmpnwprd
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export maillist='geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'

${HOMEevs}/jobs/global_ens/stats/JEVS_GLOBAL_ENS_STATS

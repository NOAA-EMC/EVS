#PBS -N jevs_global_ens_ecme_atmos_precip_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter,select=1:ncpus=2:mem=100GB
#PBS -l debug=true

export OMP_NUM_THREADS=1
#Total 18 cpu cores: assigned to 1 nodes, 18 cores for each node 
#Total 9 processes 4(ecme/upper) + 1 (ecme/apcp24h) + 4 (ecme/apcp06h)
#
set -x

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver

export envir=prod
export NET=evs
export RUN=atmos
export STEP=stats
export COMPONENT=global_ens
export VERIF_CASE=precip
export MODELNAME=ecme

module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export evs_ver=v1.0.0
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export KEEPDATA=YES

export vhr=00
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}
export SENDMAIL=YES
export maillist='alicia.bentley@noaa.gov,steven.simon@noaa.gov'

${HOMEevs}/jobs/JEVS_GLOBAL_ENS_STATS

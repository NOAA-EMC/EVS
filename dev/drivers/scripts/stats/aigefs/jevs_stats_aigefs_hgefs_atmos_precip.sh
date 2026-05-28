#PBS -N jevs_stats_aigefs_hgefs_atmos_precip
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter,select=1:ncpus=5:mem=25GB:prepost=true
#PBS -l debug=true

set -x
export OMP_NUM_THREADS=1
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export envir=prod
export NET=evs
export STEP=stats
export COMPONENT=aigefs
export RUN=atmos
export MODELNAME=hgefs
export VERIF_CASE=precip

module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export vhr=00

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp

export job=${PBS_JOBNAME:-jevs_${STEP}_${COMPONENT}_${MODELNAME}_${RUN}_${VERIF_CASE}}
export jobid=$job.${PBS_JOBID:-$$}

export KEEPDATA=NO
export SENDMAIL=NO
export MAILTO='alicia.bentley@noaa.gov,lichuan.chen@noaa.gov'

${HOMEevs}/jobs/JEVS_STATS_AIGEFS

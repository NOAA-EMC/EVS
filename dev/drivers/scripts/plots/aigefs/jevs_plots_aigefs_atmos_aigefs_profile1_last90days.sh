#PBS -N jevs_plots_aigefs_atmos_aigefs_profile1_last90days
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:25:00
#PBS -l place=vscatter:exclhost,select=10:ncpus=33:mpiprocs=33:mem=170GB:prepost=true
#PBS -l debug=true

set -x
export OMP_NUM_THREADS=2
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export envir=prod
export NET=evs
export STEP=plots
export COMPONENT=aigefs
export RUN=atmos
export MODELNAME=aigefs
export VERIF_CASE=profile1

module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export vhr=00
export past_days=90
export valid_time=both

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp

export job=${PBS_JOBNAME:-jevs_${STEP}_${MODELNAME}_${VERIF_CASE}}
export jobid=$job.${PBS_JOBID:-$$}

export KEEPDATA=NO
export SENDDBN=NO
export SENDMAIL=NO

${HOMEevs}/jobs/JEVS_PLOTS_AIGEFS

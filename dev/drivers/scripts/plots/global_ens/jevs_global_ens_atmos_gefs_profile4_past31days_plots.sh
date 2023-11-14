#PBS -N jevs_global_ens_atmos_gefs_profile4_past31days_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A EVS-DEV
#PBS -l walltime=00:20:00
#PBS -l place=vscatter,select=5:ncpus=32:mpiprocs=32:mem=75GB
#PBS -l debug=true

set -x

export OMP_NUM_THREADS=1

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver

export NET=evs
export STEP=plots
export COMPONENT=global_ens
export RUN=atmos
export VERIF_CASE=profile4
export MODELNAME=gefs

module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export evs_ver=v1.0.0
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export envir=prod

export KEEPDATA=YES
export SENDDBN=YES

export vhr=00
export past_days=31

export met_v=${met_ver:0:4}
export valid_time=both

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export SENDMAIL=YES
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

${HOMEevs}/jobs/JEVS_GLOBAL_ENS_PLOTS

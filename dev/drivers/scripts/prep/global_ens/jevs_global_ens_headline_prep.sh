#PBS -N jevs_global_ens_headline_prep
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter,select=1:ncpus=1:mem=10GB
#PBS -l debug=true

set -x

export OMP_NUM_THREADS=1

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

export envir=prod
export NET=evs
export RUN=headline
export STEP=prep
export COMPONENT=global_ens
export VERIF_CASE=grid2grid
export MODELNAME=gefs

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export KEEPDATA=YES

export vhr=00
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export run_mpi=no

#export SENDMAIL=YES
export MAILTO='alicia.bentley@noaa.gov,lichuan.chen@noaa.gov'

if [ -z "$MAILTO" ]; then
   echo "MAILTO variable is not defined. Exiting without continuing."
else
  ${HOMEevs}/jobs/JEVS_GLOBAL_ENS_PREP
fi

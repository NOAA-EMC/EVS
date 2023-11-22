#PBS -N jevs_global_ens_naefs_atmos_prep
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter,select=1:ncpus=34:mem=50GB
#PBS -l debug=true

set -x

export OMP_NUM_THREADS=1

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

export envir=prod
export NET=evs
export RUN=atmos
export STEP=prep
export COMPONENT=global_ens
export VERIF_CASE=grid2grid
export MODELNAME=naefs

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export KEEPDATA=YES

export vhr=00
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export run_mpi=yes
export get_gefs_bc_apcp24h=yes
export get_model_bc=yes

#export SENDMAIL=YES
export MAILTO='alicia.bentley@noaa.gov,steven.simon@noaa.gov'

if [ -z "$MAILTO" ]; then
   echo "MAILTO variable is not defined. Exiting without continuing."
else
  ${HOMEevs}/jobs/JEVS_GLOBAL_ENS_PREP
fi

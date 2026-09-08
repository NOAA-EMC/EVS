#PBS -N jevs_prep_global_ens_atmos
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=06:00:00
#PBS -l place=vscatter:exclhost,select=2:ncpus=42:mem=200GB
#PBS -l debug=true

set -x
export OMP_NUM_THREADS=1
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export envir=prod
export NET=evs
export RUN=atmos
export STEP=prep
export COMPONENT=global_ens
export VERIF_CASE=grid2grid
export MODELNAME=gefs

module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export KEEPDATA=NO

#This var is only for testing, if not set, then run operational 

export vhr=00
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp

export job=${PBS_JOBNAME:-jevs_${STEP}_${MODELNAME}_${VERIF_CASE}}
export jobid=$job.${PBS_JOBID:-$$}

#export SENDMAIL=YES
source $HOMEevs/dev/drivers/set_MAILTO.sh

if [ -z "$MAILTO" ]; then
   echo "MAILTO variable is not defined. Exiting without continuing."
else
   ${HOMEevs}/jobs/JEVS_PREP_GLOBAL_ENS
fi

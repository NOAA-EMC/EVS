#PBS -N jevs_stats_cam_refs_snowfall
#PBS -j oe
#PBS -q dev
#PBS -S /bin/bash
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter,select=1:ncpus=21:mem=50GB
#PBS -l debug=true

set -x 

export OMP_NUM_THREADS=1

export NET=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export STEP=stats
export COMPONENT=cam
export RUN=atmos
export VERIF_CASE=precip
export MODELNAME=refs
export KEEPDATA=NO
export SENDMAIL=${SENDMAIL:-NO}

module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export vhr=${vhr:-00}

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
export envir=prod
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d/$STEP/$COMPONENT
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_${STEP}_${MODELNAME}_${VERIF_CASE}}
export jobid=$job.${PBS_JOBID:-$$}

export prepare=yes
export verif_precip=no
export verif_snowfall=yes
export gather=yes

source $HOMEevs/dev/drivers/set_MAILTO.sh

if [ -z "$MAILTO" ]; then

   echo "MAILTO variable is not defined. Exiting without continuing."

else
  ${HOMEevs}/jobs/JEVS_STATS_CAM
fi

